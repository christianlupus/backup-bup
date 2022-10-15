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

import argparse

class Cli:
    def __init__(self):
        self.args = None

    def processArgs(self):
        parser = argparse.ArgumentParser()

        parser.add_argument('-c', '--config', help='Set the config folder for the backup process', nargs=1, default=['/etc/bup-backup'])
        parser.add_argument('--common', help='Set the file name for the common configuration file', default=['common.conf'])
        parser.add_argument('-t', '--table', help='Set the table name to parse for backup tasks', default=['backup.table'])
        parser.add_argument('-v', '--verbose', help='Be verbose about the tasks involved', action='store_true')
        parser.add_argument('-n', '--dry-run', help='Do not carry out any modifications but only print what would have been done', action='store_true')
        parser.add_argument('--debug', help='Print out some debugging information', action='store_true')

        self.args = parser.parse_args()
    
    def getRawArgs(self):
        return self.args
    
    def getConfigPath(self):
        return self.args.config[0]
    
    def getCommonConfigName(self):
        return self.args.common[0]

    def getTableName(self):
        return self.args.table[0]
    
    def isVerbose(self):
        return self.args.verbose
    
    def isDryRun(self):
        return self.args.dry_run
    
    def isShowDebug(self):
        return self.args.debug
