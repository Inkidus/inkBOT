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

# Configure bot intents
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.typing = False
intents.presences = False
bot = commands.Bot(
	command_prefix='inkbot: ',
	intents=intents,
	status=discord.Status.online,
	activity=discord.Game(
		name="with MultiVAC"
	)
)


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

# Example command
@bot.command()
async def repeat(ctx, arg):
	await ctx.send(arg)

# Establish behavior for when a message is sent
@bot.event
async def on_message(message):
	# Ignore bot messages
	if message.author.bot:
		return
	
	# Ignore messages that start with #
	elif message.content.lower().startswith('# '):
		return
	
	# Random Chance Commands
	elif message.content.lower().startswith('inkbot: roll') or message.content.lower().startswith('inkbot: dice'):
		await dicePost(message)
	elif message.content.lower() == 'inkbot: coin' or message.content.lower() == 'inkbot: coinflip' or message.content.lower() == 'inkbot: flipcoin':
		await coinPost(message)
	
	# Free Game Command
	elif message.content.lower() == 'send free games' and message.author.id == free_game_ids:
		await freeGamesPost(message, bot, free_game_channels)
	
	# Help Command
	elif message.content.lower().startswith('inkbot: help'):
		await helpPost(message)
	
	# Voice Channel Commands
	elif message.content.lower() == 'inkbot: join':
		await vcJoin(message)
	elif message.content.lower() == 'inkbot: leave':
		await vcLeave(message)
	elif message.content.lower().startswith('inkbot: tts'):
		await bot.change_presence(status=discord.Status.dnd, activity=discord.Game('my voice'))
		await ttsSpeak(message)
		await bot.change_presence(status=discord.Status.online, activity=discord.Game(name="with MultiVAC"))
	elif message.content.lower().startswith('inkbot: play'):
		await bot.change_presence(status=discord.Status.dnd, activity=discord.Game('with music'))
		await mediaAdd(message)
		await bot.change_presence(status=discord.Status.online, activity=discord.Game(name="with MultiVAC"))
	elif message.content.lower() == 'inkbot: pause':
		await mediaPause(message)
	elif message.content.lower() == 'inkbot: resume':
		await mediaResume(message)
	elif message.content.lower() == 'inkbot: stop':
		await mediaStop(message)
	elif message.content.lower() == 'inkbot: skip':
		await mediaSkip(message)
	elif message.content.lower() == 'inkbot: queue':
		await mediaQueue(message)
	elif message.content.lower().startswith('inkbot: cancel'):
		await mediaCancel(message)
	
	# Dall-E Command
	elif message.content.lower().startswith('inkbot: draw'):
		await bot.change_presence(status=discord.Status.dnd, activity=discord.Game('with art'))
		await dallePost(message)
		await bot.change_presence(status=discord.Status.online, activity=discord.Game(name="with MultiVAC"))
	
	# GPT-3 Supplementary Commands
	elif message.content.lower().startswith('inkbot: forget'):
		await chatForget(message, "gpt-3.5-turbo")
	elif message.content.lower().startswith('inkbot: become'):
		await chatBecome(message, "gpt-3.5-turbo")
	elif message.content.lower().startswith('inkbot: select'):
		await chatSelect(message, "gpt-3.5-turbo")
	elif message.content.lower() == 'inkbot: session start':
		await chatSession(message, "gpt-3.5-turbo")
	elif message.content.lower() == 'inkbot: session stop':
		await chatSessionEnd(message, "gpt-3.5-turbo")
	elif message.content.lower().startswith('inkbot: session modify'):
		await chatSessionModify(message, "gpt-3.5-turbo")
	
	# GPT-4 Supplementary Commands
	elif message.content.lower().startswith('inkbot4: forget'):
		await chatForget(message, "gpt-4")
	elif message.content.lower().startswith('inkbot4: become'):
		await chatBecome(message, "gpt-4")
	elif message.content.lower().startswith('inkbot4: select'):
		await chatSelect(message, "gpt-4")
	elif message.content.lower() == 'inkbot4: session start' or message.content.lower() == 'inkbot4: session':
		await chatSession(message, "gpt-4")
	elif message.content.lower() == 'inkbot4: session stop' or message.content.lower() == 'inkbot4: endsession':
		await chatSessionEnd(message, "gpt-4")
	elif message.content.lower().startswith('inkbot4: session modify'):
		await chatSessionModify(message, "gpt-4")
	
	# Process Commands if present
	await bot.process_commands(message)
	
	# Ignore malformed commands
	if message.content.lower().startswith('inkbot:'):
		return
	elif message.content.lower().startswith('inkbot4:'):
		return
	
	# GPT Commands
	elif message.content.lower().startswith('inkbot,') or (message.channel.id in chatSessions and not message.content.lower().startswith('inkbot4,')):
		await bot.change_presence(status=discord.Status.dnd, activity=discord.Game('with words'))
		await chatPost(message, "gpt-3.5-turbo")
		await bot.change_presence(status=discord.Status.online, activity=discord.Game(name="with MultiVAC"))
	elif message.content.lower().startswith('inkbot4,') or ((message.channel.id * -1) in chatSessions):
		await bot.change_presence(status=discord.Status.dnd, activity=discord.Game('with thoughts'))
		await chatPost(message, "gpt-4")
		await bot.change_presence(status=discord.Status.online, activity=discord.Game(name="with MultiVAC"))

# Start bot
bot.run(DISCORD_TOKEN)