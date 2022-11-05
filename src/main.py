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
import time
import math

def main():
    cli = bup_backup.cli.Cli()
    cli.processArgs()

    if cli.isShowDebug():
        args = cli.getRawArgs()
        print(args)

    parser = bup_backup.config.BackupConfigParser(cli.getConfigPath(), cli.isShowDebug())
    config = bup_backup.config.BackupConfig()
    parser.parseCommonConfig(cli.getCommonConfigName(), config)
    parser.parseConfigTable(cli.getTableName(), config)
    
    if cli.isShowDebug():
        print('Total configuration', config.__dict__)
    
    helperMap = {
        'plain': bup_backup.helpers.PlainProcessingHelper(config),
        'lvm': bup_backup.helpers.LVMProcessingHelper(config),
        'crypt': bup_backup.helpers.LVMProcessingHelper(config),
        'lvm+crypt': bup_backup.helpers.LVMCryptProcessingHelper(config),
        'command': bup_backup.helpers.CommandProcessingHelper(config),
    }

    for index in range(0, len(config.table)):
        helper = helperMap[config.table[index].type]
        
        if cli.isVerbose():
            print(f'Checking entry {index} in table: {config.table[index].source}')
        helper.checkConfig(index)
    
    if cli.isVerbose():
        print('Finished the checks. Starting backup process.')
    
    tic = time.monotonic()

    for index in range(0, len(config.table)):
        helper = helperMap[config.table[index].type]

        if cli.isVerbose():
            print(f"Backing up {config.table[index].source} started.")
        
        helper.execute(index)

        if cli.isVerbose():
            print(f"Backup step completed.")
    
    toc = time.monotonic()

    if cli.isVerbose():
        delta = toc - tic
        tictocMinutes = math.floor(delta / 60)
        tictocSeconds = delta - tictocMinutes * 60
        tictocHours = math.floor(tictocMinutes / 60)
        tictocMinutes = tictocMinutes - 60 * tictocHours
        
        tictoc = f"{tictocSeconds:3.1f}s"
        if tictocMinutes > 0:
            tictoc = f"{tictocMinutes}min {tictoc}"
        if tictocHours > 0:
            tictoc = f"{tictocHours}h {tictoc}"
        
        print(f"Finished processing the backups in {tictoc}")
    

if __name__ == '__main__':
    main()
