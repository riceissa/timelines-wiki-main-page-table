.PHONY: all
all: table.mediawiki

table.mediawiki:
	./proc.py > front_page_table_data.csv
	./print_table.py > "$@"

ga.csv:
	./HelloAnalytics.py > $@

.PHONY: clean
clean:
	rm -f table.mediawiki ga.csv front_page_table_data.csv
