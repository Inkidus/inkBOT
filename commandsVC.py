# commandsVC.py
# -----------------------------------------------------------------------------
# Last Modified:   07/29/2023 20:21 PM
# Description:     This file primarily focuses on commands which are related to
#                  the bot's features in voice channels: media playback and tts
#                  through local audio generation and google's tts API.
# -----------------------------------------------------------------------------

from commandsSetup import mediaQueues, mediaHistory, GOOGLE_API_KEY
from commandsOther import sendLongMessage
from commandsGPT import checkModeration

import os
import logging
import discord
import pyttsx3
import yt_dlp
import asyncio
import yaml
import json
import base64
import asyncio
import requests

from discord import FFmpegPCMAudio
from google.cloud import texttospeech
from concurrent.futures import ThreadPoolExecutor

from commandsOther import saveYAML

# Asynchronously get information about a url
async def getInformation(ydl, url):
    loop = asyncio.get_event_loop()
    
    with ThreadPoolExecutor() as executor:
        info = await loop.run_in_executor(
            executor,
            lambda: ydl.extract_info(
                url, download=False
                )
        )
        
        return info

# Function will make the bot join the voice channel of the sender, if they are in one accessible by the bot
async def vcJoin(originalMessage):
    if (originalMessage.author.voice is not None):
        theVoiceClient = originalMessage.guild.voice_client
        
        if (originalMessage.guild.voice_client is None):
            theVoiceClient = await originalMessage.author.voice.channel.connect(reconnect = False,self_deaf = True)
            logging.info(f"User ID: {originalMessage.author.id} - Successfully Requested joining of voice channel: {originalMessage.author.voice.channel}\n")
            await originalMessage.reply(f"Joining your voice chat...", delete_after=10, mention_author=False)
        elif (theVoiceClient is not originalMessage.author.voice):
            if (len(theVoiceClient.channel.members) <= 1):
                await theVoiceClient.move_to(originalMessage.author.voice.channel)
                logging.info(f"User ID: {originalMessage.author.id} - Successfully Requested joining of voice channel: {originalMessage.author.voice.channel}\n")
            await originalMessage.reply(f"Joining your voice chat....", delete_after=10, mention_author=False)
        else:
            logging.info(f"User ID: {originalMessage.author.id} - Unsuccessfully Requested joining of voice channel: {originalMessage.author.voice.channel}\n")
            await originalMessage.reply("Sorry, looks like I'm in another voice chat", delete_after=10, mention_author=False)	
    else:
        await originalMessage.channel.send("Sorry, you don't seem to be in a voice chat I can access", delete_after=10)

# Function will make the bot leave its current voice channel, if it is in one
async def vcLeave(originalMessage):
    if originalMessage.guild.voice_client:
        logging.info(f"User ID: {originalMessage.author.id} - Requested leaving of voice channel\n")
        
        if originalMessage.guild.voice_client.is_playing():
            await mediaStop(originalMessage)
        
        await originalMessage.reply(f"Leaving my current voice chat...", delete_after=10, mention_author=False)
        
        await originalMessage.guild.voice_client.disconnect()
        
    else:
        logging.info(f"User ID: {originalMessage.author.id} - Unsuccessfully Requested leaving of voice channel\n")
        await originalMessage.channel.send("Sorry, I don't think I'm in a voice chat right now", delete_after=10)

# Function will make the bot speak some words out loud in a voice channel
async def ttsSpeak(originalMessage):
    if not originalMessage.author.voice:
        await originalMessage.channel.send("Sorry, you don't seem to be in a voice chat I can access", delete_after=10)
        return
    
    if not originalMessage.guild.voice_client:
        await vcJoin(originalMessage)
    
    message = originalMessage.content[11:].strip()
    
    logging.info(f"User ID: {originalMessage.author.id} - Requested tts of: {message}\n")
    
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[0].id)

    if os.path.exists('tospeak.wav'):
        os.remove('tospeak.wav')

    engine.save_to_file(message, 'tospeak.wav')
    engine.runAndWait()

    engine.stop()
    
    while not os.path.exists('tospeak.wav'):
        await asyncio.sleep(0.1)
    
    originalMessage.guild.voice_client.play(source = discord.FFmpegPCMAudio('tospeak.wav'))

# Function will make the bot speak some words in a voice channel using Google's TTS API
async def ttsVoice(originalMessage):
    if not originalMessage.author.voice:
        await originalMessage.channel.send("Sorry, you don't seem to be in a voice chat I can access", delete_after=10)
        return
    
    wordsToSpeak = originalMessage.content[12:].strip()
    
    promptSafe = await checkModeration(originalMessage)
    
    if promptSafe:
        logging.info(f"User ID: {originalMessage.author.id} - Requested Google TTS of: {wordsToSpeak}\n")
        
        with open("storedGoogleTTSCount.yaml", 'r') as file:
            characterCount = yaml.load(file, Loader=yaml.FullLoader)
        
        characterCount += len(wordsToSpeak)
        
        if (characterCount >= 3000000):
            await originalMessage.channel.send("Sorry, but this message will exceed the free message limit for the month")
            return
        
        characterCount += len(wordsToSpeak)
        
        data = {
            'input': {'text': wordsToSpeak},
            'voice': {'languageCode': 'en-gb', 'name': 'en-GB-Standard-C', 'ssmlGender': 'FEMALE'},
            'audioConfig': {'audioEncoding': 'MP3'},
        }
        
        response = requests.post(
            'https://texttospeech.googleapis.com/v1/text:synthesize?key=' + GOOGLE_API_KEY,
            headers={'Content-Type': 'application/json'},
            data=json.dumps(data)
        )
        
        with open("storedGoogleTTSCount.yaml", 'w') as file:
            yaml.dump(characterCount, file)
        
        response_data = response.json()
        
        audio_content = base64.b64decode(response_data['audioContent'])
        with open("tospeak.mp3", "wb") as out:
            out.write(audio_content)
        
        if not originalMessage.guild.voice_client:
            await vcJoin(originalMessage)
        
        originalMessage.guild.voice_client.play(source=discord.FFmpegPCMAudio("tospeak.mp3"))
    else:
        logging.info(f"User ID: {originalMessage.author.id} - Requested Unsafe Google TTS of: {wordsToSpeak}\n")
        await originalMessage.channel.send("Sorry, your message was unsafe. Please review the usage policy: <https://openai.com/policies/usage-policies>")

# Function will make the bot stream audio using yt-dlp
async def mediaAdd(originalMessage, theBot):
    async with originalMessage.channel.typing():
        
        guildID = originalMessage.guild.id
        if guildID not in mediaQueues:
            mediaQueues[guildID] = []

        if not originalMessage.author.voice:
            await originalMessage.channel.send("Sorry, you don't seem to be in a voice chat I can access", delete_after=10)
            return
        
        if not originalMessage.guild.voice_client:
            await vcJoin(originalMessage)
            await mediaAdd(originalMessage, theBot)
            return
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'noplaylist': False,
            'quiet': True,
            'age_limit': 17,
            'extract_flat': 'in_playlist,is_live',
            'skip_unavailable_fragments': True,
            'ignoreerrors': True
        }
        
        url = originalMessage.content[12:].strip()
        logging.info(f"User ID: {originalMessage.author.id} - Requested Media: {url}\n")
        
        # Prevent youtube mixes
        if "&start_radio=1" in url:
            await originalMessage.channel.send("Sorry, I can't play Youtube Mixes...", delete_after=10)
            return
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = await getInformation(ydl,url)
            
            # If livestream, do nothing
            is_live = info.get('is_live', False)
            if is_live:
                await originalMessage.channel.send("Sorry, I can't play livestreams...", delete_after=10)
                return

            songList = f""
            
            # If playlist, add all
            if "entries" in info:				
                for entry in info["entries"]:
                    try:
                        audio_url = entry.get('url')
                        video_title = entry.get('title', 'Unknown Title')
                        video_url = entry.get('webpage_url')
                        video_duration = entry.get('duration')
                        mediaQueues[originalMessage.guild.id].append((audio_url, originalMessage.author.global_name, video_title, video_url, video_duration))
                        songList += f"Added {video_title} to the queue!\n"
                    except:
                        songList += f"Failed to add {video_title} to the queue...\n"
            
            # If single video, add
            else:
                audio_url = info.get('url')
                video_title = info.get('title', 'Unknown Title')
                video_url = info.get('webpage_url')
                video_duration = info.get('duration')
                mediaQueues[originalMessage.guild.id].append((audio_url, originalMessage.author.global_name, video_title, video_url, video_duration))
                songList += f"Added {video_title} to the queue!\n"
            
            # Send confirmation message
            await originalMessage.reply(songList, delete_after=10, mention_author=False)

        # If not currently playing, start the queue
        if not originalMessage.guild.voice_client.is_playing():
            await playNext(originalMessage)

# Function will force media to resume playing
async def mediaForce(originalMessage):
    await playNext(originalMessage)

# Function will make bot pause current media
async def mediaPause(originalMessage):
    voice_client = originalMessage.guild.voice_client

    if (not voice_client) and (not voice_client.is_playing()):
        await originalMessage.reply("Sorry, I don't seem to be playing anything right now", delete_after=10, mention_author=False)
        return

    voice_client.pause()
    await originalMessage.reply("Pausing your media...", delete_after=10, mention_author=False)

# Function will make bot continue current media
async def mediaResume(originalMessage):
    voice_client = originalMessage.guild.voice_client

    if (not voice_client) and (not voice_client.is_paused()):
        await originalMessage.reply("Sorry, I don't seem to be paused right now", delete_after=10, mention_author=False)
        return

    voice_client.resume()
    await originalMessage.channel.send("Resuming your media...")

# Function will make the bot stop current media
async def mediaStop(originalMessage):
    guildID = originalMessage.guild.id
    voice_client = originalMessage.guild.voice_client
    
    await originalMessage.reply("Ending audio and clearing the queue...", delete_after=10, mention_author=False)
    
    if not voice_client or not (voice_client.is_playing() or voice_client.is_paused()):
        await originalMessage.reply("Sorry, I don't seem to be playing anything right now", delete_after=10, mention_author=False)
        return
    
    mediaQueues[guildID] = [] # Clear the queue for the guild
    voice_client.stop()

# Function will make the bot skip to the next item in the queue
async def mediaSkip(originalMessage):
    voice_client = originalMessage.guild.voice_client

    if not voice_client or not voice_client.is_playing():
        await originalMessage.reply("Sorry, I don't seem to be playing anything right now", delete_after=10, mention_author=False)
        return

    voice_client.stop()
    await originalMessage.reply("Skipping this item...", delete_after=10, mention_author=False)

# Function will make the bot show the current queue
async def mediaQueue(originalMessage):
    async with originalMessage.channel.typing():
        queue = mediaQueues.get(originalMessage.guild.id, [])

        if not queue:
            await originalMessage.reply("The queue is currently empty", delete_after=10, mention_author=False)
            return

        queue_text = "**Coming Up:**\n```md\n"
        for i, (audio_url, requester_name, video_title, video_url,
        video_duration) in enumerate(queue, start=1):
            if (len(queue_text) + 200) >= 2000:
                queue_text += "```"
                await originalMessage.reply(queue_text)
                queue_text = "**Coming Up (continued):**\n```md\n"
            
            queue_text += f"{i}. {video_title} - Requested by: {requester_name}\n"
            
        queue_text += "```"

        await originalMessage.reply(queue_text)
        
# Function will make the bot show the queue history
async def mediaRecent(originalMessage):
    async with originalMessage.channel.typing():
        queue = mediaHistory.get(originalMessage.guild.id, [])

        if not queue:
            await originalMessage.reply("There has been no media played since I was last restarted", delete_after=10, mention_author=False)
            return

        historyText = ""
        for i, (requester_name, video_title) in enumerate(queue, start=0):
            historyText = f"{len(mediaHistory[originalMessage.guild.id]) - i}. {video_title} - Requested by: {requester_name}\n" + historyText
        historyText += "```"
        historyText = "**Recently Played in this Server:**\n```md\n" + historyText

        await originalMessage.reply(historyText)

# Function will remove the item at a given slot from the queue
async def mediaCancel(originalMessage):
    guildID = originalMessage.guild.id
    serverQueue = mediaQueues.get(guildID, [])
    
    index = int(originalMessage.content[14:].strip())

    if not serverQueue:
        await originalMessage.reply("The queue is currently empty", delete_after=10, mention_author=False)
        return

    try:
        removed_item = serverQueue.pop(index - 1)
        await originalMessage.reply(f"Removed item #{index} from the queue.", delete_after=10, mention_author=False)
        await mediaQueue(originalMessage)
    except IndexError:
        await originalMessage.reply(f"Sorry, couldn't find item #{index}.", delete_after=10, mention_author=False)
        await mediaQueue(originalMessage)

async def playNext(originalMessage):
    voice_client = originalMessage.guild.voice_client
    guildID = originalMessage.guild.id
    
    if not mediaQueues[originalMessage.guild.id]:
        return
    if not voice_client:
        return
    
    if guildID not in mediaHistory:
        mediaHistory[originalMessage.guild.id] = []
    
    audio_url, requester_name, video_title, video_url, video_duration = mediaQueues[originalMessage.guild.id].pop(0)
    voice_client.stop()
    
    FFMPEG_OPTIONS = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
        'options': '-vn'
    }
    
    await originalMessage.channel.send("**Now Playing:** " + video_url + "\n**Requested by:** " + originalMessage.author.nick + " (" + originalMessage.author.global_name + ")",delete_after=(video_duration + 10))
    
    voice_client.play(FFmpegPCMAudio(executable="ffmpeg", source=audio_url, **FFMPEG_OPTIONS), after=lambda e: asyncio.run_coroutine_threadsafe(playNext(originalMessage), voice_client.loop))
    voice_client.source = discord.PCMVolumeTransformer(voice_client.source)
    voice_client.source.volume = 0.1
    
    mediaHistory[originalMessage.guild.id].append((originalMessage.author.global_name, video_title))
    
    if (len(mediaHistory[originalMessage.guild.id]) > 10):
        mediaHistory[originalMessage.guild.id].pop(0)

async def checkAlone(guild, voice_client):
    while True:
        members = voice_client.channel.members
        non_bots = [member for member in members if not member.bot]
        
        # If no humans present, check again in 20 seconds. If no humans present then, leave
        await asyncio.sleep(20)
        members = voice_client.channel.members
        non_bots = [member for member in members if not member.bot]
        
        if len(non_bots) == 0:
            while voice_client.is_playing():
                voice_client.stop()
            await voice_client.disconnect()
            voice_client.cleanup()
            break