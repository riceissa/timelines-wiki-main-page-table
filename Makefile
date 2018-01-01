.PHONY: all
all: table.mediawiki

table.mediawiki:
	./proc.py > "$@"

ga.csv:
	./HelloAnalytics.py > $@

.PHONY: clean
clean:
	rm -f table.mediawiki ga.csv
