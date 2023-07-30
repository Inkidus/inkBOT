# inkBOT
A simple discord bot


## Functions
Includes a version of FreeGameFormat recreated in Python, text to speech and audio playback for voice channels, dice rolls and coinflips, as well as a chatbot and image generator using OpenAI's API (provide your own API key).


## Installation
Download and extract the zip file. Add your own API keys to keys.env. In keys.env, also set the channel(s) you would like the free game formatter to output to as well as the users you would like to have access to that command. Depending on the number of channels, the free_game_channels and free_game_ids portion in main.py may have to be updated.

Some additional libraries are required in order to run this bot. Please install the following in order to ensure proper operation: discord.py, openai, requests, datetime, asyncio, pyttsx3, random, yt-dlp, PyYAML, python-dotenv, tiktoken

To obtain a discord API key, please see the following page: https://discordpy.readthedocs.io/en/stable/discord.html

Temporarily free games can be input by creating a file named toShareFreebies.txt in the same directory as main.py. Modify it with the following format:

Store Name 1:

GameName: GameURL

GameName: GameURL

...

Store Name 2:

...



## Usage
Run the main.py file (Python 3). A log file named storedLogs.txt will be created in the same directory as main.py to track usage. Additional files will be created in order to store history, wikipedia information, sessions, the google tts character count.