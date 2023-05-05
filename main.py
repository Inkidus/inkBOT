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
mediaQueues = {}
chatSessions = set()
chat4Sessions = set()
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
bot = commands.Bot(command_prefix='$', intents=intents, status=discord.Status.online, activity=discord.Game(name="with MultiVAC"))


# Establish behavior for when the bot is ready
@bot.event
async def on_ready():
	logging.info(f"Successfully logged in as {bot.user}\n")


# Establish behavior for voice channels
@bot.event
async def on_voice_state_update(member, before, after):
    if not member.bot and (before.channel != after.channel):
        guild = member.guild
        voice_client = guild.voice_client
		
		# Leave if alone
        if voice_client and voice_client.channel == before.channel:
            await checkAlone(guild, voice_client)


# Establish behavior for when a message is sent
@bot.event
async def on_message(message):
	if message.author == bot.user:
		return
	
	elif message.content.lower().startswith('inkbot: roll') or message.content.lower().startswith('inkbot: dice'):
		await dicePost(message)
	elif message.content.lower() == 'inkbot: coin' or message.content.lower() == 'inkbot: coinflip' or message.content.lower() == 'inkbot: flipcoin':
		await coinPost(message)
		
	elif message.content.lower() == 'send free games' and message.author.id == free_game_ids:
		await freeGamesPost(message, bot, free_game_channels)
		
	elif message.content.lower().startswith('inkbot: help'):
		await helpPost(message)
		
	elif message.content.lower() == 'inkbot: join':
		await vcJoin(message)
	elif message.content.lower() == 'inkbot: leave':
		await vcLeave(message, mediaQueues)
	elif message.content.lower().startswith('inkbot: tts'):
		await bot.change_presence(status=discord.Status.dnd, activity=discord.Game('my voice'))
		await ttsSpeak(message)
		await bot.change_presence(status=discord.Status.online, activity=discord.Game(name="with MultiVAC"))
	elif message.content.lower().startswith('inkbot: play'):
		await bot.change_presence(status=discord.Status.dnd, activity=discord.Game('with music'))
		await mediaAdd(message, mediaQueues)
		await bot.change_presence(status=discord.Status.online, activity=discord.Game(name="with MultiVAC"))
	elif message.content.lower() == 'inkbot: pause':
		await mediaPause(message)
	elif message.content.lower() == 'inkbot: resume':
		await mediaResume(message)
	elif message.content.lower() == 'inkbot: stop':
		await mediaStop(message, mediaQueues)
	elif message.content.lower() == 'inkbot: skip':
		await mediaSkip(message, mediaQueues)
	elif message.content.lower() == 'inkbot: queue':
		await mediaQueue(message, mediaQueues)
	elif message.content.lower().startswith('inkbot: cancel'):
		await mediaCancel(message, mediaQueues)
		
	elif message.content.lower().startswith('inkbot: draw'):
		await bot.change_presence(status=discord.Status.dnd, activity=discord.Game('with art'))
		await dallePost(message)
		await bot.change_presence(status=discord.Status.online, activity=discord.Game(name="with MultiVAC"))
		
	elif message.content.lower().startswith('inkbot: forget'):
		await chatForget(message, chatHistories)
	elif message.content.lower().startswith('inkbot: become'):
		await chatBecome(message, chatHistories)
	elif message.content.lower().startswith('inkbot: select'):
		await chatSelect(message, chatHistories)
	elif message.content.lower() == 'inkbot: session start' or message.content.lower() == 'inkbot: session':
		await chatSession(message, chatSessions)
	elif message.content.lower() == 'inkbot: session stop' or message.content.lower() == 'inkbot: endsession':
		await chatSessionEnd(message, chatSessions)
	elif (
		message.content.lower().startswith('inkbot,') or
		message.content.lower().startswith('dinklebot,') or
		(
			message.channel.id in chatSessions and
			not message.content.lower().startswith('inkbot:') and
			(
				not message.content.lower().startswith('inkbot4,') or
				not message.content.lower().startswith('dinklebot4,')
			)
		)
	):
		await bot.change_presence(status=discord.Status.dnd, activity=discord.Game('with words'))
		await chatPost(message, chatHistories, defaultHistoryEntry, "gpt-3.5-turbo")
		await bot.change_presence(status=discord.Status.online, activity=discord.Game(name="with MultiVAC"))
		
	elif message.content.lower().startswith('inkbot4: forget'):
		await chatForget(message, chat4Histories)
	elif message.content.lower().startswith('inkbot4: become'):
		await chatBecome(message, chat4Histories)
	elif message.content.lower().startswith('inkbot4: select'):
		await chatSelect(message, chat4Histories)
	elif message.content.lower() == 'inkbot4: session start' or message.content.lower() == 'inkbot4: session':
		await chatSession(message, chat4Sessions)
	elif message.content.lower() == 'inkbot4: session stop' or message.content.lower() == 'inkbot4: endsession':
		await chatSessionEnd(message, chat4Sessions)
	elif (
		message.content.lower().startswith('inkbot4,') or
		message.content.lower().startswith('dinklebot4,') or
		(
			message.channel.id in chat4Sessions and
			not message.content.lower().startswith('inkbot:') and
			(
				not message.content.lower().startswith('inkbot,') or
				not message.content.lower().startswith('dinklebot,')
			)
		)
	):
		await bot.change_presence(status=discord.Status.dnd, activity=discord.Game('with thoughts'))
		await chatPost(message, chat4Histories, defaultHistoryEntry, "gpt-4")
		await bot.change_presence(status=discord.Status.online, activity=discord.Game(name="with MultiVAC"))

# Start bot
bot.run(DISCORD_TOKEN)