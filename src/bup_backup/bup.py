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

import subprocess
import os

from .helpers.abstract_processing_helper import ConfigurationException
from .helpers.config_helper import ConfigHelper
from .helpers.workdir import Workdir

class Bup:
    def __init__(self, config, verbose: bool, dry: bool, debug: bool):
        self.config = config

        self.verbose = verbose
        self.dry = dry
        self.debug = debug

        self.configHelper = ConfigHelper(self.config)
        self.workdir = Workdir(self.config)
        
        self.bupCmd = self.configHelper.getGlobalOption('bup_cmd', '/usr/bin/bup')
        self.bupFolder = self.configHelper.getGlobalOption('bup_folder', '')

    def check(self):
        bup_cmd = self.bupCmd
        if not os.path.exists(bup_cmd):
            raise ConfigurationException(f"The bup_cmd configuration ({bup_cmd}) does not exist.")
        if not os.access(bup_cmd, os.R_OK+os.X_OK):
            raise ConfigurationException(f"The bup_cmd configuration ({bup_cmd}) cannot be executed.")

        bup_folder = self.bupFolder
        if bup_folder == '':
            raise ConfigurationException('Configuration variable bup_folder must be provided.')
        if not os.path.exists(bup_folder):
            raise ConfigurationException(f"The bup_folder configuration ({bup_folder}) does not exist.")
        if not os.access(bup_cmd, os.R_OK+os.X_OK+os.W_OK):
            raise ConfigurationException(f"The bup_folder configuration ({bup_folder}) cannot be accessed.")

    def index(self, base):
        if self.verbose:
            print(f"Indexing working folder {base}.")
        
        cmd = [
            self.bupCmd,
            '-d', self.bupFolder,
            'index', base
        ]

        if self.debug:
            print('Bup index command line:', cmd)
        
        if self.dry:
            print('Running bup index command.')
        else:
            if self.verbose:
                subprocess.run(cmd).check_returncode()
            else:    
                sp = subprocess.run(
                    cmd,
                    text=True,
                    stderr=subprocess.STDOUT,
                    stdout=subprocess.PIPE,
                )
                
                if sp.returncode == 0:
                    # Everything went smoothly
                    pass
                else:
                    print(sp.stdout)
                    raise Exception(f"'bup index' terminated with return code {sp.returncode}.")
                    

    def save(self, base):
        if self.verbose:
            print('Preparing to save the working folder.')
        
        cmdStub = [
            self.bupCmd,
            '-d', self.bupFolder,
            'save', '-q',
        ]

        for branch in self.__getAllBranches():
            if self.verbose:
                print(f"Preparing for saving branch \"{branch}\".")
            
            cmd = cmdStub + ['-n', branch]
            dirs = []

            graftArray = self.__getGrafts(branch)
            for key in graftArray.keys():
                cmd.append('--graft')
                cmd.append(f"{key}={graftArray[key]}")
                dirs.append(key)
            
            cmd = cmd + dirs
            if self.debug:
                print('Bup save command line:', cmd)
            
            if self.dry:
                print(f'Saving bup for branch "{branch}".')
            else:
                subprocess.run(
                    cmd
                ).check_returncode()

    def __getAllBranches(self):
        branches = [row.branch for row in self.config.table]
        return set(branches)
    
    def __getGrafts(self, branch):
        ret = {}
        
        for index in range(0, len(self.config.table)):
            if self.config.table[index].branch != branch:
                continue

            destName = self.config.table[index].target
            srcName = self.workdir.getWorkingPath(index)

            ret[srcName] = destName
        
        return ret
