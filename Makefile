SHELL := /bin/bash
PYTHON ?= python3

.PHONY: up down iocs testdata load test all
up:
	docker compose up -d --wait --wait-timeout 900
	bash scripts/wait_for_splunk.sh

down:
	docker compose down

iocs:
	$(PYTHON) scripts/build_iocs.py

testdata:
	$(PYTHON) scripts/generate_test_data.py

load:
	bash scripts/load_test_data.sh

test:
	$(PYTHON) tests/run_tests.py

# Recursive calls preserve ordering even when make is invoked with -j.
all:
	$(MAKE) up
	$(MAKE) iocs
	$(MAKE) testdata
	$(MAKE) load
	$(MAKE) test
