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

import hashlib
import subprocess

class LuksCryptsetupMiddleware:
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

    def prepare(self, index):
        return None

    def __getCryptDeviceName(self, index):
        dynPart = f'{self.config.table[index].branch}:{self.config.table[index].target}'
        return f'snap-crypt-{hashlib.md5(dynPart.encode()).hexdigest()}'
    
    def getFullCryptName(self, index):
        cryptName = self.__getCryptDeviceName(index)
        return f'/dev/mapper/{cryptName}'
    
    def beforeStep(self, index, source, inPlace, state):
        cryptName = self.__getCryptDeviceName(index)
        fullCryptName = self.getFullCryptName(index)
        keyFile = self.configHelper.getOption(index, 'key_file')

        if self.verbose:
            print(f'Decrypting {source} in middleware.')
        
        cmd = [
            'cryptsetup', 'open', 
            '-d', keyFile,
            source,
            cryptName
        ]

        if self.debug:
            print('Decryption command', cmd)
        
        if self.dry:
            print(f'Carrying out decryption of {source} to {cryptName}.')
        else:
            subprocess.run(cmd).check_returncode()
        
        return (fullCryptName, cryptName)

    def afterStep(self, dest, state):
        if self.verbose:
            print(f'Closing crypt device {state} in middleware')
        
        cmd = ['cryptsetup', 'close', state]
        if self.debug:
            print('Closing crypt command:', cmd)
        
        if self.dry:
            print('Closing the crypt device')
        else:
            subprocess.run(cmd).check_returncode()
