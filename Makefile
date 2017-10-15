.PHONY: all
all: table.mediawiki

table.mediawiki:
	./proc.py > "$@"

.PHONY: clean
clean:
	rm -f table.mediawiki
