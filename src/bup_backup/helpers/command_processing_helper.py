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

import os
import stat
import re
import subprocess

class CommandProcessingHelper(AbstractProcessingHelper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def checkConfig(self, index: int):
        super().checkConfig(index, sourceMustExist=False)
        tableLine = self.config.table[index]

        cmd = self.__splitSource(tableLine.source)

        if len(cmd) == 0:
            raise ConfigurationException(f"The command '{tableLine.source}' is not valid.")
        if not os.path.isfile(cmd[0]):
            raise ConfigurationException(f"The path {cmd[0]} is no file to be executable.")
        if not os.access(cmd[0], os.X_OK):
            raise ConfigurationException(f"The file {cmd[0]} cannot be executed.")

    def __splitSource(self, source):
        regex = re.compile('\\\\ ')
        cmd = regex.split(source)
        return cmd

    def prepareBackup(self, index):
        if self.verbose:
            print(f"Extracting the command output from {self.config.table[index].source}.")

        cmd = self.__splitSource(self.config.table[index].source)
        
        if self.debug:
            print('Cmd', cmd)
        
        workdir = self.workdirHelper.ensureWorkingPathExists(index, self.dryRun, emptyDir=True)

        if self.dryRun:
            print('Executed command', self.config.table[index].source)
        else:
            # Make sure the folder is not readable by anyone except root
            os.chmod(workdir, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
            
            subprocess.run(
                cmd,
                cwd=workdir,
            ).check_returncode()

    def cleanUpBackup(self, index):
        # There is nothing to be done here.
        pass
