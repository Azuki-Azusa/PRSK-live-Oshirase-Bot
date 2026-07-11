# What
This is a announce discord bot for Project-Sekai(JP Server) virtual live.

This bot is using the data from [https://sekai-world.github.io/sekai-master-db-diff/virtualLives.json](https://sekai-world.github.io/sekai-master-db-diff/virtualLives.json), which is from github repository [Sekai-World](https://github.com/orgs/Sekai-World/repositories).

You can change the url in `crawler.py` if you want to use this bot for another server.

# How
## Environment
Python3.9~

## Install required packages

Run 
```shell
pip install -r requirements.txt
```

## Create a environment file

- Create a file named `.env`.
- Fill the file like 
```
BOT_TOKEN=
CHANNEL_ID_REMIND=
CHANNEL_ID_PRSK=
CHANNEL_ID_RANK=
env=production
MEMBERS=
VIRTUAL_LIVE_API=
CURRENT_EVENT_API=
GAME_API_URL=
GAME_API_PATH=
GAME_API_RANK_PATH1=
GAME_API_RANK_PATH2=
GAME_API_HEADER=
GAME_API_TOKEN=
DELAY=
```
id is the user id whose want to be mentioned

## Run the bot
Run
```shell
python .\dcbot.py
```

## Run tests

Run:
```shell
python -m unittest discover -s tests -v
```
## Docker on NAS

Build and start the bot:

```shell
docker compose build
docker compose up -d
```

Or use Makefile shortcuts:

```shell
make build
make up
make logs
make down
```

## Environment files

Use `.env` for the running container. `.env.example` documents the required keys without secrets.

`APP_ENV` is the preferred environment mode key. The old `env` key is still supported for compatibility.

## Project structure

- `config.py`: loads and validates environment configuration.
- `crawler.py`: Project Sekai API client plus compatibility wrapper functions.
- `dcbot.py`: Discord bot wiring, scheduled tasks, and command handling.
- `event.py`, `live.py`, `participation.py`, `rankLogQueue.py`: small domain objects.
- `tests/`: unit tests that do not require Discord or live network access.
