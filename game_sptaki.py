# SPT plugin for ModOrganizer, coded by a moron: Me :)
# Note: This is highly incomplete, and will almost deffinitely break.
# Some inconveniences exist, such as the fact that every time you install a mod that does not auto handle, you have to create the user/mods or bepinex/plugins directory manually etc.
# I would like to expand those features, but it will probably happen slowly; I'm not a programmer.
# This script was made by cross referencing several other basic_game extensions.
# I sincerely hope somebody with actual experience comes along and decides to fix it up. But for now, this auto resolves the vast majority of mods on the hub :).
# Discord: Archon001

from typing import List, Tuple
from PyQt5.QtCore import QFileInfo
import mobase
from ..basic_game import BasicGame


class SPTAKIGame(BasicGame, mobase.IPluginFileMapper):

    Name = "SPT AKI Plugin"
    Author = "Archon"
    Version = "1.0.0a"
    GameName = "SPT AKI"
    GameShortName = "sptaki"
    GameBinary = "EscapeFromTarkov.exe"
    GameLauncher = "sptBridge.exe"
    GameDataPath = "%GAME_PATH%"
    GameSaveExtension = "json"
    GameSavesDirectory = "%GAME_PATH%/user/profiles"

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

set "launcher_path=aki.launcher.exe"
set "server_path=aki.server.exe"

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

        return execs


class SPTAKIModDataChecker(mobase.ModDataChecker):
    def __init__(self):
        super().__init__()

    def get_plugins_and_mods(
        self, tree: mobase.IFileTree
    ) -> Tuple[List[mobase.FileTreeEntry], List[mobase.FileTreeEntry]]:

        plugins: List[mobase.FileTreeEntry] = []
        mods: List[mobase.FileTreeEntry] = []

        for e in tree:
            if e.isDir() and e.exists("package.json", mobase.IFileTree.FILE):
                mods.append(e)
            elif e.isFile() and e.suffix().lower() == "dll":
                plugins.append(e)
            elif e.isDir():
                has_dll = False
                for file_entry in e:
                    if file_entry.isFile() and file_entry.suffix().lower() == "dll":
                        has_dll = True
                        break
                if has_dll and not e.exists("package.json", mobase.IFileTree.FILE):
                    plugins.append(e)

        return plugins, mods

    def dataLooksValid(
        self, tree: mobase.IFileTree
    ) -> mobase.ModDataChecker.CheckReturn:
        # Check if we have bepinex/plugins, user/mods folders or .json/.dll
        plugins, mods = self.get_plugins_and_mods(tree)

        if not plugins and not mods:
            if tree.exists("bepinex/plugins") or tree.exists("user/mods"):
                return mobase.ModDataChecker.VALID
            else:
                return mobase.ModDataChecker.INVALID

        return mobase.ModDataChecker.FIXABLE

    def fix(self, tree: mobase.IFileTree) -> mobase.IFileTree:
        plugins, mods = self.get_plugins_and_mods(tree)
        toMove = []
        if mods:
            for entry in tree:
                toMove.append((entry, "/user/mods/"))
            for (entry, path) in toMove:
                tree.move(entry, path, policy=mobase.IFileTree.MERGE)

        if plugins:
            for entry in tree:
                toMove.append((entry, "/bepinex/plugins/"))
            for (entry, path) in toMove:
                tree.move(entry, path, policy=mobase.IFileTree.MERGE)

        return tree
