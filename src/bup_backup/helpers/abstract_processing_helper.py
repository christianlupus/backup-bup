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

class ConfigurationException(Exception):
    pass

class AbstractProcessingHelper:
    def __init__(self, config: bup_backup.config.BackupConfig, verbose=False, dryRun=False, debug=False):
        self.config = config

        self.verbose = verbose
        self.dryRun = dryRun
        self.debug = debug

        self.configHelper = ConfigHelper(config)

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
    
    def execute(self, index):
        raise Exception('Not yet implemented.')

    def finish(self, index):
        pass
