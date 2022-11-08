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
from .rsync_helper import RSyncHelper

import os
import re

class PlainProcessingHelper(AbstractProcessingHelper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rsync = RSyncHelper(self.config)
    
    def checkConfig(self, index: int):
        super().checkConfig(index)
        tableLine = self.config.table[index]

        if not os.path.isdir(tableLine.source):
            raise ConfigurationException(f"Path {tableLine.source} is no folder.")
        
        self.rsync.check()
    
    def prepareBackup(self, index):
        workDir = self.workdirHelper.ensureWorkingPathExists(index, self.dryRun)

        currentTarget = self.config.table[index].target
        while currentTarget.endswith('/'):
            currentTarget = currentTarget[0:-1]
        regex = re.compile(f'{currentTarget}(/.+)')

        protectedPaths = []
        for line in self.config.table:
            if line.branch != self.config.table[index].branch:
                continue
            match = regex.match(line.target)
            if match is not None:
                protectedPaths.append(match.group(1))
        
        if self.verbose:
            print('Cloning files from plain folder')
        
        self.rsync.execute(
            index, 
            self.config.table[index].source, 
            workDir, 
            verbose=self.verbose, dry=self.dryRun, debug=self.debug,
            protectedDirs=protectedPaths
        )

    def cleanUpBackup(self, index):
        # We do not need to clean anything up here.
        pass
