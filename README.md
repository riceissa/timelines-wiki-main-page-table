# Timelines Wiki main page table update script

This is the script that prints the table seen at
<https://timelines.issarice.com/wiki/Main_Page>.

To update the main page table, simply run from the shell:

```bash
./run.sh
```

Note that this script is not yet fully automated, so at certain times
it will prompt you to do something manually.

## Dependencies

```bash
pip3 install google-analytics-data
sudo dnf install mysql-connector-python3
```

## See also

- https://github.com/riceissa/analytics-table
