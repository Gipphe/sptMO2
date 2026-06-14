from typing import List, Tuple

import mobase
from PyQt6.QtCore import QFileInfo

from ..basic_features import BasicModDataChecker, GlobPatterns
from ..basic_game import BasicGame


class SPTGame(BasicGame, mobase.IPluginFileMapper):
    Name = "SPT Plugin"
    Author = "Archon"
    Version = "2.0.0"
    GameName = "SPT"
    GameShortName = "spt"
    GameBinary = "SPT.Launcher.exe"
    GameDataPath = "%GAME_PATH%"
    GameSaveExtension = "json"
    GameSavesDirectory = "%GAME_PATH%/user/profiles"

    def __init__(self):
        super().__init__()
        mobase.IPluginFileMapper.__init__(self)

    def init(self, organizer: mobase.IOrganizer) -> bool:
        super().init(organizer)
        if hasattr(self, "_featureMap"):
            self._featureMap[mobase.ModDataChecker] = SPTModDataChecker()
        else:
            self._register_feature(SPTModDataChecker())
        return True

    def executables(self) -> List[mobase.ExecutableInfo]:
        execs = super().executables()

        workaroundPath = self.windows_workaround()
        linux_workaround_path = self.linux_workaround()

        execs.append(
            mobase.ExecutableInfo("Launch SP Tarkov", QFileInfo(workaroundPath))
        ).append(
            mobase.ExecutableInfo(
                "Launch SPT Tarkov (Linux)", QFileInfo(linux_workaround_path)
            )
        )
        execs.pop(0)
        return execs

    def windows_workaround(self) -> str:
        """
        A bat script file to bridge the environment to server and launcher.
        """
        workaroundPath = self._gamePath + "/sptvfsbridge.bat"

        try:
            workaround = open(workaroundPath, "rt")
        except FileNotFoundError:
            with open(workaroundPath, "wt") as workaround:
                workaround.write(
                    """
@echo off
setlocal

set "launcher_path=SPT.Launcher.exe"
set "server_path=SPT/SPT.Server.exe"

REM Launch the server.exe
start "" "%server_path%"

REM Wait for a moment to ensure the server.exe has started
timeout /t 5 /nobreak >nul

REM Launch the launcher.exe
start "" "%launcher_path%"

endlocal
"""
                )
        workaround.close()
        return workaroundPath

    def linux_workaround(self) -> str:
        workaroundPath = self._gamePath + "/sptvfsbridge.sh"

        try:
            workaround = open(workaroundPath, "rt")
        except FileNotFoundError:
            with open(workaroundPath, "wt") as workaround:
                workaround.write(
                    """
#!/usr/bin/env bash
launcher_path=SPT.Launcher.exe
server_path=SPT/SPT.Server.Linux
nohup x-terminal-emulator -e "bash -c '$server_path'" &
sleep 5s
nohup umu-launcher "$launcher_path" &
                    """
                )

    def mappings(self) -> list[mobase.Mapping]:
        return []


class SPTModDataChecker(BasicModDataChecker):
    def __init__(self, patterns: GlobPatterns = GlobPatterns()):
        super().__init__(
            GlobPatterns(
                valid=["BepInEx", "SPT"],
                move={
                    "plugins": "BepInEx/plugins",
                    "patchers": "BepInEx/patchers",
                    "config": "BepInEx/config",
                    "*": "SPT/user/mods/",
                },
            ).merge(patterns),
        )

