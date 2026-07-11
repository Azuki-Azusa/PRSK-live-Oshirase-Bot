IMAGE_NAME = prsk-bot:local
COMPOSE = docker compose

.PHONY: build up down restart logs shell test clean

build:
	$(COMPOSE) build

up:
	$(COMPOSE) up -d

down:
	$(COMPOSE) down

restart: down up

logs:
	$(COMPOSE) logs -f app

shell:
	$(COMPOSE) run --rm app bash

test:
	python -m unittest discover -s tests -v

clean:
	$(COMPOSE) down --remove-orphans