# What
This is a announce discord bot for Project-Sekai(JP Server) virtual live.

This bot is using the data from [https://sekai-world.github.io/sekai-master-db-diff/virtualLives.json](https://sekai-world.github.io/sekai-master-db-diff/virtualLives.json), which is from github repository [Sekai-World](https://github.com/orgs/Sekai-World/repositories).

You can change the url in `crawler.py` if you want to use this bot for another server.

# How
## Environment
Python3~

## Install required packages

Run 
```shell
pip install -r requirements.txt
```

## Create a environment file

- Create a file named `.env`.
- Fill the file like 
```
BOT_TOKEN=[BOT_TOKEN]
CHANNEL_ID=[CHANNEL_ID]
env=production
```

## Run the bot
Run
```shell
python .\dcbot.py
```