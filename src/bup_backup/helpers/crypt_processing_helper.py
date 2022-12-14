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

class CryptProcessingHelper(AbstractProcessingHelper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def checkConfig(self, index: int):
        super().checkConfig(index)
        tableLine = self.config.table[index]

        decryptName = self.configHelper.getOption(index, 'decrypt_name')
        if os.path.exists(os.path.join('/dev/mapper', decryptName)):
            raise ConfigurationException(f"Could not use {decryptName} as name of the decrypted device for {tableLine.source} as it exists already.")
        
        keyfile = self.configHelper.getOption(index, 'key')
        if not os.path.exists(keyfile):
            raise ConfigurationException(f"No key was given for decryption of {tableLine.source}.")
        if not os.access(keyfile, os.R_OK):
            raise ConfigurationException(f"Cannot access key file {keyfile}.")
        keyfileStat = os.stat(keyfile)
        if keyfileStat.st_size == 0:
            raise ConfigurationException(f"The key file {keyfile} has length 0.")
