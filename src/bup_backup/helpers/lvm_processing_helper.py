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
from .rsync_helper import RSyncHelper

import hashlib

class LVMProcessingHelper(AbstractProcessingHelper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.vg = bup_backup.lvm.Vg()
        self.lv = bup_backup.lvm.Lv()

    def checkConfig(self, index: int):
        super().checkConfig(index)
        tableLine = self.config.table[index]

        vgName = self.lv.getVgName(tableLine.source)
        snapName = f"/dev/{vgName}/{self.configHelper.getOption(index, 'snap_name')}"
        if self.vg.hasLv(snapName):
            raise ConfigurationException(f"Cannot create {snapName} as it exists already.")
        
        snapSizeStr = self.configHelper.getOption(index, 'snap_size')
        snapSize = self.configHelper.getParsedSize(snapSizeStr)
        # print(f"snapSize ({snapSize}) comapted with free space ({self.vg.getFreeSize(vgName)})")
        # print(self.vg.getPeSize(vgName))
        # print(self.vg.getFreeSizePE(vgName))
        if snapSize > self.vg.getFreeSize(vgName):
            raise ConfigurationException(f"Not enough free space in VG {vgName} to create snapshot for {tableLine.source}.")

    def __getSnapName(self, index):
        snapNameBase = self.configHelper.getOption(index, 'snap_name')
        dest = self.config.table[index].target
        runInplace = self.configHelper.getOption(index, 'mount_inplace', False)

        if runInplace:
            snapName = f'{snapNameBase}---{hashlib.md5(dest.encode()).hexdigest()}'
        else:
            snapName = f'{snapNameBase}---tmp'
        
        return snapName

    def prepareBackup(self, index):
        name = self.config.table[index].source
        size = self.configHelper.getOption(index, 'snap_size')
        runInplace = self.configHelper.getOption(index, 'mount_inplace', False)

        workdir = Workdir(self.config)
        workpath = workdir.ensureWorkingPathExists(index, self.dryRun)

        snapName = self.__getSnapName(index)
        fullSnapName = self.lv.createSnapshot(name, snapName, size, self.dryRun, self.verbose, self.debug)

        mountHelper = MountHelper(self.config)

        if runInplace:
            # We need to mount the snapshot to the workdir.
            if self.verbose:
                print(f'Mounting snapshot to workpath {workpath}.')
            
            mountHelper.mount(fullSnapName, workpath, self.dryRun, self.verbose, self.debug)
        else:
            mountPath = mountHelper.getMountPoint(index)
            workdir.ensurePathExists(mountPath, self.dryRun)

            if self.verbose:
                print(f'Mounting snapshot to temporary mount point {mountPath}.')
            mountHelper.mount(fullSnapName, mountPath, self.dryRun, self.verbose, self.debug)

            if self.verbose:
                print(f'Cloning files from {mountPath} to {workpath}.')
            rsync = RSyncHelper(self.config)
            rsync.execute(index, mountPath, workpath, self.verbose, self.dryRun, self.debug)

            if self.verbose:
                print('Unmounting from temporary mount point')
            mountHelper.umount(mountPath, self.dryRun, self.verbose, self.debug)

            if self.verbose:
                print('Removing temporary snapshot')
            self.lv.removeSnapshot(fullSnapName, dry=self.dryRun, verbose=self.verbose, debug=self.debug)
    
    def cleanUpBackup(self, index):
        if self.configHelper.getOption(index, 'mount_inplace', False):
            workdir = Workdir(self.config)
            workpath = workdir.ensureWorkingPathExists(index, self.dryRun)
            mountHelper = MountHelper(self.config)

            if self.verbose:
                print(f'Unmounting snapshot from workpath {workpath}.')
            mountHelper.umount(workpath, self.dryRun, self.verbose, self.debug)

            snapName = self.__getSnapName(index)
            fullSnapName = self.lv.getFullSnapshotName(self.config.table[index].source, snapName)
            if self.verbose:
                print(f'Removing snapshot {snapName}')
            self.lv.removeSnapshot(fullSnapName, dry=self.dryRun, verbose=self.verbose, debug=self.debug)
