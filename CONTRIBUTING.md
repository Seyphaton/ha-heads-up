# Contributing

## Run the tests

1. Install [uv](https://docs.astral.sh/uv/).
2. Install Node 22 (for the card tests).
3. Run `make setup`.
4. Run `make check`. It runs lint, types, pytest, docs checks and the card tests (`make test-card`).

## Report a bug

Open an issue with the bug report template. Include:

- Home Assistant version
- Heads Up version
- The action call or card configuration that shows the problem
- Log lines from `custom_components.heads_up`
