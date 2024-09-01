

# TasksListsBot

This Telegram bot is used to manage multiple tasks lists within Telegram chats.

It is based on [pyTelegramBotAPI](https://github.com/eternnoir/pyTelegramBotAPI"), a Python interface for the [Telegram Bot API](https://core.telegram.org/bots/api).

**Try it in Telegram**: [TasksListsBot](https://t.me/TasksListsBot)


## Usage

To run your own instance of this bot you must first [register a new Telegram bot](https://core.telegram.org/bots#6-botfather). Once you have a token for your bot, you may proceed with options 1 or 2.


### Option 1: Manual execution

First, you have to create the necessary environment variables:
  - `BOT_TOKEN`: The token you obtained in the previous step.
  - `DATA_DIR_PATH`: The path for the data directory.

After that, you only need to execute the following terminal command:

```Bash
python ./tasks_lists_bot.py
```

This will run the bot attached to your current terminal. If you want it to stay in the background you will need to have a look at tools like [`tmux`](https://github.com/tmux/tmux).


### Option 2: Docker container (recommended)

First, you have to create a ".env" file in the repository root with the following format:

```
DATA_DIR_PATH=pat_to_the_data_directory
BOT_TOKEN=your_bot_token_here
```

You can now run the bot with a single `docker` command:

```Bash
docker compose up -d --build
```

This will run the bot as a Docker container in the background.
