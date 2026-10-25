.PHONY: setup test test-card lint format typecheck hassfest docs-check check dev-up dev-onboard dev-smoke dev-down dev-reset dev-logs

COMPOSE = docker compose -f dev/docker-compose.yml

setup:          ## install Python 3.14 venv and dev dependencies
	uv sync

test:           ## run pytest (pass ARGS="-k name" for a single test)
	uv run pytest $(ARGS)

test-card:      ## run vitest on the card's pure functions (needs npm install once)
	npm install --no-audit --no-fund
	npx vitest run

lint:           ## ruff lint + format check
	uv run ruff check .
	uv run ruff format --check .

format:
	uv run ruff format .
	uv run ruff check --fix .

typecheck:
	uv run mypy

hassfest:       ## validate manifest/translations with HA's hassfest image (amd64 only; emulated on arm64)
	docker run --rm --platform linux/amd64 -v "$(CURDIR)":/github/workspace ghcr.io/home-assistant/hassfest

docs-check:     ## banned words, placeholders, example validation, field parity
	uv run python scripts/docs_check.py

check: lint typecheck test docs-check test-card

dev-up:         ## start local throwaway HA on http://127.0.0.1:8124
	@test -f dev/ha-config/automations.yaml || echo '[]' > dev/ha-config/automations.yaml
	@test -f dev/ha-config/scripts.yaml || echo '{}' > dev/ha-config/scripts.yaml
	$(COMPOSE) up -d

dev-onboard:    ## first start only: onboarding, dev-admin + dev-user with persons, Heads Up entry
	uv run python dev/onboard.py

dev-smoke:      ## end-to-end check against dev HA (see dev/smoke.py; restarts the container)
	uv run python dev/smoke.py create
	$(COMPOSE) restart homeassistant
	until curl -sf -o /dev/null http://127.0.0.1:8124/manifest.json; do sleep 2; done; sleep 5
	uv run python dev/smoke.py verify
	uv run python dev/smoke.py conditions
	uv run python dev/smoke.py rules
	$(COMPOSE) restart homeassistant
	until curl -sf -o /dev/null http://127.0.0.1:8124/manifest.json; do sleep 2; done; sleep 5
	uv run python dev/smoke.py rules_verify

dev-down:
	$(COMPOSE) down

dev-reset:      ## stop and delete dev HA runtime state (keeps configuration.yaml)
	$(COMPOSE) down
	cd dev/ha-config && rm -rf .storage home-assistant_v2.db* home-assistant.log* .HA_VERSION deps tts blueprints

dev-logs:
	$(COMPOSE) logs -f homeassistant
