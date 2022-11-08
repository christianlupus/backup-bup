"""
    Copyright (C) 2022 Christian Wolf

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

# from .config import BackupConfig
import bup_backup
from .config_helper import ConfigHelper

import os
import shutil
import hashlib

class Workdir:
    def __init__(self, config: bup_backup.config.BackupConfig):
        self.config = config
        self.configHelper = ConfigHelper(config)

    def getWorkingBasePath(self):
        workFolder = self.configHelper.getGlobalOption('work_folder', '')

        if workFolder == '':
            raise ConfigurationException('There was no work_folder specified.')
        
        return workFolder
    
    def getRelativeWorkingPath(self, index: int):
        target = self.config.table[index].target
        while target[0] == '/':
            target = target[1:]
        relPath = os.path.join(self.config.table[index].branch, target)
        return relPath
        # return hashlib.md5(relPath.encode()).hexdigest()

    def getWorkingPath(self, index: int):
        return os.path.join(self.getWorkingBasePath(), self.getRelativeWorkingPath(index))
    
    def ensureWorkingPathExists(self, index: int, dry: bool, emptyDir: bool = False):
        path = self.getWorkingPath(index)
        self.ensurePathExists(path, dry, emptyDir)
        return path

    def ensurePathExists(self, path, dry: bool, emptyDir: bool = False):
        if emptyDir and os.path.exists(path):
            if dry:
                print(f"Removing {path} for later recreation.")
            else:
                shutil.rmtree(path)
        
        if not os.path.exists(path):
            if dry:
                print(f"Creating folder {path}.")
            else:
                os.makedirs(path)
    
    