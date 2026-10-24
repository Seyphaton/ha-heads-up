.PHONY: setup test lint format typecheck hassfest docs-check check dev-up dev-down dev-reset dev-logs

COMPOSE = docker compose -f dev/docker-compose.yml

setup:          ## install Python 3.14 venv and dev dependencies
	uv sync

test:           ## run pytest (pass ARGS="-k name" for a single test)
	uv run pytest $(ARGS)

lint:           ## ruff lint + format check
	uv run ruff check .
	uv run ruff format --check .

format:
	uv run ruff format .
	uv run ruff check --fix .

typecheck:
	uv run mypy

hassfest:       ## validate manifest/translations with HA's hassfest image
	docker run --rm -v "$(CURDIR)":/github/workspace ghcr.io/home-assistant/hassfest

docs-check:     ## banned words, placeholders, example validation, field parity
	uv run python scripts/docs_check.py

check: lint typecheck test docs-check

dev-up:         ## start local throwaway HA on http://127.0.0.1:8124
	$(COMPOSE) up -d

dev-down:
	$(COMPOSE) down

dev-reset:      ## stop and delete dev HA runtime state (keeps configuration.yaml)
	$(COMPOSE) down
	cd dev/ha-config && rm -rf .storage home-assistant_v2.db* home-assistant.log* .HA_VERSION deps tts blueprints

dev-logs:
	$(COMPOSE) logs -f homeassistant
