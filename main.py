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
	
	# Ignore messages that start with ;
	elif message.content.lower().startswith('; '):
		return
		
	# Random Chance Commands
	elif message.content.lower().startswith('inkbot: roll'):
		await dicePost(message)
		return
	elif  message.content.lower() == 'inkbot: coinflip':
		await coinPost(message)
		return
	
	# Free Game Command
	elif message.content.lower() == 'inkbot: freebies' and message.author.id == free_game_ids:
		await freeGamesPost(message, bot, free_game_channels)
		return
	
	# Help Command
	elif message.content.lower().startswith('inkbot: help'):
		await helpPost(message)
		return
	
	# Voice Channel Media Commands
	elif message.content.lower() == 'inkbot: join':
		await vcJoin(message)
		return
	elif message.content.lower() == 'inkbot: leave':
		await vcLeave(message)
		return
	elif message.content.lower().startswith('inkbot: play'):
		await bot.change_presence(status=discord.Status.dnd, activity=discord.Game('with music'))
		await mediaAdd(message)
		await bot.change_presence(status=discord.Status.online, activity=discord.Game(name="with MultiVAC"))
		return
	elif message.content.lower() == 'inkbot: pause':
		await mediaPause(message)
		return
	elif message.content.lower() == 'inkbot: resume':
		await mediaResume(message)
		return
	elif message.content.lower() == 'inkbot: stop':
		await mediaStop(message)
		return
	elif message.content.lower() == 'inkbot: skip':
		await mediaSkip(message)
		return
	elif message.content.lower() == 'inkbot: queue':
		await mediaQueue(message)
		return
	elif message.content.lower().startswith('inkbot: cancel'):
		await mediaCancel(message)
		return
	
	# Voice Channel Text to Speech Commands
	elif message.content.lower().startswith('inkbot: tts'):
		await bot.change_presence(status=discord.Status.dnd, activity=discord.Game('my voice'))
		await ttsSpeak(message)
		await bot.change_presence(status=discord.Status.online, activity=discord.Game(name="with MultiVAC"))
		return
	elif message.content.lower().startswith('inkbot4: tts'):
		await ttsVoice(message)
		return
	
	# Dall-E Command
	elif message.content.lower().startswith('inkbot: draw'):
		await bot.change_presence(status=discord.Status.dnd, activity=discord.Game('with art'))
		await dallePost(message)
		await bot.change_presence(status=discord.Status.online, activity=discord.Game(name="with MultiVAC"))
		return
	
	# GPT-3 Supplementary Commands
	elif message.content.lower().startswith('inkbot: forget'):
		await chatForget(message, "gpt-3.5-turbo")
		return
	elif message.content.lower().startswith('inkbot: become'):
		await chatBecome(message, "gpt-3.5-turbo")
		return
	elif message.content.lower().startswith('inkbot: select'):
		await chatSelect(message, "gpt-3.5-turbo")
		return
	elif message.content.lower() == 'inkbot: session start':
		await chatSession(message, "gpt-3.5-turbo")
		return
	elif message.content.lower() == 'inkbot: session stop':
		await chatSessionEnd(message, "gpt-3.5-turbo")
		return
	elif message.content.lower().startswith('inkbot: session modify'):
		await chatSessionModify(message, "gpt-3.5-turbo")
		return
	elif message.content.lower().startswith('inkbot: learn'):
		await chatLearn(message, "gpt-3.5-turbo")
		return
	
	# GPT-4 Supplementary Commands
	elif message.content.lower().startswith('inkbot4: forget'):
		await chatForget(message, "gpt-4")
		return
	elif message.content.lower().startswith('inkbot4: become'):
		await chatBecome(message, "gpt-4")
		return
	elif message.content.lower().startswith('inkbot4: select'):
		await chatSelect(message, "gpt-4")
		return
	elif message.content.lower() == 'inkbot4: session start' or message.content.lower() == 'inkbot4: session':
		await chatSession(message, "gpt-4")
		return
	elif message.content.lower() == 'inkbot4: session stop' or message.content.lower() == 'inkbot4: endsession':
		await chatSessionEnd(message, "gpt-4")
		return
	elif message.content.lower().startswith('inkbot4: session modify'):
		await chatSessionModify(message, "gpt-4")
		return
	elif message.content.lower().startswith('inkbot4: learn'):
		await chatLearn(message, "gpt-4")
		return
	
	# Process Commands if present
	await bot.process_commands(message)
	
	# Ignore malformed commands so chatbot does not consider them prompts
	if message.content.lower().startswith('inkbot:'):
		return
	elif message.content.lower().startswith('inkbot4:'):
		return
	
	# GPT Commands
	elif message.content.lower().startswith('inkbot,') or (message.channel.id in chatSessions and not message.content.lower().startswith('inkbot4,')):
		await bot.change_presence(status=discord.Status.dnd, activity=discord.Game('with words'))
		await chatPost(message, "gpt-3.5-turbo")
		await bot.change_presence(status=discord.Status.online, activity=discord.Game(name="with MultiVAC"))
		return
	elif message.content.lower().startswith('inkbot4,') or ((message.channel.id * -1) in chatSessions):
		await bot.change_presence(status=discord.Status.dnd, activity=discord.Game('with thoughts'))
		await chatPost(message, "gpt-4")
		await bot.change_presence(status=discord.Status.online, activity=discord.Game(name="with MultiVAC"))
		return

# Start bot
bot.run(DISCORD_TOKEN)