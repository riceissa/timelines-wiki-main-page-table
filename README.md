# Timelines Wiki main page table update script

This is the script that prints the table seen at
<https://timelines.issarice.com/wiki/Main_Page>.

Steps:

- `make clean`
- `make ga.csv`: Re-run google analytics script to get a new `ga.csv`
- (manual) git pull from Vipul's contract work repo, then re-read the `tasks.sql` file,
  to get new payments info

  ```bash
  # from the contractwork directory
  git up
  mysql contractwork -e "drop table if exists tasks"
  mysql contractwork < sql/tasks.sql
  ```

- `make table.mediawiki`: Re-run `proc.py`. The Wikipedia pageviews fetching is included in this.
  **Important**: If this step crashes, you should re-run `proc.py` manually
  (look inside the `Makefile` for the line that uses `proc.py` to see what
  command you should run)
  instead of running `make`. Otherwise the previous month's pageviews data will
  be overwritten by the blank new data file!

- (manual) Make sure `table.mediawiki` file does not exist on my Desktop.

- Run
  
  ```
  cp table.mediawiki /mnt/c/Users/Issa/Desktop/
  ```
  
  to copy the newly-generated `table.mediawiki` file out of WSL and into Windows's Desktop.

- (manual) update https://timelines.issarice.com/wiki/User:Issa/Main_page_automated with
  the contents of `table.mediawiki`

- (manual) update the last generated date on https://timelines.issarice.com/wiki/Main_Page

- (manual) message Vipul saying I have updated the front page

- (manual) Delete the file `table.mediawiki` from the Windows Desktop.

- (manual) in org mode, update the scheduled timestamp to be the first day of the next month.

## See also

- https://github.com/riceissa/analytics-table
