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

    sorter = bup_backup.config.BackupConfigSorter()
    config = sorter.sort(config)
    
    if cli.isShowDebug():
        print('Total configuration', config.__dict__)
    
    bup = bup_backup.bup.Bup(config, verbose=cli.isVerbose(), dry=cli.isDryRun(), debug=cli.isShowDebug())
    workDir = bup_backup.helpers.workdir.Workdir(config)

    bup.check()

    helperMap = {
        'plain': bup_backup.helpers.PlainProcessingHelper(config, dryRun=cli.isDryRun(), verbose=cli.isVerbose(), debug=cli.isShowDebug()),
        'command': bup_backup.helpers.CommandProcessingHelper(config, dryRun=cli.isDryRun(), verbose=cli.isVerbose(), debug=cli.isShowDebug()),
        'lvm': bup_backup.helpers.LVMProcessingHelper(config, dryRun=cli.isDryRun(), verbose=cli.isVerbose(), debug=cli.isShowDebug()),
        # 'crypt': bup_backup.helpers.LVMProcessingHelper(config, dryRun=cli.isDryRun(), verbose=cli.isVerbose(), debug=cli.isShowDebug()),
        'lvm+crypt': bup_backup.helpers.LVMCryptProcessingHelper(config, dryRun=cli.isDryRun(), verbose=cli.isVerbose(), debug=cli.isShowDebug()),
    }

    for index in range(0, len(config.table)):
        helper = helperMap[config.table[index].type]
        
        if cli.isVerbose():
            print(f'Checking entry {index} in table: {config.table[index].source}')
        helper.checkConfig(index)
    
    lvmSizeChecker = bup_backup.helpers.LvmConfigChecker(config)
    lvmSizeChecker.checkFreeSpace()

    if cli.isVerbose():
        print('Finished the checks. Starting backup preparations.')
    
    tic = time.monotonic()

    for index in range(0, len(config.table)):
        helper = helperMap[config.table[index].type]

        if cli.isVerbose():
            print(f"Prepare step for backing up {config.table[index].source}.")
        
        helper.prepareBackup(index)

        if cli.isVerbose():
            print(f"Backup preparation step for {config.table[index].source} completed.")
    
    if cli.isVerbose():
        print('Starting bup backup process.')
    
    workPath = workDir.getWorkingBasePath()
    bup.index(workPath)
    bup.save(workPath)

    if cli.isVerbose():
        print('Finished bup backup process. Cleaning up backup work now.')

    for index in range(0, len(config.table)):
        helper = helperMap[config.table[index].type]

        if cli.isVerbose():
            print(f"Clean up after backing up {config.table[index].source}.")
        
        helper.cleanUpBackup(index)

        if cli.isVerbose():
            print(f"Cleanup step for {config.table[index].source} completed.")
    
    bup.finishBackup()
    
    if cli.isVerbose():
        print('Finished clean up.')


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
