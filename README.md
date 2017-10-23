# Timelines Wiki main page table update script

This is the script that prints the table seen at
<https://timelines.issarice.com/wiki/Main_Page>.

Steps:

- Re-run google analytics script to get a new `ga.csv`
- git pull from vipul's contract work repo, then re-read the `tasks.sql` file,
  to get new payments info
- Re-run `proc.py`. The wikipedia pageviews fetching is included in this.
