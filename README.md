## Backup and restore python script for elasticdump 

These scripts inspired by:
https://github.com/import-io/es-backup-scripts

## requirement
sudo npm install -g elasticdump

## How to backup
If Elastic Search is running on your local machine and the default port (9200), you can just run it like this:

    python backup.py myindex

If you need a different host, you can do this:

    python backup.py myindex eshost

If you also need a different port, you can do this:

    python backup.py myindex eshost esport

This will generate a file called (myindex).tar.gz You only need this file - its all contained.


## How to restore
Copy the (myindex).tar.gz to whatever server you want to run it on.

Options are the same as for the backup script. To restore on default host:

    python restore.py myindex

Non default host:

    python restore.py myindex eshost

Non default port too:

    python restore.py myindex eshost esport


