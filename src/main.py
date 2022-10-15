import bup_backup

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

if __name__ == '__main__':
    main()
