"""
Static file of the integration driver.

:copyright: (c) 2025 Albaintor
:license: Mozilla Public License Version 2.0, see LICENSE for more details.
"""

import dataclasses
from dataclasses import dataclass

__version__ = "1.0.3"

from enum import Enum
from typing import Any

from ucapi.ui import Buttons, DeviceButtonMapping, EntityCommand

SCAN_INTERVAL = 10
DEFAULT_NAME = "MPC-HC"
DEFAULT_PORT = 13579


@dataclass
class MPCHCCommand:
    """MPC-HC command."""

    wm_command: int
    param_name: str | None = dataclasses.field(default=None)
    param_value: Any | None = dataclasses.field(default=None)

    # pylint: disable=R0801
    def __post_init__(self):
        """Apply default values on missing fields."""
        for attribute in dataclasses.fields(self):
            # If there is a default and the value of the field is none we can assign a value
            if (
                not isinstance(attribute.default, dataclasses.MISSING.__class__)
                and getattr(self, attribute.name) is None
            ):
                setattr(self, attribute.name, attribute.default)


class MPCHCCommands(int, Enum):
    """List of commands."""

    AUDIO_DELAY_DECREASE = 906
    AUDIO_DELAY_INCREASE = 905
    AUDIO_TRACK_NEXT = 952
    AUDIO_TRACK_PREV = 953
    BOOKMARK_ADD = 975
    BRIGHTNESS_DOWN = 985
    BRIGHTNESS_UP = 984
    CLOSE = 804
    COLORS_RESET = 992
    CONTRAST_DOWN = 987
    CONTRAST_UP = 986
    CURSOR_CENTER = 876
    CURSOR_DOWN = 871
    CURSOR_LEFT = 868
    CURSOR_RIGHT = 869
    CURSOR_UP = 870
    EXIT = 816
    GOTO = 893
    GOTO_START = 1085
    LOAD_SUBTITLES_EXT = 809
    MENU_AUDIO = 1000
    MENU_BOOKMARK = 936
    MENU_DVD_ANGLE = 927
    MENU_DVD_AUDIO = 926
    MENU_DVD_BACK = 934
    MENU_DVD_CHAPTERS = 928
    MENU_DVD_DOWN = 932
    MENU_DVD_EXIT = 935
    MENU_DVD_LEFT = 929
    MENU_DVD_MAIN = 924
    MENU_DVD_RIGHT = 930
    MENU_DVD_SELECT = 933
    MENU_DVD_SUBTITLES = 925
    MENU_DVD_TITLE = 923
    MENU_DVD_UP = 931
    MENU_GOTO = 1002
    MENU_HISTORY = 1018
    MENU_OPTIONS = 815
    MENU_OSD_CURRENTFILE = 1037
    MENU_OSD_LOCALTIME = 1036
    MENU_OSD_TIMELEFT = 1043
    MENU_RECENT_FILES = 1006
    MENU_SUBTITLES = 1001
    NEXT = 922
    NEXT_FILE = 920
    NEXT_KEY_PICTURE = 898
    NEXT_PICTURE = 891
    OPEN_DEVICE = 802
    OPEN_DVD = 801
    OPEN_FILE = 800
    OPEN_FILE_QUICK = 969
    OPEN_FOLDER = 1016
    OPEN_ISO_FILE = 1090
    PAUSE = 888
    PLAY = 887
    PLAY_PAUSE = 889
    PREVIOUS = 921
    PREVIOUS_FILE = 919
    PREVIOUS_KEY_PICTURE = 897
    PREVIOUS_PICTURE = 892
    PROPERTIES = 814
    REPEAT = 967
    RESUME_FILE = 976
    SATURATION_DOWN = 991
    SATURATION_UP = 990
    SAVE_AS = 805
    SAVE_DISP_PICT_AUTO = 996
    SAVE_PICTURE = 806
    SAVE_PICTURE_AUTO = 807
    SAVE_PICTURE_CLIPB = 997
    SAVE_SUBTITLES = 810
    SAVE_THUMBS = 808
    SHOW_CONTROLBAR = 819
    SHOW_HEADER_MENUS = 817
    SHOW_OSD = 820
    SHOW_PLAYLIST = 824
    SHOW_STATS = 821
    SHOW_STATUS = 822
    SHOW_STATUSBAR = 818
    SPEED_DOWN = 894
    SPEED_NORMAL = 896
    SPEED_UP = 895
    STEP_BACKWARD = 899
    STEP_BACKWARD_LARGE = 903
    STEP_BACKWARD_MEDIUM = 901
    STEP_FORWARD = 900
    STEP_FORWARD_LARGE = 904
    STEP_FORWARD_MEDIUM = 902
    STOP = 890
    SUBTITLES_DELAY_DOWN = 24001
    SUBTITLES_DELAY_UP = 24000
    SUBTITLES_DOWN = 1101
    SUBTITLES_LEFT = 1102
    SUBTITLES_NEXT = 954
    SUBTITLES_NEXT2 = 1015
    SUBTITLES_OFFSET_LEFT = 1012
    SUBTITLES_OFFSET_RIGHT = 1013
    SUBTITLES_PREVIOUS = 955
    SUBTITLES_PREVIOUS2 = 1014
    SUBTITLES_RELOAD = 1173
    SUBTITLES_RESETPOS = 1104
    SUBTITLES_RIGHT = 1103
    SUBTITLES_SIZE_DOWN = 1108
    SUBTITLES_SIZE_UP = 1107
    SUBTITLES_SYNC = 823
    SUBTITLES_TOGGLE = 956
    SUBTITLES_UP = 1100
    VIEW_ADJUST = 838
    VIEW_ADJUST_INSIDE = 839
    VIEW_ADJUST_OUTSIDE = 840
    VIEW_ALWAYS_ONTOP = 884
    VIEW_COMPACT = 828
    VIEW_DOUBLE = 837
    VIEW_FULLSCREEN = 830
    VIEW_FULLSCREEN_KEEP = 831
    VIEW_HALF = 835
    VIEW_MINIMAL = 827
    VIEW_MOVE_MAINSCREEN = 1038
    VIEW_NEXT = 859
    VIEW_NORMAL = 829
    VIEW_ORIGIN = 836
    VIEW_PIVOTE_CLOCKWISE = 882
    VIEW_PIVOTE_FLIP = 880
    VIEW_PIVOTE_INV_CLOCKW = 881
    VIEW_RESET = 861
    VIEW_SWAP_VIDEO = 843
    VIEW_VIDEO1 = 841
    VIEW_VIDEO2 = 842
    VIEW_ZOOM_100 = 833
    VIEW_ZOOM_200 = 834
    VIEW_ZOOM_50 = 832
    VIEW_ZOOM_AUTO = 968
    VOLUME_AUTO = 994
    VOLUME_CENTER_DOWN = 1151
    VOLUME_CENTER_UP = 1150
    VOLUME_DOWN = 908
    VOLUME_GAIN_DOWN = 971
    VOLUME_GAIN_MAX = 973
    VOLUME_GAIN_OFF = 972
    VOLUME_GAIN_UP = 970
    VOLUME_MUTE = 909
    VOLUME_UP = 907


REMOTE_BUTTONS_MAPPING: list[DeviceButtonMapping] = [
    DeviceButtonMapping(button=Buttons.BACK, short_press=EntityCommand(cmd_id=str(MPCHCCommands.MENU_DVD_BACK))),
    DeviceButtonMapping(button=Buttons.HOME, short_press=EntityCommand(cmd_id=str(MPCHCCommands.MENU_DVD_MAIN))),
    DeviceButtonMapping(button=Buttons.CHANNEL_DOWN, short_press=EntityCommand(cmd_id=str(MPCHCCommands.PREVIOUS))),
    DeviceButtonMapping(button=Buttons.CHANNEL_UP, short_press=EntityCommand(cmd_id=str(MPCHCCommands.NEXT))),
    DeviceButtonMapping(button=Buttons.DPAD_UP, short_press=EntityCommand(cmd_id=str(MPCHCCommands.CURSOR_UP))),
    DeviceButtonMapping(button=Buttons.DPAD_DOWN, short_press=EntityCommand(cmd_id=str(MPCHCCommands.CURSOR_DOWN))),
    DeviceButtonMapping(button=Buttons.DPAD_LEFT, short_press=EntityCommand(cmd_id=str(MPCHCCommands.CURSOR_LEFT))),
    DeviceButtonMapping(button=Buttons.DPAD_RIGHT, short_press=EntityCommand(cmd_id=str(MPCHCCommands.CURSOR_RIGHT))),
    DeviceButtonMapping(button=Buttons.DPAD_MIDDLE, short_press=EntityCommand(cmd_id=str(MPCHCCommands.CURSOR_CENTER))),
    DeviceButtonMapping(button=Buttons.PLAY, short_press=EntityCommand(cmd_id=str(MPCHCCommands.PLAY_PAUSE))),
    DeviceButtonMapping(button=Buttons.PREV, short_press=EntityCommand(cmd_id=str(MPCHCCommands.STEP_BACKWARD_MEDIUM))),
    DeviceButtonMapping(button=Buttons.NEXT, short_press=EntityCommand(cmd_id=str(MPCHCCommands.STEP_FORWARD_MEDIUM))),
    DeviceButtonMapping(button=Buttons.VOLUME_UP, short_press=EntityCommand(cmd_id=str(MPCHCCommands.VOLUME_UP))),
    DeviceButtonMapping(button=Buttons.VOLUME_DOWN, short_press=EntityCommand(cmd_id=str(MPCHCCommands.VOLUME_DOWN))),
    DeviceButtonMapping(button=Buttons.MUTE, short_press=EntityCommand(cmd_id=str(MPCHCCommands.VOLUME_MUTE))),
    DeviceButtonMapping(button=Buttons.MENU, short_press=EntityCommand(cmd_id=str(MPCHCCommands.MENU_OPTIONS))),
    DeviceButtonMapping(button=Buttons.STOP, short_press=EntityCommand(cmd_id=str(MPCHCCommands.STOP))),
]

# REMOTE_UI_PAGES: list[UiPage] = [
#     UiPage(**{
#         "page_id": "MPC-HC commands",
#         "name": "MPC-HC commands",
#         "grid": {"width": 4, "height": 6},
#         "items": [
#             {
#                 "command": {"cmd_id": "remote.send", "params": {"command": "POWER", "repeat": 1}},
#                 "icon": "uc:power-on",
#                 "location": {"x": 0, "y": 0},
#                 "size": {"height": 1, "width": 1},
#                 "type": "icon",
#             },
#             {
#                 "command": {"cmd_id": "remote.send", "params": {"command": "MENU", "repeat": 1}},
#                 "icon": "uc:home",
#                 "location": {"x": 1, "y": 0},
#                 "size": {"height": 1, "width": 1},
#                 "type": "icon",
#             },
#             {
#                 "command": {"cmd_id": "remote.send", "params": {"command": "OK", "repeat": 1}},
#                 "icon": "uc:info",
#                 "location": {"x": 2, "y": 0},
#                 "size": {"height": 1, "width": 1},
#                 "type": "icon",
#             },
#             {
#                 "command": {"cmd_id": "remote.send", "params": {"command": "REC", "repeat": 1}},
#                 "icon": "uc:rec",
#                 "location": {"x": 3, "y": 0},
#                 "size": {"height": 1, "width": 1},
#                 "type": "icon",
#             },
#         ],
#     }),
#     {
#         "page_id": "Orange numbers",
#         "name": "Orange numbers",
#         "grid": {"height": 4, "width": 3},
#         "items": [
#             {
#                 "command": {"cmd_id": "remote.send", "params": {"command": "1", "repeat": 1}},
#                 "location": {"x": 0, "y": 0},
#                 "size": {"height": 1, "width": 1},
#                 "text": "1",
#                 "type": "text",
#             },
#             {
#                 "command": {"cmd_id": "remote.send", "params": {"command": "2", "repeat": 1}},
#                 "location": {"x": 1, "y": 0},
#                 "size": {"height": 1, "width": 1},
#                 "text": "2",
#                 "type": "text",
#             },
#             {
#                 "command": {"cmd_id": "remote.send", "params": {"command": "3", "repeat": 1}},
#                 "location": {"x": 2, "y": 0},
#                 "size": {"height": 1, "width": 1},
#                 "text": "3",
#                 "type": "text",
#             },
#             {
#                 "command": {"cmd_id": "remote.send", "params": {"command": "4", "repeat": 1}},
#                 "location": {"x": 0, "y": 1},
#                 "size": {"height": 1, "width": 1},
#                 "text": "4",
#                 "type": "text",
#             },
#             {
#                 "command": {"cmd_id": "remote.send", "params": {"command": "5", "repeat": 1}},
#                 "location": {"x": 1, "y": 1},
#                 "size": {"height": 1, "width": 1},
#                 "text": "5",
#                 "type": "text",
#             },
#             {
#                 "command": {"cmd_id": "remote.send", "params": {"command": "6", "repeat": 1}},
#                 "location": {"x": 2, "y": 1},
#                 "size": {"height": 1, "width": 1},
#                 "text": "6",
#                 "type": "text",
#             },
#             {
#                 "command": {"cmd_id": "remote.send", "params": {"command": "7", "repeat": 1}},
#                 "location": {"x": 0, "y": 2},
#                 "size": {"height": 1, "width": 1},
#                 "text": "7",
#                 "type": "text",
#             },
#             {
#                 "command": {"cmd_id": "remote.send", "params": {"command": "8", "repeat": 1}},
#                 "location": {"x": 1, "y": 2},
#                 "size": {"height": 1, "width": 1},
#                 "text": "8",
#                 "type": "text",
#             },
#             {
#                 "command": {"cmd_id": "remote.send", "params": {"command": "9", "repeat": 1}},
#                 "location": {"x": 2, "y": 2},
#                 "size": {"height": 1, "width": 1},
#                 "text": "9",
#                 "type": "text",
#             },
#             {
#                 "command": {"cmd_id": "remote.send", "params": {"command": "0", "repeat": 1}},
#                 "location": {"x": 1, "y": 3},
#                 "size": {"height": 1, "width": 1},
#                 "text": "0",
#                 "type": "text",
#             },
#         ],
#     },
# ]
