.PHONY: all
all: table.mediawiki

table.mediawiki:
	mv front_page_table_data.csv previous_month_front_page_table_data.csv
	./proc.py > front_page_table_data.csv
	./print_table.py > "$@"

ga.csv:
	./ga4_pageviews_fetch.py > $@

.PHONY: clean
clean:
	rm -f table.mediawiki ga.csv
