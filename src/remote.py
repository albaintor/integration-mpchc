"""
Remote entity functions.

:copyright: (c) 2025 Albaintor
:license: Mozilla Public License Version 2.0, see LICENSE for more details.
"""

import asyncio
import logging
from asyncio import shield
from typing import Any

from ucapi import EntityTypes, Remote, StatusCodes
from ucapi.media_player import States
from ucapi.remote import Attributes, Commands, Features
from ucapi.remote import States as RemoteStates

import client
from config import DeviceInstance, create_entity_id
from const import REMOTE_BUTTONS_MAPPING, MPCHCCommands  # TODO , REMOTE_UI_PAGES

_LOG = logging.getLogger(__name__)

REMOTE_STATE_MAPPING = {
    States.UNKNOWN: RemoteStates.OFF,
    States.UNAVAILABLE: RemoteStates.OFF,
    States.OFF: RemoteStates.OFF,
    States.ON: RemoteStates.ON,
    States.PLAYING: RemoteStates.ON,
    States.PAUSED: RemoteStates.ON,
}

COMMAND_TIMEOUT = 4.5


def get_int_param(param: str, params: dict[str, Any], default: int):
    """Parse integer parameter value from given parameter."""
    # TODO bug to be fixed on UC Core : some params are sent as (empty) strings by remote (hold == "")
    value = params.get(param, default)
    if isinstance(value, str) and len(value) > 0:
        return int(float(value))
    return default


class MPCHCRemote(Remote):
    """Representation of a MPCHC Remote entity."""

    # pylint: disable=R0801
    def __init__(self, config_device: DeviceInstance, device: client.MPCHCClient):
        """Initialize the class."""
        self._device = device
        _LOG.debug("MPCHCRemote init")
        entity_id = create_entity_id(config_device.id, EntityTypes.REMOTE)
        features = [Features.SEND_CMD, Features.ON_OFF]
        attributes = {
            Attributes.STATE: REMOTE_STATE_MAPPING.get(device.state),
        }
        super().__init__(
            entity_id,
            config_device.name,
            features,
            attributes,
            button_mapping=REMOTE_BUTTONS_MAPPING,
            # ui_pages=REMOTE_UI_PAGES,
        )

    async def command(self, cmd_id: str, params: dict[str, Any] | None = None) -> StatusCodes:
        """
        Media-player entity command handler.

        Called by the integration-API if a command is sent to a configured media-player entity.

        :param cmd_id: command
        :param params: optional command parameters
        :return: status code of the command request
        """
        _LOG.info("Got %s command request: %s %s", self.id, cmd_id, params)

        if self._device is None:
            _LOG.warning("No instance for entity: %s", self.id)
            return StatusCodes.SERVICE_UNAVAILABLE

        # Occurs when the user press a button after wake up from standby and
        # the driver reconnection is not triggered yet
        if not self._device.connected:
            await self._device.connect()

        res = StatusCodes.OK
        if cmd_id == Commands.OFF:
            res = await self._device.exit()
        elif cmd_id in [Commands.SEND_CMD, Commands.SEND_CMD_SEQUENCE]:
            # If the duration exceeds the remote timeout, keep it running and return immediately
            try:
                async with asyncio.timeout(COMMAND_TIMEOUT):
                    res = await shield(self.send_commands(cmd_id, params))
            except asyncio.TimeoutError:
                _LOG.info("[%s] Command request timeout, keep running: %s %s", self.id, cmd_id, params)
        else:
            return StatusCodes.NOT_IMPLEMENTED
        return res

    async def send_commands(self, cmd_id: str, params: dict[str, Any] | None = None) -> StatusCodes:
        """Handle custom command or commands sequence."""
        # hold = get_int_param("hold", params, 0)
        delay = get_int_param("delay", params, 0)
        repeat = get_int_param("repeat", params, 1)
        command = params.get("command", "")
        res: StatusCodes = StatusCodes.OK
        for _i in range(0, repeat):
            if cmd_id == Commands.SEND_CMD:
                if command in MPCHCCommands:
                    result: StatusCodes = await self._device.send_command(MPCHCCommands[command])
                else:
                    result = StatusCodes.NOT_IMPLEMENTED
                if result != StatusCodes.OK:
                    res = result
                if delay > 0:
                    await asyncio.sleep(delay / 1000)
            else:
                commands = params.get("sequence", [])
                for command in commands:
                    if command in MPCHCCommands:
                        result: StatusCodes = await self._device.send_command(MPCHCCommands[command])
                    else:
                        result = StatusCodes.NOT_IMPLEMENTED
                    if result != StatusCodes.OK:
                        res = result
                    if delay > 0:
                        await asyncio.sleep(delay / 1000)
        return res

    def filter_changed_attributes(self, update: dict[str, Any]) -> dict[str, Any]:
        """
        Filter the given attributes and return only the changed values.

        :param update: dictionary with attributes.
        :return: filtered entity attributes containing changed attributes only.
        """
        attributes = {}

        if Attributes.STATE in update:
            state = REMOTE_STATE_MAPPING.get(update[Attributes.STATE])
            attributes = self._key_update_helper(Attributes.STATE, state, attributes)
        if attributes:
            _LOG.debug("MPCHC remote update attributes %s -> %s", update, attributes)
        return attributes

    def _key_update_helper(self, key: str, value: str | None, attributes):
        if value is None:
            return attributes

        if key in self.attributes:
            if self.attributes[key] != value:
                attributes[key] = value
        else:
            attributes[key] = value

        return attributes
