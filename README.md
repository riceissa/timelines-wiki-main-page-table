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
  make reset && make read_public
  ```

- `make table.mediawiki`: Re-run `proc.py`. The Wikipedia pageviews fetching is included in this.

- Navigate to `\\wsl.localhost\Ubuntu-20.04\home\issa\projects\timelines-wiki-main-page-table` in Windows Explorer and open the file `table.mediawiki`.

- (manual) update https://timelines.issarice.com/wiki/User:Issa/Main_page_automated with
  the contents of `table.mediawiki`

- (manual) update the last generated date on https://timelines.issarice.com/wiki/Main_Page

- (manual) message Vipul saying I have updated the front page

- (manual) in org mode, update the scheduled timestamp to be the first day of the next month.

## See also

- https://github.com/riceissa/analytics-table
