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
from ..workdir import Workdir
from ..mount_helper import MountHelper

from .middleware import Middleware

class MountMiddleware(Middleware):
    def __init__(
        self,
        workdir: Workdir,
        mountHelper: MountHelper,
        emptyDir: bool,
        dry, verbose, debug
    ):
        self.workdir = workdir
        self.mountHelper = mountHelper
        self.emptyDir = emptyDir

        self.dry = dry
        self.verbose = verbose
        self.debug = debug

    def prepare(self, index):
        self.workpath = self.workdir.ensureWorkingPathExists(index, self.dry, emptyDir=self.emptyDir)
        return None

    def beforeStep(self, index, source, inPlace, state):
        if inPlace:
            mountPath = self.workpath
        else:
            mountPath = self.mountHelper.getMountPoint(index)
        
        if self.verbose:
            print('Mounting using mount middleware')
        self.mountHelper.mount(source, mountPath, dry=self.dry, verbose=self.verbose, debug=self.debug)

        return (mountPath, state)

    def afterStep(self, dest, state):
        if self.verbose:
            print(f'Unmounting {dest} using mount middleware')
        self.mountHelper.umount(dest, dry=self.dry, verbose=self.verbose, debug=self.debug)
