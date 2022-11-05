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
import re

class ConfigHelper:
    def __init__(self, config: bup_backup.config.BackupConfig):
        self.config = config

    def getOption(self, index: int, param: str, fallback = None):
        return self.config.table[index].options.get(param, self.config.common.get(param, fallback))

    def getParsedSize(self, str):
        pattern = '([0-9,.]+)([kKmMgGtT]?)'
        expression = re.compile(pattern)
        match = expression.fullmatch(str)

        mantis = match.group(1).replace(',', '.')
        unit = match.group(2)

        number = float(mantis)
        unitMap = {
            'k': 1024,
            'm': 1024*1024,
            'g': 1024*1024*1024,
            't': 1024*1024*1024*1024
        }
        # print(number, mantis, unit, unitMap[unit.lower()])
        return number * unitMap[unit.lower()]
