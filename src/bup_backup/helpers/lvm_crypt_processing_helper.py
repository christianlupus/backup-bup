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

from .lvm_processing_helper import LVMProcessingHelper
from .crypt_processing_helper import CryptProcessingHelper

class LVMCryptProcessingHelper(AbstractProcessingHelper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.lvmHelper = LVMProcessingHelper(*args, **kwargs)
        self.cryptoHelper = CryptProcessingHelper(*args, **kwargs)

    def checkConfig(self, index: int):
        super().checkConfig(index)
        tableLine = self.config.table[index]

        self.lvmHelper.checkConfig(index)
        self.cryptoHelper.checkConfig(index)

        #####################  TODO