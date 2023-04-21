# inkBOT
A simple discord bot


## Functions
Includes a version of FreeGameFormat recreated in Python as well as a chatbot and image generator using OpenAI's API.


## Installation
Download and extract the zip file. Add your own API keys to values.env. In values.env, also set the channel(s) you would like the free game formatter to output to as well as the users you would like to have access to that command. Depending on the number of channels, the free_game_channels and free_game_ids portion in main.py may have to be updated.

Any temporarily free games can be input by creating a file freegames.txt in the same directory as main.py. Use the following format:
Store Name 1:

GameName: GameURL

GameName: GameURL

...

Store Name 2:

...


## Usage

Run the main.py file (Python 3). A log file named inkbot_logs will be created in the same directory as main.py to track usage.