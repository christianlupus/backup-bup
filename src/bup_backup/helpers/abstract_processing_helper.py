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

class AbstractProcessingHelper:
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

class MountingProcessingHelper(AbstractProcessingHelper):
    def getMountPoint(self, index):
        tableLine = self.config.table[index]
        base = self.getOption(index, 'mount_base')
        basedPath = os.path.join(base, tableLine.source)
        return self.getOption(index, 'mount_path', basedPath)
