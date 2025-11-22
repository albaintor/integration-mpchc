#!/usr/bin/env python
# coding: utf-8
"""
This module implements the MPC-HC TV communication of the Remote Two integration driver.

:copyright: (c) 2025 Albaintor
:license: Mozilla Public License Version 2.0, see LICENSE for more details.
"""
import asyncio
import datetime
import logging
import re
import time
from asyncio import CancelledError, Lock
from enum import IntEnum
from functools import wraps
from typing import Any, Awaitable, Callable, Concatenate, Coroutine, ParamSpec, TypeVar

import aiohttp
import ucapi.media_player
from aiohttp import ClientSession, ClientTimeout
from pyee.asyncio import AsyncIOEventEmitter
from ucapi.media_player import Attributes, MediaType, States

from config import DeviceInstance
from const import MPCHCCommands

_LOGGER = logging.getLogger(__name__)


class Events(IntEnum):
    """Internal driver events."""

    CONNECTED = 0
    ERROR = 1
    UPDATE = 2
    IP_ADDRESS_CHANGED = 3
    DISCONNECTED = 4


_MPCHCDeviceT = TypeVar("_MPCHCDeviceT", bound="MPCHCClient")
_P = ParamSpec("_P")

CONNECTION_RETRIES = 10
UPDATE_LOCK_TIMEOUT = 10.0


def cmd_wrapper(
    func: Callable[Concatenate[_MPCHCDeviceT, _P], Awaitable[dict[str, Any] | None]],
) -> Callable[Concatenate[_MPCHCDeviceT, _P], Coroutine[Any, Any, ucapi.StatusCodes | None]]:
    """Catch command exceptions."""

    @wraps(func)
    async def wrapper(obj: _MPCHCDeviceT, *args: _P.args, **kwargs: _P.kwargs) -> ucapi.StatusCodes:
        """Wrap all command methods."""
        res = await func(obj, *args, **kwargs)
        await obj.start_polling()
        if res and isinstance(res, dict):
            result: dict[str, Any] | None = res.get("result", None)
            if result and result.get("responseCode", None) == "0":
                return ucapi.StatusCodes.OK
            return ucapi.StatusCodes.BAD_REQUEST
        return ucapi.StatusCodes.OK

    return wrapper


class MPCHCClient:
    """Client for MPC-HC TV STBs."""

    # pylint: disable = E0606

    def __init__(self, device_config: DeviceInstance, device_id=None):
        """Create a MPC-HC STB instance."""
        if device_id is None:
            self.id = device_config.id
        else:
            self.id = device_id
        self.hostname = device_config.address
        self.port = device_config.port
        self._device_config = device_config
        self.timeout = 3
        self._media_type = MediaType.VIDEO
        self._media_title = ""
        self._state = States.UNKNOWN
        self._event_loop = asyncio.get_event_loop() or asyncio.get_running_loop()
        self.events = AsyncIOEventEmitter(self._event_loop)
        self._update_lock = Lock()
        self._update_lock_time: float = 0
        self._session: ClientSession | None = None
        self._reconnect_retry = 0
        self._update_task = None
        self._player_variables = {}
        self._media_position_updated_at: datetime.datetime | None = None
        self._media_position = 0
        self._media_duration = 0
        self._subtitle_track: str | None = None
        self._audio_track: str | None = None
        self._muted = False
        self._volume_level = 100
        self._playback_rate = 1.0
        self._connected = False

    async def check_session(self):
        """Check session state."""
        if self._session:
            return
        await self.connect()

    async def connect(self):
        """Connect to SDB."""
        if self._session:
            await self._session.close()
            self._session = None
        session_timeout = aiohttp.ClientTimeout(total=None, sock_connect=self.timeout, sock_read=self.timeout)
        # connector = aiohttp.TCPConnector(ssl=False)
        self._session = aiohttp.ClientSession(timeout=session_timeout, raise_for_status=True, trust_env=True)
        self.events.emit(Events.CONNECTED, self.id)
        await self.start_polling()

    async def disconnect(self):
        """Disconnect from STB."""
        await self.stop_polling()
        if self._session:
            await self._session.close()
            self._session = None
        self._connected = False

    async def _background_update_task(self):
        self._reconnect_retry = 0
        while True:
            if not self._device_config.always_on:
                if not self._connected:
                    self._reconnect_retry += 1
                    if self._reconnect_retry > CONNECTION_RETRIES:
                        _LOGGER.debug(
                            "[%s] Stopping update task as the device %s is off", self._device_config.address, self.id
                        )
                        break
                    _LOGGER.debug(
                        "[%s] Device %s is off, retry %s", self._device_config.address, self.id, self._reconnect_retry
                    )
                elif self._reconnect_retry > 0:
                    self._reconnect_retry = 0
                    _LOGGER.debug("[%s] Device %s is on again", self._device_config.address, self.id)
            await self.update()
            await asyncio.sleep(10)
        self._update_task = None
        await self.disconnect()

    async def start_polling(self):
        """Start polling task."""
        if self._update_task is not None:
            return
        _LOGGER.debug("[%s] Start polling task for device %s", self._device_config.address, self.id)
        self._update_task = self._event_loop.create_task(self._background_update_task())

    async def stop_polling(self):
        """Stop polling task."""
        if self._update_task:
            try:
                self._update_task.cancel()
            except CancelledError:
                pass
            self._update_task = None
            try:
                self._update_lock.release()
            except RuntimeError:
                pass

    async def get_device_info(self) -> str | None:
        """Return device information."""
        response = await self._session.get(f"{self.url}/info.html", timeout=ClientTimeout(3))
        mpchc_variables = re.findall(r'<p id="(.+?)">(.+?)</p>', await response.text(encoding="utf-8"))
        _data: dict[str, Any] = {}
        for var in mpchc_variables:
            _data[var[0]] = var[1]
        return _data.get("mpchc_np", None)

    async def update(self) -> dict[str, Any] | None:
        """Update method to refresh data."""
        # pylint: disable=R0914,R1702,R0915
        if self._update_lock.locked():
            _LOGGER.debug("[%s] Update is locked", self._device_config.address)
            if time.time() - self._update_lock_time > UPDATE_LOCK_TIMEOUT:
                _LOGGER.warning(
                    "[%s] Update is locked since a too long time, unlock it anyway", self._device_config.address
                )
                try:
                    self._update_lock.release()
                except RuntimeError:
                    pass
            else:
                return None

        await self._update_lock.acquire()
        self._update_lock_time = time.time()
        if self._device_config.log_client:
            _LOGGER.debug("[%s] Refresh MPC-HC API data", self._device_config.address)
        _data: dict[str, Any] = {}
        try:
            if self._session is None:
                await self.connect()
            updated_data = {}
            current_state = self.state
            response = await self._session.get(f"{self.url}/variables.html", timeout=ClientTimeout(3))
            mpchc_variables = re.findall(r'<p id="(.+?)">(.+?)</p>', await response.text(encoding="utf-8"))

            for var in mpchc_variables:
                self._player_variables[var[0]] = var[1]  # .lower()
                _data[var[0]] = var[1]

            self._connected = True
            state = self._player_variables.get("state", None)
            if state is None:
                self._state = States.OFF
            elif state == "2":
                self._state = States.PLAYING
            elif state == "1":
                self._state = States.PAUSED
            else:
                self._state = States.ON

            if current_state != self.state:
                updated_data[Attributes.STATE] = self.state

            try:
                duration = self._player_variables.get("durationstring", "00:00:00").split(":")
                position = self._player_variables.get("positionstring", "00:00:00").split(":")
                media_duration = int(duration[0]) * 3600 + int(duration[1]) * 60 + int(duration[2])
                media_position = int(position[0]) * 3600 + int(position[1]) * 60 + int(position[2])
                if self._media_position != media_position or self._media_position_updated_at is None:
                    self._media_position = media_position
                    updated_data[Attributes.MEDIA_POSITION] = media_position
                    self._media_position_updated_at = datetime.datetime.now(datetime.timezone.utc)
                    updated_data[Attributes.MEDIA_POSITION_UPDATED_AT] = self.media_position_updated_at
                if self._media_duration != media_duration:
                    self._media_duration = media_duration
                    updated_data[Attributes.MEDIA_POSITION] = self.media_position
                    updated_data[Attributes.MEDIA_DURATION] = media_duration
            # pylint: disable=W0718
            except Exception:
                pass

            current_media_artist = self.media_artist
            self._audio_track = self._player_variables.get("audiotrack", None)
            self._subtitle_track = self._player_variables.get("subtitletrack", None)
            if current_media_artist != self.media_artist:
                updated_data[Attributes.MEDIA_ARTIST] = self.media_artist

            muted = self._player_variables.get("muted", 0) == 1
            if muted != self._muted:
                self._muted = muted
                updated_data[Attributes.MUTED] = self.muted
            try:
                volume = int(self._player_variables.get("volumelevel", 100))
                if volume != self._volume_level:
                    self._volume_level = volume
                    updated_data[Attributes.VOLUME] = self.volume_level
                self._playback_rate = float(self._player_variables.get("playbackrate", 1.0))
            # pylint: disable=W0718
            except Exception:
                pass

            media_title: str | None = self._player_variables.get("file", None)
            if media_title:
                media_title = media_title.rsplit(".", 1)[0]

            if media_title != self._media_title:
                self._media_title = media_title
                updated_data[Attributes.MEDIA_TITLE] = self._media_title

            if updated_data:
                self.events.emit(Events.UPDATE, self._device_config.id, updated_data)
        # pylint: disable=W0718
        except Exception as ex:
            _LOGGER.error("[%s] Error during update %s", self._device_config.address, ex)
            self._connected = False
        self._update_lock.release()
        return _data

    @property
    def attributes(self) -> dict[str, Any]:
        """Return the device attributes."""
        updated_data = {
            Attributes.STATE: self.state,
            Attributes.MEDIA_TYPE: self.media_type,
            Attributes.MEDIA_TITLE: self.media_title if self.media_title else "",
            Attributes.MEDIA_ARTIST: self.media_artist if self.media_artist else "",
            Attributes.MEDIA_POSITION: self.media_position,
            Attributes.MEDIA_DURATION: self.media_duration,
            Attributes.MUTED: self.muted,
            Attributes.VOLUME: self.volume_level,
        }
        return updated_data

    @property
    def state(self) -> States:
        """State of device."""
        return self._state

    @property
    def url(self):
        """Return formatted URL."""
        return f"http://{self._device_config.address}:{self._device_config.port}"

    @property
    def media_type(self):
        """Media type of current media."""
        return self._media_type

    @property
    def media_title(self):
        """Media title of current media."""
        return self._media_title

    @property
    def media_artist(self):
        """Current media artist."""
        media_artist: list[str] = []
        if self._audio_track:
            media_artist.append(self._audio_track)
        if self._subtitle_track:
            media_artist.append(self._subtitle_track)
        return " - ".join(media_artist)

    @property
    def media_position(self):
        """Current media duration."""
        return self._media_position

    @property
    def media_position_updated_at(self) -> str | None:
        """Return timestamp of urrent media position."""
        if self._media_position_updated_at:
            return self._media_position_updated_at.isoformat()
        return None

    @property
    def media_duration(self):
        """Current media duration."""
        return self._media_duration

    @property
    def muted(self):
        """Is current media muted."""
        return self._muted

    @property
    def volume_level(self):
        """Current volume level."""
        return self._volume_level

    async def exit(self):
        """Exit MPC-HC."""
        return await self._send_command(MPCHCCommands.EXIT)

    async def _send_command(self, command_id: MPCHCCommands):
        """Send a command to MPC-HC via its window message ID."""
        params = {"wm_command": command_id}
        _LOGGER.debug("[%s] Send command %s %s", f"{self.url}/command.html", self._device_config.id, params)
        await self._session.get(f"{self.url}/command.html", params=params, timeout=ClientTimeout(3))

    async def _send_command_params(self, params: dict[str, Any]):
        """Send a command to MPC-HC via its window message ID."""
        _LOGGER.debug("[%s] Send command %s %s", f"{self.url}/command.html", self._device_config.id, params)
        await self._session.post(f"{self.url}/command.html", params=params, timeout=ClientTimeout(3))

    @cmd_wrapper
    async def send_command(self, command_id: MPCHCCommands):
        """Send a command to MPC-HC via its window message ID."""
        await self._send_command(command_id)

    @cmd_wrapper
    async def seek(self, position: float) -> None:
        """Seek media to given position."""
        params = {"wm_command": -1, "position": str(datetime.timedelta(seconds=position))}
        await self._send_command_params(params)
        asyncio.create_task(self.update())

    @cmd_wrapper
    async def volume_up(self):
        """Volume up the media player."""
        await self._send_command(MPCHCCommands.VOLUME_UP)

    @cmd_wrapper
    async def volume_down(self):
        """Volume down media player."""
        await self._send_command(MPCHCCommands.VOLUME_DOWN)

    @cmd_wrapper
    async def mute_volume(self):
        """Mute the volume."""
        await self._send_command(MPCHCCommands.VOLUME_MUTE)

    @cmd_wrapper
    async def play(self):
        """Send play command."""
        await self._send_command(MPCHCCommands.PLAY)

    @cmd_wrapper
    async def play_pause(self):
        """Send play/pause command."""
        await self._send_command(MPCHCCommands.PLAY_PAUSE)

    @cmd_wrapper
    async def pause(self):
        """Send pause command."""
        await self._send_command(MPCHCCommands.PAUSE)

    @cmd_wrapper
    async def stop(self):
        """Send stop command."""
        await self._send_command(MPCHCCommands.STOP)

    @cmd_wrapper
    async def next_track(self):
        """Send next track command."""
        await self._send_command(MPCHCCommands.NEXT)

    @cmd_wrapper
    async def previous_track(self):
        """Send previous track command."""
        await self._send_command(MPCHCCommands.PREVIOUS)
