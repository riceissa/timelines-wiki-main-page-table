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

# Normally doing `explorer.exe .` does not require the &, but for some reason
# within a script, not having the & will just end the script right here.
# Possibly because we set -e above.
explorer.exe . &

# Turn off command echoing because the rest are just echo commands
set +x

echo -e "\n\nOpen the file table.mediawiki using a text editor."
read -p "Press enter to continue"

echo -e "\n\nUpdate https://timelines.issarice.com/wiki/User:Issa/Main_page_automated with the contents of table.mediawiki" | fold -w 70 -s
read -p "Press enter to continue"

echo -e "\n\nUpdate the last generated date on https://timelines.issarice.com/wiki/Main_Page" | fold -w 70 -s
read -p "Press enter to continue"

echo -e "\n\nMessage Vipul saying I have updated the front page" | fold -w 70 -s
read -p "Press enter to continue"

echo -e "\n\nIn org mode, update the scheduled timestamp to be the first day of the next month." | fold -w 70 -s
read -p "Press enter to continue"

echo -e "\n\nDone!"
