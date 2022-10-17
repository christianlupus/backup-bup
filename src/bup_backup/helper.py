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

import os
import re

class ConfigurationException(Exception):
    pass

class PreprocessingHelper:
    def __init__(self, config: bup_backup.config.BackupConfig, verbose=False, dryRun=False, debug=False):
        self.config = config

        self.verbose = verbose
        self.dryRun = dryRun
        self.debug = debug

    def getOption(self, index: int, param: str, fallback = None):
        return self.config.table[index].options.get(param, self.config.common.get(param, fallback))

    def getParsedSize(self, str):
        pattern = '([0-9,.]+)([kKmMgGtT]?)'
        expression = re.compile(pattern)
        match = expression.fullmatch(str)

        mantis = match.group(1).replace(',', '.')
        unit = match.group(2)

        number = float(mantis)
        unitMap = {
            'k': 1024,
            'm': 1024*1024,
            'g': 1024*1024*1024,
            't': 1024*1024*1024*1024
        }
        # print(number, mantis, unit, unitMap[unit.lower()])
        return number * unitMap[unit.lower()]

    def __isCommonConfigurationValid(self, index: int):
        # Is the current user root?
        if os.environ.get('USER') != 'root':
            raise ConfigurationException('You must be root in order to allow system commands to execute')
    
    def checkConfig(self, index):
        self.__isCommonConfigurationValid(index)

        if not os.path.exists(self.config.table[index].source):
            raise ConfigurationException(f"The source {self.config.table[index].source} does not exist.")
        
    def prepare(self, index):
        pass

    def finish(self, index):
        pass

class MountingProcessingHelper(PreprocessingHelper):
    def getMountPoint(self, index):
        tableLine = self.config.table[index]
        base = self.getOption(index, 'mount_base')
        basedPath = os.path.join(base, tableLine.source)
        return self.getOption(index, 'mount_path', basedPath)

class PlainProcessingHelper(MountingProcessingHelper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def checkConfig(self, index: int):
        super().checkConfig(index)
        tableLine = self.config.table[index]

        if not os.path.isdir(tableLine.source):
            raise ConfigurationException(f"Path {tableLine.source} is no folder.")

class LVMProcessingHelper(MountingProcessingHelper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.vg = bup_backup.lvm.Vg()
        self.lv = bup_backup.lvm.Lv()

    def checkConfig(self, index: int):
        super().checkConfig(index)
        tableLine = self.config.table[index]

        vgName = self.lv.getVgName(tableLine.source)
        snapName = f"/dev/{vgName}/{self.getOption(index, 'snap_name')}"
        if self.vg.hasLv(snapName):
            raise ConfigurationException(f"Cannot create {snapName} as it exists already.")
        
        snapSizeStr = self.getOption(index, 'snap_size')
        snapSize = self.getParsedSize(snapSizeStr)
        # print(f"snapSize ({snapSize}) comapted with free space ({self.vg.getFreeSize(vgName)})")
        # print(self.vg.getPeSize(vgName))
        # print(self.vg.getFreeSizePE(vgName))
        if snapSize > self.vg.getFreeSize(vgName):
            raise ConfigurationException(f"Not enough free space in VG {vgName} to create snapshot for {tableLine.source}.")
        

class CryptProcessingHelper(MountingProcessingHelper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def checkConfig(self, index: int):
        super().checkConfig(index)
        tableLine = self.config.table[index]

        decryptName = self.getOption(index, 'decrypt_name')
        if os.path.exists(os.path.join('/dev/mapper', decryptName)):
            raise ConfigurationException(f"Could not use {decryptName} as name of the decrypted device for {tableLine.source} as it exists already.")
        
        keyfile = self.getOption(index, 'key')
        if not os.path.exists(keyfile):
            raise ConfigurationException(f"No key was given for decryption of {tableLine.source}.")
        if not os.access(keyfile, os.R_OK):
            raise ConfigurationException(f"Cannot access key file {keyfile}.")
        keyfileStat = os.stat(keyfile)
        if keyfileStat.st_size == 0:
            raise ConfigurationException(f"The key file {keyfile} has length 0.")

class LVMCryptProcessingHelper(PreprocessingHelper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.lvmHelper = LVMProcessingHelper(*args, **kwargs)
        self.cryptoHelper = CryptProcessingHelper(*args, **kwargs)

    def checkConfig(self, index: int):
        super().checkConfig(index)
        tableLine = self.config.table[index]

        self.lvmHelper.checkConfig(index)
        self.cryptoHelper.checkConfig(index)

        #####################  TODO

## Create classes to handle LVM/Crypt/LVM+CRYPT classes
