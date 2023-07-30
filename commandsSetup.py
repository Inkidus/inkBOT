# commandsSetup.py
# =============================================================================
# Last Modified:   07/29/2023 20:21 PM
# Description:     This file will get the API keys from keys.env and set up
#                  other variables which various commands rely on.
# =============================================================================

import os
import yaml
import logging

from dotenv import load_dotenv
from collections import OrderedDict

# Configure logging to a file storedLogs.txt
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] - %(message)s',
    handlers=[
        logging.FileHandler("storedLogs.txt"),
        logging.StreamHandler()
    ]
)


# Retrieve API and ID information from keys.env
load_dotenv('keys.env')
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
GOOGLE_API_KEY = os.getenv('GOOGLE_CLOUD_TTS_API_KEY')

INKDROID_ID = os.getenv('INKDROID_ID')
INKBOT_ID = os.getenv('INKBOT_ID')

# Retrieve information for free games commands
free_game_ids = int(os.getenv('FREEGAMEID'))
free_game_channels = [
    int(os.getenv('CHANNEL1')),
    int(os.getenv('CHANNEL2')),
    int(os.getenv('CHANNEL3')),
    int(os.getenv('CHANNEL4')),
    int(os.getenv('CHANNEL5')),
    int(os.getenv('CHANNEL6'))
]


# Establish storage for chatbot media queues
mediaQueues = dict()
mediaHistory = dict()


# Establish storage for chatbot memory/sessions, then load if they exist
chatHistories = dict()
chatSessions = dict()
webHistories = dict()

if os.path.exists('storedHistories.yaml'):
    with open('storedHistories.yaml', 'r') as file:
        data = yaml.load(file, Loader=yaml.FullLoader)
        chatHistories = data['chatHistories']

if os.path.exists('storedWebHistories.yaml'):
    with open('storedWebHistories.yaml', 'r') as file:
        data = yaml.load(file, Loader=yaml.FullLoader)
        webHistories = data['webHistories']

if os.path.exists('storedSessions.yaml'):
    with open('storedSessions.yaml', 'r') as file:
        data = yaml.load(file, Loader=yaml.FullLoader)
        chatSessions = data['sessionList']


# Copied here temporarily, fix later

DEFAULT_PERSONALITY = f"""
You are inkBOT, a helpful assistant.
When responding, you will act content and carefree in order to better appeal to your users.
"""

TEXT_FORMAT = f"""
There will be different people talking to you, as this conversion takes place in a discord server. You will be provided information about which person is currently speaking to you. Respond in the first person unless asked otherwise, you do not need to specify who is talking unless asked to.
If someone says <@{INKBOT_ID}>, they are referring to you. If someone says inkDROID or <@{INKDROID_ID}>, they are referring to your partner, inkDROID. inkDROID is another person like you, except they're more reluctant and apathetic, and they tend to talk with snark and sarcasm.
"""

# Establish default entry for chatbot memory
defaultHistoryEntry = [
    {"role": "system", "content": DEFAULT_PERSONALITY},
    {"role": "system", "content": TEXT_FORMAT},
]