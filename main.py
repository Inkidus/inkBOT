from functions import *

# Configure logging to a file inkbot_logs.txt
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] - %(message)s',
    handlers=[
        logging.FileHandler("inkbot_logs.txt"),
        logging.StreamHandler()
    ]
)

# Retrieve API and ID information from values.env
load_dotenv('values.env')
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
openai.api_key = OPENAI_API_KEY
free_game_ids = int(os.getenv('FREEGAMEID'))
free_game_channels = [
    int(os.getenv('CHANNEL1')),
    int(os.getenv('CHANNEL2')),
    int(os.getenv('CHANNEL3')),
    int(os.getenv('CHANNEL4')),
    int(os.getenv('CHANNEL5')),
    int(os.getenv('CHANNEL6'))
]

# Establish a default chatbot memory and the default contents for each channel
chatHistories = OrderedDict()
defaultHistoryEntry = [
    {"role": "system", "content": DEFAULT_PERSONALITY},
    {"role": "system", "content": TEXT_FORMAT},
]

# Configure bot intents
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.typing = False
intents.presences = False
client = discord.Client(intents=intents)

# Set bot prefix
bot = commands.Bot(command_prefix=':', intents=intents)

# Establish behavior for when the bot is ready
@client.event
async def on_ready():
    logging.info(f"Successfully logged in as {client.user}\n")

# Establish behavior for when the bot receives a message, run corresponding function depending on contents and author
@client.event
async def on_message(message):
    if message.author == client.user:
        return
    elif message.content.lower() == 'send free games' and message.author.id == free_game_ids:
        await freeGamesPost(message, client, free_game_channels)
    elif message.content.lower().startswith('inkbot: help'):
        await helpPost(message)
    elif message.content.lower() == 'inkbot: join':
        await vcJoin(message)
    elif message.content.lower() == 'inkbot: leave':
        await vcLeave(message)
    elif message.content.lower().startswith('inkbot: tts'):
        await ttsSpeak(message)
    elif message.content.lower().startswith('inkbot: forget'):
        await chatForget(message, chatHistories)
    elif message.content.lower().startswith('inkbot: become'):
        await chatBecome(message, chatHistories)
    elif message.content.lower().startswith('inkbot: draw'):
        await dallePost(message)
    elif message.content.lower().startswith('inkbot,') or message.content.lower().startswith('dinklebot,'):
        await chatPost(message, chatHistories, defaultHistoryEntry)


# Start bot
client.run(DISCORD_TOKEN)