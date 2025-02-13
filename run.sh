#!/bin/bash
set -euxo pipefail

git remote update -p && git merge --ff-only @{u}

thisdir="$(pwd)"

make clean

# Re-run google analytics script to get a new `ga.csv`
make ga.csv

# git pull from Vipul's contract work repo, then re-read the `tasks.sql`
# file, to get new payments info
cd ~/projects/vipulnaik/contractwork/
git remote update -p && git merge --ff-only @{u}
make reset && make read_public

# Return to the timelines-wiki-main-page-table directory
cd "$thisdir"

# Re-run `proc.py`. The Wikipedia pageviews fetching is included in this.
make table.mediawiki

explorer.exe .

echo "Open the file table.mediawiki using a text editor."
read -p "Press enter to continue"

echo "Update https://timelines.issarice.com/wiki/User:Issa/Main_page_automated with the contents of table.mediawiki"
read -p "Press enter to continue"

echo "Update the last generated date on https://timelines.issarice.com/wiki/Main_Page"
read -p "Press enter to continue"

echo "Message Vipul saying I have updated the front page"
read -p "Press enter to continue"

echo "In org mode, update the scheduled timestamp to be the first day of the next month."
read -p "Press enter to continue"

echo "Done!"
