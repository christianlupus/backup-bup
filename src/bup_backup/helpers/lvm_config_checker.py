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
from .config_helper import ConfigHelper
from .abstract_processing_helper import ConfigurationException

class LvmConfigChecker:
    def __init__(self, config: bup_backup.config.BackupConfig):
        self.config = config
        self.configHelper = ConfigHelper(config)
        self.neededVgSizes = {}
        self.neededMaxVgSizes = {}

    def __updateRequiredLvSize(self, index):
        def __handleNoLvm(index):
            pass
        
        lv = bup_backup.lvm.Lv()

        def __handleLvm(index: int):
            vgName = lv.getVgName(self.config.table[index].source)
            currentSnapSize = self.configHelper.getParsedSize(self.configHelper.getOption(index, 'snap_size'))

            if self.configHelper.getOption(index, 'mount_inplace', False) == True:
                # There is nothing to account for permanently as data is copied to work folder.
                # Just the intermediate snapshot is needed
                maxVgTempSize = max(currentSnapSize, self.neededMaxVgSizes.get(vgName, 0))
                self.neededMaxVgSizes[vgName] = maxVgTempSize
            else:
                neededVgSize = self.neededVgSizes.get(vgName, 0) + currentSnapSize
                self.neededVgSizes[vgName] = neededVgSize

        
        handlerMapping = {
            'plain': __handleNoLvm,
            'command': __handleNoLvm,
            'crypt': __handleNoLvm,
            'lvm': __handleLvm,
            'lvm+crypt': __handleLvm,
        }

        # Update the sum and max value
        handlerMapping[self.config.table[index].type](index)

    def checkFreeSpace(self):
        self.neededVgSizes = {}
        self.neededMaxVgSizes = {}

        for index in range(0, len(self.config.table)):
            self.__updateRequiredLvSize(index)
        
        # Worst case scenario: The temporary LV is used after all snapshots are already allocated
        for vgName in self.neededMaxVgSizes.keys():
            self.neededVgSizes[vgName] = self.neededVgSizes.get(vgName, 0) + self.neededMaxVgSizes[vgName]
        
        # Run the checks
        vg = bup_backup.lvm.Vg()
        for vgName in self.neededVgSizes.keys():
            if vg.getFreeSize(vgName) < self.neededVgSizes[vgName]:
                msg = f'There is not enough free space ({vg.getFreeSize(vgName)/1024.0/1024:1.3f} MB) in the VG {vgName} to hold all snapshots (totally {self.neededVgSizes[vgName]/1024.0/1024:1.3f} MB).'
                raise ConfigurationException(msg)
