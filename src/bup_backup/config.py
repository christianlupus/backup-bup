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
import re

class BackupTableRow:
    def __init__(self, source, branch, target, type, options = []):
        self.source = source
        self.branch = branch
        self.target = target
        self.type = type
        self.options = options
    
    def __repr__(self):
        return f"BackupLine({self.source} to {self.branch}:{self.target} as {self.type} with {self.options})"

class BackupConfig:
    def __init__(self):
        self.common = {}
        self.common['bup'] = 'bup'
        self.common['snap_size'] = '1g'
        self.common['snap_name'] = 'snap-backup'
        self.common['decrypt_name'] = 'snap-backup-decrypted'
        self.common['mount_base'] = '/run/bup-backup/mnt'
        self.common['mount_inplace'] = False

        self.table: list[BackupTableRow] = []

class BackupConfigParser:
    def __init__(self, configPath = '/etc/bup-backup', debug=False):
        self.configPath = configPath
        self.debug = debug
    
    def __readConfigLines(self, name):
        filename = os.path.join(self.configPath, name)
        with open(filename, 'r') as fp:
            lines = fp.readlines()
        
        lines = [x.strip() for x in lines if x.strip() != '' and not x.strip().startswith('#')]

        if self.debug:
            print('Read effective lines from configuration file:')
            print(lines)

        return lines

    def parseCommonConfig(self, name, config):
        lines = self.__readConfigLines(name)
        for line in lines:
            parts = line.split('=', 2)
            if len(parts) == 2:
                key = parts[0].strip()
                value = parts[1].strip()
                config.common[key] = value
        
        # if self.debug:
        #     print('Common configuration:')
        #     print(config.__dict__)
        
    def __readTableColumn(self, line):
        pattern = '([^ \\t\\\\]|\\\\ )+'
        expr = re.compile(pattern)
        match = expr.match(line)
        matchedString = match.group(0)
        rest = line[match.end(0):]
        return (matchedString, rest)

    def __skipTableSeparator(self, line):
        pattern = '[\\t ]+'
        expr = re.compile(pattern)
        match = expr.match(line)
        return line[match.end(0):]
    
    def __parseAdditionalOptionsField(self, options):
        if options == 'none':
            return {}
        
        opts = options.split(',')
        ret = {}
        for o in opts:
            parts = o.split('=', 2)
            if len(parts) == 2:
                ret[parts[0]] = parts[1]
            elif len(parts) == 1:
                ret[o] = True
        return ret

    def parseConfigTable(self, name, config):
        lines = self.__readConfigLines(name)
        for line in lines:
            source, rest = self.__readTableColumn(line)
            rest = self.__skipTableSeparator(rest)
            branch, rest = self.__readTableColumn(rest)
            rest = self.__skipTableSeparator(rest)
            target, rest = self.__readTableColumn(rest)
            rest = self.__skipTableSeparator(rest)
            type, rest = self.__readTableColumn(rest)
            rest = rest.strip()
            if len(rest) > 0:
                options = rest
            else:
                options = 'none'
            
            if target == '-':
                target = source

            options = self.__parseAdditionalOptionsField(options)

            lineOptions = BackupTableRow(source, branch, target, type, options)
            
            if self.debug:
                print('Parsed config table line:', lineOptions)
            
            config.table.append(lineOptions)
            
