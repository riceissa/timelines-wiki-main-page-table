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

- (manual) update https://timelines.issarice.com/wiki/User:Issa/Main_page_automated with
  the contents of `table.mediawiki`

- (manual) update the last generated date on https://timelines.issarice.com/wiki/Main_Page

## See also

- https://github.com/riceissa/analytics-table
