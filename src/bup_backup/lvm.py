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

import os
import subprocess

class Vg:
    def __init__(self):
        self.cache = {}
    
    def __getVgDisplay(self, name):
        if name not in self.cache.keys():
            sp = subprocess.run(['vgdisplay', '-c', name], capture_output=True, text=True)
            sp.check_returncode()
            self.cache[name] = sp.stdout.strip().split(':')

        return self.cache[name]

    def getPeSize(self, name):
        return int(self.__getVgDisplay(name)[12]) * 1024
    
    def getFreeSizePE(self, name):
        return int(self.__getVgDisplay(name)[15])
    
    def getFreeSize(self, name):
        return self.getFreeSizePE(name) * self.getPeSize(name)
    
    def hasLv(self, name):
        sp = subprocess.run(['lvdisplay', name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if sp.returncode == 0:
            return True
        elif sp.returncode == 5:
            return False
        else:
            raise Exception(f"Could not detect if {name} is a valid LV")

class Lv:
    def __init__(self):
        self.cache = {}
    
    def __getLvDisplay(self, name):
        if name not in self.cache.keys():
            sp = subprocess.run(['lvdisplay', '-c', name], capture_output=True, text=True)
            sp.check_returncode()
            self.cache[name] = sp.stdout.strip().split(':')
        
        return self.cache[name]
    
    def getVgName(self, name):
        return self.__getLvDisplay(name)[1]

    def getFullSnapshotName(self, original, snapName):
        vgName = self.getVgName(original)
        return f'/dev/{vgName}/{snapName}'

    def createSnapshot(self, name, snapName, size, dry, verbose, debug):
        if verbose:
            print(f'Creating snapshort {snapName} for LV {name} with size {size}.')
        
        cmd = [
            'lvcreate', '--snapshot',
            '--name', snapName,
            '--size', size,
            name
        ]
        if not verbose:
            cmd.append('-q')
        
        if debug:
            print('Snapshot command', cmd)

        if dry:
            print(f'Creation of snapshot {snapName}.')
        else:
            subprocess.run(cmd).check_returncode()
        
        return self.getFullSnapshotName(name, snapName)
    
    def removeSnapshot(self, snapName, dry, verbose, debug):
        if verbose:
            print(f'Removing snapshort {snapName}.')
        
        cmd = [
            'lvremove',
            '--force',
            snapName
        ]
        if not verbose:
            cmd.append('-q')
        
        if debug:
            print('Snapshot command', cmd)

        if dry:
            print(f'Removal of snapshot {snapName}.')
        else:
            subprocess.run(cmd).check_returncode()
