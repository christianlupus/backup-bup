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

import os
import subprocess
import hashlib

class MountHelper:
    
    def __init__(self, config: bup_backup.config.BackupConfig):
        self.config = config
        self.configHelper = ConfigHelper(self.config)

    def getMountPoint(self, index):
        tableLine = self.config.table[index]
        base = self.configHelper.getOption(index, 'mount_base')
        basedPath = os.path.join(base, hashlib.md5(tableLine.source.encode()).hexdigest())
        return self.configHelper.getOption(index, 'mount_path', basedPath)
    
    def mount(self, device, location, dry, verbose, debug, options = 'ro'):
        if verbose:
            print(f'Mounting {device} at {location} (options {options}).')
        
        cmd = ['mount', device, location]
        if options is not None:
            cmd.append('-o')
            cmd.append(options)
        
        if debug:
            print('Mount command', cmd)
        
        if dry:
            print(f"Mounting {device}")
        else:
            subprocess.run(cmd).check_returncode()
    
    def umount(self, location, dry, verbose, debug):
        if verbose:
            print(f'Unmounting {location}.')
        
        cmd = ['umount', location]
        
        if debug:
            print('Umount command', cmd)
        
        if dry:
            print(f"Carry out umount {location}")
        else:
            subprocess.run(cmd).check_returncode()
