from typing import List, Tuple
from PyQt6.QtCore import QFileInfo
import mobase
from ..basic_game import BasicGame
from ..basic_features import BasicModDataChecker, GlobPatterns


class SPTAKIGame(BasicGame, mobase.IPluginFileMapper):

    Name = "SPT Plugin"
    Author = "Archon"
    Version = "1.1.2"
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
        self._featureMap[mobase.ModDataChecker] = SPTAKIModDataChecker()
        return True

    def executables(self) -> List[mobase.ExecutableInfo]:
        execs = super().executables()

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
set "server_path=SPT.Server.exe"

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

        execs.append(
            mobase.ExecutableInfo("Launch SP Tarkov", QFileInfo(workaroundPath))
        )
        execs.pop(0)
        return execs

    def mappings(self) -> list[mobase.Mapping]:
        return []

class SPTAKIModDataChecker(BasicModDataChecker):
    def __init__(self, patterns: GlobPatterns = GlobPatterns()):
        super().__init__(
            GlobPatterns(
                valid=["BepInEx", "User"],
                move={"plugins": "BepInEx/", "patchers": "BepInEx/", "package.json": "User/Mods/", "*.dll": "BepInEx/plugins/", "*": "User/Mods/"},
            ).merge(patterns),
        )