PYTHON ?= python3

up:
	docker compose up -d

down:
	docker compose down

install:
	$(PYTHON) -m pip install -r requirements.txt

seed:
	$(PYTHON) scripts/seed_data.py

indexes:
	$(PYTHON) scripts/create_indexes.py

demo:
	$(PYTHON) scripts/demo_queries.py

smoke:
	$(PYTHON) scripts/smoke_check.py

reset:
	$(PYTHON) scripts/seed_data.py --drop-existing
