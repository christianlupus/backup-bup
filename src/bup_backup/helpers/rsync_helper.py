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

import bup_backup

from .abstract_processing_helper import (
    ConfigurationException
)
from .config_helper import ConfigHelper

import os
import subprocess

class RSyncHelper:
    __DEFAULT_SHORT_OPTIONS = '-ax'
    __DEFAULT_OPTIONS = '--delete --delete-delay --delete-excluded'

    def __init__(self, config: bup_backup.config.BackupConfig):
        self.checked = False
        self.config = config
        self.configHelper = ConfigHelper(config)
    
    def __getRSync(self):
        return self.config.common.get('rsync', '/usr/bin/rsync')
    
    def __getShortOptions(self, index: int):
        shortOpts = self.configHelper.getOption(index, 'rsync_short_opts', self.__DEFAULT_SHORT_OPTIONS)
        return shortOpts
    
    def __getLongOptions(self, index: int):
        opts = self.configHelper.getOption(index, 'rsync_opts', self.__DEFAULT_OPTIONS)
        return opts.split(' ')
    
    def check(self):
        if not self.checked:
            rsyncPath = self.__getRSync()
            
            if not os.path.exists(rsyncPath):
                raise ConfigurationException(f"Cannot find rsync at {rsyncPath}.")
            if not os.access(rsyncPath, os.R_OK + os.X_OK):
                raise ConfigurationException(f"Cannot execute rsync command {rsyncPath}.")
            
            self.checked = True
    
    def execute(self, index: int, source: str, dest: str, verbose: bool, dry: bool, debug: bool, protectedDirs: list[str] = []):
        src = source
        if not src.endswith('/'):
            src = f"{src}/"
        
        cmd = [
            self.__getRSync(),
            self.__getShortOptions(index)
        ] + self.__getLongOptions(index) + [
            src, dest
        ]

        for pd in protectedDirs:
            cmd = cmd + [f"-fP {pd}", f"-fH {pd}"]

        if verbose:
            cmd.append('-v')
        if dry:
            cmd.append('-n')
        
        if debug:
            print('RSync command line:', cmd)
        
        sp = subprocess.run(cmd)
        if dry:
            if sp.returncode != 0:
                print('Warning: rsync failed. This might be a problem.')
        else:
            sp.check_returncode()
