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

from .abstract_processing_helper import (
    AbstractProcessingHelper, ConfigurationException
)
from .config_helper import ConfigHelper

from .middleware.crypt import LuksCryptsetupMiddleware
from .middleware.lvm import LVMSnapshotMiddleware
from .middleware.mount import MountMiddleware
from .middleware.runner import MiddlewareRunner

from .workdir import Workdir
from .mount_helper import MountHelper

import bup_backup.lvm

import os

class LVMCryptProcessingHelper(AbstractProcessingHelper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.configHelper = ConfigHelper(self.config)

        self.luksCryptsetupMiddleware = LuksCryptsetupMiddleware(
            config=self.config,
            configHelper=self.configHelper,
            dry=self.dryRun,
            verbose=self.verbose,
            debug=self.debug
        )
        self.lvmSnapshotMiddleware = LVMSnapshotMiddleware(
            config=self.config,
            configHelper=self.configHelper,
            dry=self.dryRun,
            verbose=self.verbose,
            debug=self.debug
        )
        workdir = Workdir(self.config)
        mountHelper = MountHelper(self.config)
        mountMiddleware = MountMiddleware(
            workdir=workdir,
            mountHelper=mountHelper,
            emptyDir=False,
            createDir=True,
            dry=self.dryRun,
            verbose=self.verbose,
            debug=self.debug
        )
        middlewareList = [
            self.lvmSnapshotMiddleware,
            self.luksCryptsetupMiddleware,
            mountMiddleware
        ]

        self.runner = MiddlewareRunner(
            middlewareList=middlewareList,
            config=self.config,
            configHelper=self.configHelper,
            workdir=workdir,
            dry=self.dryRun,
            verbose=self.verbose,
            debug=self.debug
        )

    def checkConfig(self, index: int):
        super().checkConfig(index)
        tableLine = self.config.table[index]

        keyFile = self.configHelper.getOption(index, 'key_file', '')
        if keyFile == '':
            raise ConfigurationException('No keyfile was provided.')
        if not os.path.exists(keyFile):
            raise ConfigurationException(f'The key file {keyFile} does not exist.')
        if not os.access(keyFile, os.R_OK):
            raise ConfigurationException(f'The key file {keyFile} cannot be read.')
        
        keyFileStat = os.stat(keyFile)
        if keyFileStat.st_size == 0:
            raise ConfigurationException(f'The key file {keyFile} seems to be an empty file. This is not possible.')
        
        cryptName = self.luksCryptsetupMiddleware.getFullCryptName(index)
        if os.path.exists(cryptName):
            raise ConfigurationException(f'The configured crypto device {cryptName} name is already occupied.')

        snapName = self.lvmSnapshotMiddleware.getFullSnapshotName(index)
        vg = bup_backup.lvm.Vg()
        if vg.hasLv(snapName):
            raise ConfigurationException(f'The snapshot {snapName} exists already. Cannot use that name twice.')
    
    def prepareBackup(self, index):
        tableLine = self.config.table[index]
        self.runner.prepareBackup(index, tableLine)
    
    def cleanUpBackup(self, index):
        self.runner.cleanUpAfterBackup(index)
