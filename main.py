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
chat4Histories = OrderedDict()
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
client = discord.Client(intents=intents, status=discord.Status.online, activity=discord.Game(name="with MultiVAC"))

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

	elif message.content.lower().startswith('inkbot: roll') or message.content.lower().startswith('inkbot: dice'):
		await client.change_presence(status=discord.Status.dnd, activity=discord.Game('thinking...'))
		await dicePost(message)
		await client.change_presence(status=discord.Status.online, activity=discord.Game(name="with MultiVAC"))
	elif message.content.lower() == 'inkbot: coin' or message.content.lower() == 'inkbot: coinflip' or message.content.lower() == 'inkbot: flipcoin':
		await client.change_presence(status=discord.Status.dnd, activity=discord.Game('thinking...'))
		await coinPost(message)
		await client.change_presence(status=discord.Status.online, activity=discord.Game(name="with MultiVAC"))
		
	elif message.content.lower() == 'send free games' and message.author.id == free_game_ids:
		await client.change_presence(status=discord.Status.dnd, activity=discord.Game('thinking...'))
		await freeGamesPost(message, client, free_game_channels)
		await client.change_presence(status=discord.Status.online, activity=discord.Game(name="with MultiVAC"))
		
	elif message.content.lower().startswith('inkbot: help'):
		await client.change_presence(status=discord.Status.dnd, activity=discord.Game('thinking...'))
		await helpPost(message)
		await client.change_presence(status=discord.Status.online, activity=discord.Game(name="with MultiVAC"))
		
	elif message.content.lower() == 'inkbot: join':
		await client.change_presence(status=discord.Status.dnd, activity=discord.Game('thinking...'))
		await vcJoin(message)
		await client.change_presence(status=discord.Status.online, activity=discord.Game(name="with MultiVAC"))
	elif message.content.lower() == 'inkbot: leave':
		await client.change_presence(status=discord.Status.dnd, activity=discord.Game('thinking...'))
		await vcLeave(message)
		await client.change_presence(status=discord.Status.online, activity=discord.Game(name="with MultiVAC"))
	elif message.content.lower().startswith('inkbot: tts'):
		await client.change_presence(status=discord.Status.dnd, activity=discord.Game('thinking...'))
		await ttsSpeak(message)
		await client.change_presence(status=discord.Status.online, activity=discord.Game(name="with MultiVAC"))
	elif message.content.lower().startswith('inkbot: play'):
		await mediaPlay(message)
	elif message.content.lower().startswith('inkbot: playAlternative'):
		await mediaPlayAlternative(message)
		
	elif message.content.lower().startswith('inkbot: draw'):
		await client.change_presence(status=discord.Status.dnd, activity=discord.Game('thinking...'))
		await dallePost(message)
		await client.change_presence(status=discord.Status.online, activity=discord.Game(name="with MultiVAC"))
		
	elif message.content.lower().startswith('inkbot: forget'):
		await client.change_presence(status=discord.Status.dnd, activity=discord.Game('thinking...'))
		await chatForget(message, chatHistories)
		await client.change_presence(status=discord.Status.online, activity=discord.Game(name="with MultiVAC"))
	elif message.content.lower().startswith('inkbot: become'):
		await client.change_presence(status=discord.Status.dnd, activity=discord.Game('thinking...'))
		await chatBecome(message, chatHistories)
		await client.change_presence(status=discord.Status.online, activity=discord.Game(name="with MultiVAC"))
	elif message.content.lower().startswith('inkbot: select'):
		await client.change_presence(status=discord.Status.dnd, activity=discord.Game('thinking...'))
		await chatSelect(message, chatHistories)
		await client.change_presence(status=discord.Status.online, activity=discord.Game(name="with MultiVAC"))
	elif message.content.lower().startswith('inkbot,') or message.content.lower().startswith('dinklebot,'):
		await client.change_presence(status=discord.Status.dnd, activity=discord.Game('thinking...'))
		await chatPost(message, chatHistories, defaultHistoryEntry, "gpt-3.5-turbo")
		await client.change_presence(status=discord.Status.online, activity=discord.Game(name="with MultiVAC"))
		
	elif message.content.lower().startswith('inkbot4: forget'):
		await client.change_presence(status=discord.Status.dnd, activity=discord.Game('thinking...'))
		await chatForget(message, chat4Histories)
		await client.change_presence(status=discord.Status.online, activity=discord.Game(name="with MultiVAC"))
	elif message.content.lower().startswith('inkbot4: become'):
		await client.change_presence(status=discord.Status.dnd, activity=discord.Game('thinking...'))
		await chatBecome(message, chat4Histories)
		await client.change_presence(status=discord.Status.online, activity=discord.Game(name="with MultiVAC"))
	elif message.content.lower().startswith('inkbot4: select'):
		await client.change_presence(status=discord.Status.dnd, activity=discord.Game('thinking...'))
		await chatSelect(message, chat4Histories)
		await client.change_presence(status=discord.Status.online, activity=discord.Game(name="with MultiVAC"))
	elif message.content.lower().startswith('inkbot4,') or message.content.lower().startswith('dinklebot4,'):
		await client.change_presence(status=discord.Status.dnd, activity=discord.Game('thinking...'))
		await chatPost(message, chat4Histories, defaultHistoryEntry, "gpt-4")
		await client.change_presence(status=discord.Status.online, activity=discord.Game(name="with MultiVAC"))


# Start bot
client.run(DISCORD_TOKEN)