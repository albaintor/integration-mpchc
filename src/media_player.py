"""
Media-player entity functions.

:copyright: (c) 2025 Albaintor
:license: Mozilla Public License Version 2.0, see LICENSE for more details.
"""

import logging
from typing import Any

from ucapi import EntityTypes, MediaPlayer, StatusCodes
from ucapi.media_player import (
    Commands,
    DeviceClasses,
    Features,
)

from client import MPCHCClient
from config import DeviceInstance, create_entity_id
from const import MPCHCCommands

_LOG = logging.getLogger(__name__)


class MPCHCMediaPlayer(MediaPlayer):
    """Representation of a MPCHC Media Player entity."""

    # pylint: disable=R0915,R0903
    def __init__(self, config_device: DeviceInstance, device: MPCHCClient):
        """Initialize the class."""
        self._device = device

        entity_id = create_entity_id(config_device.id, EntityTypes.MEDIA_PLAYER)
        features = [
            Features.ON_OFF,
            Features.VOLUME,
            Features.VOLUME_UP_DOWN,
            Features.MUTE_TOGGLE,
            Features.MEDIA_TITLE,
            Features.MEDIA_ARTIST,
            Features.MEDIA_TYPE,
            Features.PLAY_PAUSE,
            Features.DPAD,
            Features.SETTINGS,
            Features.STOP,
            Features.FAST_FORWARD,
            Features.REWIND,
            Features.MENU,
            Features.CHANNEL_SWITCHER,
            Features.MEDIA_POSITION,
            Features.MEDIA_DURATION,
            Features.PREVIOUS,
            Features.NEXT,
            Features.AUDIO_TRACK,
            Features.SUBTITLE,
            Features.HOME,
            Features.INFO,
            Features.CONTEXT_MENU,
            Features.SEEK,
        ]
        attributes = device.attributes

        super().__init__(
            entity_id,
            config_device.name,
            features,
            attributes,
            device_class=DeviceClasses.STREAMING_BOX,
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
            _LOG.warning("No device instance for entity: %s", self.id)
            return StatusCodes.SERVICE_UNAVAILABLE

        if cmd_id == Commands.VOLUME_UP:
            res = await self._device.volume_up()
        elif cmd_id == Commands.VOLUME_DOWN:
            res = await self._device.volume_down()
        elif cmd_id == Commands.VOLUME:
            res = await self._device.set_volume(params.get("volume", 0))
        elif cmd_id == Commands.MUTE_TOGGLE:
            res = await self._device.mute_volume()
        elif cmd_id == Commands.OFF:
            await self._device.exit()
            return StatusCodes.OK
        elif cmd_id == Commands.CHANNEL_UP:
            res = await self._device.next_track()
        elif cmd_id == Commands.CHANNEL_DOWN:
            res = await self._device.previous_track()
        elif cmd_id == Commands.PLAY_PAUSE:
            res = await self._device.play_pause()
        elif cmd_id == Commands.FAST_FORWARD:
            res = await self._device.send_command(MPCHCCommands.STEP_FORWARD_MEDIUM)
        elif cmd_id == Commands.REWIND:
            res = await self._device.send_command(MPCHCCommands.STEP_BACKWARD_MEDIUM)
        elif cmd_id == Commands.CURSOR_UP:
            res = await self._device.send_command(MPCHCCommands.CURSOR_UP)
        elif cmd_id == Commands.CURSOR_DOWN:
            res = await self._device.send_command(MPCHCCommands.CURSOR_DOWN)
        elif cmd_id == Commands.CURSOR_LEFT:
            res = await self._device.send_command(MPCHCCommands.CURSOR_LEFT)
        elif cmd_id == Commands.CURSOR_RIGHT:
            res = await self._device.send_command(MPCHCCommands.CURSOR_RIGHT)
        elif cmd_id == Commands.CURSOR_ENTER:
            res = await self._device.send_command(MPCHCCommands.CURSOR_CENTER)
        elif cmd_id == Commands.BACK:
            res = await self._device.send_command(MPCHCCommands.MENU_DVD_BACK)
        elif cmd_id == Commands.MENU:
            res = await self._device.send_command(MPCHCCommands.MENU_DVD_MAIN)
        elif cmd_id == Commands.CONTEXT_MENU:
            res = await self._device.send_command(MPCHCCommands.MENU_OPTIONS)
        elif cmd_id == Commands.INFO:
            res = await self._device.send_command(MPCHCCommands.SHOW_HEADER_MENUS)
        elif cmd_id == Commands.AUDIO_TRACK:
            res = await self._device.send_command(MPCHCCommands.AUDIO_TRACK_NEXT)
        elif cmd_id == Commands.SUBTITLE:
            res = await self._device.send_command(MPCHCCommands.SUBTITLES_NEXT)
        elif cmd_id == Commands.SETTINGS:
            res = await self._device.send_command(MPCHCCommands.OPEN_FILE)
        elif cmd_id == Commands.SEEK:
            position = params.get("media_position", 0)
            res = await self._device.seek(position)
        else:
            return StatusCodes.NOT_IMPLEMENTED
        return res
