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

import bup_backup
from .workdir import Workdir
from .mount_helper import MountHelper
from .middleware import *

import hashlib

class LVMProcessingHelper(AbstractProcessingHelper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.vg = bup_backup.lvm.Vg()
        self.lv = bup_backup.lvm.Lv()

        workdir = Workdir(self.config)
        mountHelper = MountHelper(self.config)
        self.lvmSnapshotMiddleware = LVMSnapshotMiddleware(
            config=self.config,
            configHelper=self.configHelper,
            dry=self.dryRun,
            verbose=self.verbose,
            debug=self.debug
        )
        mountMiddleware = MountMiddleware(
            workdir=workdir,
            mountHelper=mountHelper,
            emptyDir=False,
            createDir=False,
            dry=self.dryRun,
            verbose=self.verbose,
            debug=self.debug
        )
        self.runner = MiddlewareRunner(
            middlewareList=[self.lvmSnapshotMiddleware, mountMiddleware],
            config=self.config,
            configHelper=self.configHelper,
            workdir=workdir,
            dry=self.dryRun, verbose=self.verbose, debug=self.debug
        )

    def checkConfig(self, index: int):
        super().checkConfig(index)
        tableLine = self.config.table[index]
        vgName = self.lv.getVgName(tableLine.source)

        snapName = self.lvmSnapshotMiddleware.getFullSnapshotName(index)
        if self.vg.hasLv(snapName):
            raise ConfigurationException(f"Cannot create {snapName} as it exists already.")
        
        snapSizeStr = self.configHelper.getOption(index, 'snap_size')
        snapSize = self.configHelper.getParsedSize(snapSizeStr)
        if snapSize > self.vg.getFreeSize(vgName):
            raise ConfigurationException(f"Not enough free space in VG {vgName} to create snapshot for {tableLine.source}.")

    def prepareBackup(self, index):
        tableLine = self.config.table[index]
        self.runner.prepareBackup(index, tableLine)
    
    def cleanUpBackup(self, index):
        self.runner.cleanUpAfterBackup(index)
