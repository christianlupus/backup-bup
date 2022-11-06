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
from ..config_helper import ConfigHelper

from .middleware import Middleware

import hashlib

class LVMSnapshotMiddleware(Middleware):
    def __init__(
        self,
        config: bup_backup.config.BackupConfig,
        configHelper: ConfigHelper,
        dry, verbose, debug
    ):
        self.config = config
        self.configHelper = configHelper

        self.dry = dry
        self.verbose = verbose
        self.debug = debug

        self.lv = bup_backup.lvm.Lv()

    def __getSnapNameInPlace(self, index, snapNameBase):
        dest = self.config.table[index].target
        snapName = f'{snapNameBase}---{hashlib.md5(dest.encode()).hexdigest()}'
        return snapName
    
    def __getSnapNameTemporarySnapshot(self, index, snapNameBase):
        snapName = f'{snapNameBase}---tmp'
        return snapName
        
    def __getSnapName(self, index, runInplace):
        snapNameBase = self.configHelper.getOption(index, 'snap_name')

        if runInplace:
            return self.__getSnapNameInPlace(index, snapNameBase)
        else:
            return self.__getSnapNameTemporarySnapshot(index, snapNameBase)
        
    def prepare(self, index):
        return None

    def beforeStep(self, index, source, inPlace, state):
        snapName = self.__getSnapName(index, inPlace)
        size = self.configHelper.getOption(index, 'snap_size')

        if self.verbose:
            print(f'Create snapshot {snapName} using middleware.')
        
        fullSnapName = self.lv.createSnapshot(
            name=source, snapName=snapName,
            size=size,
            dry=self.dry, verbose=self.verbose, debug=self.debug
            )
        
        return (fullSnapName, None)

    def afterStep(self, dest, state):
        if self.verbose:
            print(f'Removing snapshot {dest} using middleware.')
        
        self.lv.removeSnapshot(dest, dry=self.dry, verbose=self.verbose, debug=self.debug)
