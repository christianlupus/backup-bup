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
from ..config_helper import ConfigHelper
from ..workdir import Workdir
from ..rsync_helper import RSyncHelper
from .middleware import Middleware

import re

class MiddlewareRunner:
    def __init__(
        self,
        middlewareList: list[Middleware],
        config: bup_backup.config.BackupConfig,
        configHelper: ConfigHelper,
        workdir: Workdir,
        dry, verbose, debug
    ):
        self.middlewareList = middlewareList
        self.configHelper = configHelper
        self.workdir = workdir
        self.config = config

        self.dry = dry
        self.verbose = verbose
        self.debug = debug

        self.states = {}
        self.rsync = RSyncHelper(self.config)

    def __prepareStateStructure(self, index):
        if index not in self.states.keys():
            # We need to initialize the structure
            self.states[index] = [None for x in self.middlewareList]

    def __isRunningInPlace(self, index):
        return self.configHelper.getOption(index, 'mount_inplace')

    def prepareBackup(self, index, tableLine: bup_backup.config.BackupTableRow):
        self.__prepareStateStructure(index)
        inPlace = self.__isRunningInPlace(index)
        indexRange = range(len(self.middlewareList))

        # Run the preparation steps
        middleware: Middleware
        for i in indexRange:
            middleware = self.middlewareList[i]
            self.states[index][i] = (None, middleware.prepare(index))
        
        # Run the middleware tasks in forward order for the before tasks
        for i in indexRange:
            middleware = self.middlewareList[i]

            state = self.states[index][i][1]
            if i == 0:
                source = tableLine.source
            else:
                source = self.states[index][i-1][0]
            
            (dest, newState) = middleware.beforeStep(index, source, inPlace, state)

            self.states[index][i] = (dest, newState)
        
        # All preparation steps have been done.

        if not inPlace:
            # First, the sync to the work folder need to be carried out
            lastStoredLocation = self.states[index][-1][0]
            dest = self.workdir.getWorkingPath(index)

            if self.verbose:
                print('Copying data from temporary location to final workdir')

            currentTarget = tableLine.target
            while currentTarget.endswith('/'):
                currentTarget = currentTarget[0:-1]
            regex = re.compile(f'{currentTarget}(/.+)')

            protectedPaths = []
            for line in self.config.table:
                if line.branch != tableLine.branch:
                    continue
                match = regex.match(line.target)
                if match is not None:
                    protectedPaths.append(match.group(1))
                

            self.rsync.execute(
                index=index,
                source=lastStoredLocation,
                dest=dest,
                verbose=self.verbose, dry=self.dry, debug=self.debug,
                protectedDirs=protectedPaths
            )

            if self.verbose:
                print('Data is synchronized. Closing temporary steps.')
            
            # We need to run the closing steps of the middlewares in revered order
            self.__cleanUpMiddlewares(index)

    def __cleanUpMiddlewares(self, index):
        indexRange = range(len(self.middlewareList))
        for i in reversed(indexRange):
            middleware: Middleware
            middleware = self.middlewareList[i]

            (dest, state) = self.states[index][i]
            middleware.afterStep(dest=dest, state=state)

    def cleanUpAfterBackup(self, index):
        if self.__isRunningInPlace(index):
            self.__cleanUpMiddlewares(index)
        else:
            if self.verbose:
                print('Nothing to be done in clean up script for in-place jobs.')
