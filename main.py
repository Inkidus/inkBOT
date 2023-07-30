# main.py
# =============================================================================
# Last Modified:   07/29/2023 20:21 PM
# Description:     This file is the main file for the discord bot. It will call
#                  different functions in the commands<Category>.py files to
#                  respond to different commands/conditions. Running this file
#                  will also start the bot.
# =============================================================================


from commandsSetup import DISCORD_TOKEN, INKDROID_ID
from commandsGPT import *
from commandsVC import *
from commandsOther import *

import discord
from discord.ext import commands
from discord.ext.commands import CommandNotFound


# Configure Bot Intents + other bot settings, gives the bot the perms it needs
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.voice_states = True
intents.typing = False
intents.presences = False


# Create the representation of the bot using the intents above + other settings
bot = commands.Bot(
    command_prefix='inkbot!',
    intents=intents,
    status=discord.Status.online,
    activity=discord.Game(
        name="with MultiVAC",
    )
)


# Establish bot behavior after successful login (may occur multiple times)
@bot.event
async def on_ready():
    logging.info(f"Successfully logged in as {bot.user}\n")
    
    global allowBOT
    allowBOT = False


# Establish bot behavior when a change in someone's voice state is detected
@bot.event
async def on_voice_state_update(member, before, after):
    guild = member.guild
    voice_client = guild.voice_client
    
    # If bot has left a voice channel, clear the queue
    if ((member == bot.user) and (after.channel is None) and
        (before.channel is not None)):
        mediaQueues[guild.id] = []
    
    # If bot is left alone in a voice channel, start timer
    if ((not member.bot) and (before.channel != after.channel)):
        # Leave if alone
        if voice_client and voice_client.channel == before.channel:
            await checkAlone(guild, voice_client)


# Establish bot behavior when a message is sent in a channel it can read
@bot.event
async def on_message(message):
    global allowBOT
    
    msgAuthor = message.author
    msgChannel = message.channel.id
    msgText = message.content.lower()
    
    # Ignore bot messages except if inkDROID + setting are on
    if msgAuthor.bot and not allowBOT:
        return
    if msgAuthor.bot and msgAuthor.id != INKDROID_ID:
        return
    
    # Ignore messages that start with ;
    elif msgText.startswith(';'):
        return
    
    # inkBOT Settings
    elif (msgText == 'inkbot: setting allowbot' and
          msgAuthor.id == free_game_ids):
        
        allowBOT = not allowBOT
        if (allowBOT):
            await message.reply(
                "Understood, I'll listen to messages from inkDROID", 
                mention_author=False,
                delete_after=10,
            )
        else:
            await message.reply(
                "Understood, I'll ignore messages from inkDROID", 
                mention_author=False,
                delete_after=10,
            )
            return
    
    elif msgText.startswith('inkbot: setting'):
        await message.reply(
            "Coming soon",
            mention_author=False,
            delete_after=10,
        )
        return
    
    # Useful Commands
    elif msgText.startswith('inkbot: avatar'):
        await avatarPost(message, bot)
        return
    elif msgText == 'inkbot: servericon':
        await serverPost(message, bot)
        return
    
    # Random Chance Commands
    elif msgText.startswith('inkbot: roll'):
        await dicePost(message)
        return
    elif msgText == 'inkbot: coinflip':
        await coinPost(message)
        return
    
    # Free Game Commands
    elif (msgText == 'inkbot: freebies send' and
          msgAuthor.id == free_game_ids):
        await freebiesPost(message, bot, free_game_channels)
        return
    elif (msgText == 'inkbot: freebies read' and
          msgAuthor.id == free_game_ids):
        await freebiesRead(message)
        return
    elif (msgText.startswith('inkbot: freebies write') and 
          msgAuthor.id == free_game_ids):
        await freebiesWrite(message)
        return
    
    # Help Command
    elif msgText.startswith('inkbot: help'):
        await helpPost(message)
        return
    
    # Voice Channel Media Commands
    elif msgText == 'inkbot: join':
        await vcJoin(message)
        return
    elif msgText == 'inkbot: leave':
        await vcLeave(message)
        return
    elif msgText == 'inkbot: play':
        await mediaForce(message)
        return
    elif msgText.startswith('inkbot: play'):
        await mediaAdd(message, bot)
        return
    elif msgText == 'inkbot: pause':
        await mediaPause(message)
        return
    elif msgText == 'inkbot: resume':
        await mediaResume(message)
        return
    elif msgText == 'inkbot: stop':
        await mediaStop(message)
        return
    elif msgText == 'inkbot: skip':
        await mediaSkip(message)
        return
    elif msgText == 'inkbot: queue':
        await mediaQueue(message)
        return
    elif msgText == 'inkbot: recent':
        await mediaRecent(message)
        return
    elif msgText.startswith('inkbot: cancel'):
        await mediaCancel(message)
        return
    
    # Voice Channel Text to Speech Commands
    elif msgText.startswith('inkbot: tts'):
        await ttsSpeak(message)
        return
    elif msgText.startswith('inkbot4: tts'):
        await ttsVoice(message)
        return
    
    # Dall-E Command
    elif msgText.startswith('inkbot: draw'):
        await dallePost(message)
        return
    
    # GPT-3 Supplementary Commands
    elif msgText.startswith('inkbot: forget'):
        await chatForget(message, "gpt-3.5-turbo")
        return
    elif msgText.startswith('inkbot: become'):
        await chatBecome(message, "gpt-3.5-turbo")
        return
    elif msgText.startswith('inkbot: select'):
        await chatSelect(message, "gpt-3.5-turbo")
        return
    elif msgText == 'inkbot: session start':
        await chatSession(message, "gpt-3.5-turbo")
        return
    elif msgText == 'inkbot: session stop':
        await chatSessionEnd(message, "gpt-3.5-turbo")
        return
    elif msgText.startswith('inkbot: session modify'):
        await chatSessionModify(message, "gpt-3.5-turbo")
        return
    elif msgText.startswith('inkbot: learn'):
        await chatLearn(message, "gpt-3.5-turbo")
        return
    
    # GPT-4 Supplementary Commands
    elif msgText.startswith('inkbot4: forget'):
        await chatForget(message, "gpt-4")
        return
    elif msgText.startswith('inkbot4: become'):
        await chatBecome(message, "gpt-4")
        return
    elif msgText.startswith('inkbot4: select'):
        await chatSelect(message, "gpt-4")
        return
    elif msgText == 'inkbot4: session start':
        await chatSession(message, "gpt-4")
        return
    elif msgText == 'inkbot4: session stop':
        await chatSessionEnd(message, "gpt-4")
        return
    elif msgText.startswith('inkbot4: session modify'):
        await chatSessionModify(message, "gpt-4")
        return
    elif msgText.startswith('inkbot4: learn'):
        await chatLearn(message, "gpt-4")
        return
    
    # Process Commands if present
    # await bot.process_commands(message)
    
    # Ignore malformed commands so chatbot does not consider them prompts
    if msgText.startswith('inkbot:'):
        return
    elif msgText.startswith('inkbot4:'):
        return
    
    # Ignore commands meant for inkDROID
    elif msgText.startswith('inkdroid:'):
        return
    elif msgText.startswith('inkdroid4:'):
        return
    elif msgText.startswith('inkdroid,'):
        return
    elif msgText.startswith('inkdroid4,'):
        return
    
    # GPT Commands
    elif (msgText.startswith('inkbot,') or bot.user.mentioned_in(message) or
          (msgChannel in chatSessions and not msgText.startswith('inkbot4,'))):
        await chatPost(message, "gpt-3.5-turbo")
        return
    elif (msgText.startswith('inkbot4,') or ((-msgChannel) in chatSessions)):
        await chatPost(message, "gpt-4")
        return

# Start bot
bot.run(DISCORD_TOKEN)