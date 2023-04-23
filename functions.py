from strings import *

import logging
import os
import discord
import openai
import requests
import datetime
import asyncio
import pyttsx3

from dotenv import load_dotenv
from collections import OrderedDict
from discord.ext import commands
from openai.error import InvalidRequestError
from openai.error import RateLimitError


async def send_long_message(message_content, channel):
    while message_content:
        split_index = message_content.rfind('\n', 0, 2000)
        if split_index == -1:
            split_index = 2000

        part = message_content[:split_index]
        message_content = message_content[split_index:].lstrip('\n')

        await channel.send(part)

async def freeGamesPost(originalMessage, client, free_game_channels):
    async with originalMessage.channel.typing():
        with open("freegames.txt", "r") as file:
            lines = file.readlines()

        deals = {}
        current_website = None

        for line in lines:
            line = line.strip()
            if not line:
                continue

            if line.endswith(':'):
                current_website = line[:-1]
                deals[current_website] = []
            else:
                deals[current_website].append(line)

        response = "__Here's some new (temporarily) free games to add to your accounts:__"
        for website, website_deals in deals.items():
            response += f"\n**From {website}:**\n"
            for deal in website_deals:
                response += f"{deal}\n"

        for channel_id in free_game_channels:
            target_channel = client.get_channel(channel_id)
            await target_channel.send(response)

async def helpPost(originalMessage):
    async with originalMessage.channel.typing():
        user_content  = originalMessage.content[12:].strip()
        if not user_content:
            await originalMessage.channel.send(DEFAULT_HELP)
        elif user_content.lower() == 'become':
            await originalMessage.channel.send(BECOME_HELP)
        elif user_content.lower() == 'forget':
            await originalMessage.channel.send(FORGET_HELP)
        elif user_content.lower() == 'draw':
            await originalMessage.channel.send(DRAW_HELP)
        elif user_content.lower() == 'join':
            await originalMessage.channel.send(JOIN_HELP)
        elif user_content.lower() == 'leave':
            await originalMessage.channel.send(LEAVE_HELP)
        elif user_content.lower() == 'tts':
            await originalMessage.channel.send(TTS_HELP)
        else:
            await originalMessage.channel.send(UNKNOWN_HELP)

async def vcJoin(originalMessage):
    async with originalMessage.channel.typing():
        if originalMessage.author.voice is not None:
            try:
                await originalMessage.channel.send(f"Joining your voice chat")
                voice_client = await originalMessage.author.voice.channel.connect()
            except discord.errors.ClientException:
                await originalMessage.channel.send("Sorry, looks like I'm in another voice chat")
        else:
            await originalMessage.channel.send("Sorry, you don't seem to be in a voice chat I can access")

async def vcLeave(originalMessage):
    async with originalMessage.channel.typing():
        if originalMessage.guild.voice_client:
            await originalMessage.channel.send(f"Alright, leaving my current voice chat...")
            await originalMessage.guild.voice_client.disconnect()
        else:
            await originalMessage.channel.send("Sorry, I don't think I'm in a voice chat right now")

async def ttsSpeak(originalMessage):
    if not originalMessage.author.voice:
        await originalMessage.channel.send("Sorry, you don't seem to be in a voice chat I can access")
    elif not originalMessage.guild.voice_client:
        await originalMessage.channel.send("Sorry, I don't think I'm in a voice chat right now")
    else:
        user_content  = originalMessage.content[11:].strip()
        await text_to_speech(user_content, originalMessage)

async def chatForget(originalMessage, chat_histories):
    async with originalMessage.channel.typing():
        if originalMessage.channel.id in chat_histories:
            user_content  = originalMessage.content[14:].strip()
            if not user_content:
                chat_histories.pop(originalMessage.channel.id)
                await originalMessage.channel.send("Understood, clearing all memory from this channel and reverting to my default personality.")
            else:
                numToErase = int(user_content) * 2
                for i in range(numToErase):
                    chat_histories[originalMessage.channel.id].pop(2)
                await originalMessage.channel.send("Understood, clearing " + user_content + " prompts and their responses from this channel.")
        else:
            await originalMessage.channel.send("Sorry, I couldn't find any memories from this channel.")

async def chatBecome(originalMessage, chat_histories):
    async with originalMessage.channel.typing():
        logging.info(f"User ID: {originalMessage.author.id} - Submitted New Personality: {originalMessage.content}\n")
        user_content  = originalMessage.content[14:].strip()

        custom_system_message = [
            {"role": "system", "content": user_content},
            {"role": "system", "content": TEXT_FORMAT},
        ]

        if originalMessage.channel.id not in chat_histories:
            chat_histories[originalMessage.channel.id] = custom_system_message.copy()
            await originalMessage.channel.send("Successfully adopted my new personality.")
        else:
            chat_histories.pop(originalMessage.channel.id)
            chat_histories[originalMessage.channel.id] = custom_system_message.copy()
            await originalMessage.channel.send("Successfully cleared all memories of this channel and adopted my new personality.")

async def dallePost(originalMessage):
    async with originalMessage.channel.typing():
        try:
            image_response = openai.Image.create(
                prompt = originalMessage.content[12:].strip(), 
                n = 1, 
                size = "1024x1024" # Can be 256, 512, 1024
            )
            logging.info(f"User ID: {originalMessage.author.id} - Requested Image: {originalMessage.content}, ")
            logging.info(f"received {image_response['data'][0]['url']}\n")
            await originalMessage.channel.send("Image generated!\n**Prompt:** " + originalMessage.content[12:].strip())
            await originalMessage.channel.send(image_response['data'][0]['url'])
        except InvalidRequestError:
            await originalMessage.channel.send("Sorry, your prompt was unsafe, I couldn't generate an image.")
            logging.info(f"User ID: {originalMessage.author.id} - Submitted Unsafe Image Prompt: {originalMessage.content}, ")

async def chatPost(message, chat_histories, default_system_message):
    async with message.channel.typing():
        isPromptSafe = await is_message_safe(message.content)
        
        
        if isPromptSafe:
            if message.content.lower().startswith('inkbot,') and isPromptSafe:
                user_content  = message.content[7:].strip()
            if message.content.lower().startswith('dinklebot,') and isPromptSafe:
                user_content  = message.content[10:].strip()
            
            
            logging.info(f"User ID: {message.author.id} - Submitted Prompt: {message.content}\n")
            
            
            if message.channel.id not in chat_histories:
                chat_histories[message.channel.id] = default_system_message.copy()
            response = await generate_response(chat_histories[message.channel.id], user_content, message.channel.id)


            if response == "RateError":
                await message.channel.send("Sorry, the rate limit has been reached, please wait a bit before trying again.")
            elif response == "RequestError":
                await message.channel.send("Sorry, could not generate response. Please use \"inkbot: forget\" and try again. If this still did not fix the issue, there was probably an error connecting to OpenAI.")
                for i in range(2):
                    chat_histories[message.channel.id].pop(2)
            else:
                isResponseSafe = await is_message_safe(response)
                if isResponseSafe:
                    logging.info(f"Response: {response}\n")
                    
                    chat_histories[message.channel.id].extend([
                        {"role": "user", "content": user_content},
                        {"role": "assistant", "content": response},
                    ])
                    
                    if len(response) > 2000:
                        await send_long_message(response, message.channel)
                    else:
                        await message.channel.send(response)
                
                else:
                    logging.info(f"Unsafe Response Generated: {response}\n")
                    await message.channel.send("Sorry, the response was unsafe, I can't reply to your prompt.")
        else:
            logging.info(f"User ID: {message.author.id} - Submitted Unsafe Prompt: {message.content}\n")
            await message.channel.send("Sorry, your prompt was unsafe, I couldn't generate a response.")


async def generate_tts_file(message):
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[0].id)

    if os.path.exists('tospeak.wav'):
        os.remove('tospeak.wav')

    engine.save_to_file(message, 'tospeak.wav')
    engine.runAndWait()

    engine.stop()


async def text_to_speech(message, original_message):
    await generate_tts_file(message)
    
    while not os.path.exists('tospeak.wav'):
        await asyncio.sleep(0.1)
    
    current_size = os.path.getsize('tospeak.wav')
    await asyncio.sleep(2)
    new_size = os.path.getsize('tospeak.wav')
    
    while current_size != new_size:
        current_size = new_size
        await asyncio.sleep(2)
        new_size = os.path.getsize('tospeak.wav')
    
    original_message.guild.voice_client.play(source = discord.FFmpegPCMAudio('tospeak.wav'))


async def generate_response(system_content: list[str], user_content: str, channelid):
    try:
        current_date = datetime.datetime.now().strftime("%B %d, %Y")
        current_time = datetime.datetime.now().strftime("%I:%M:%S %p")
        time_of_response = f"""The current date is {current_date}. The current time is {current_time}."""

        completion_messages = system_content + [{"role": "user", "content": user_content}, {"role": "system", "content": time_of_response}]
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=completion_messages,
            top_p=0.1,
        )
    except InvalidRequestError:
        try:
            for i in range(8):
                system_content.pop(2)
            
            completion_messages = system_content + [{"role": "user", "content": user_content}]
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=completion_messages,
                top_p=0.1,
            )
        except InvalidRequestError:
            return "RequestError"
        except RateLimitError:
            return "RateError"
    except RateLimitError:
        return "RateError"
    
    
    return response.choices[0].message.content.strip()


async def is_message_safe(message):
    response = openai.Moderation.create(
        input = message
    )

    results = response["results"]
    flagged = results[0]["flagged"]
    logging.info(f"Were scanned contents flagged? {flagged}\n")
    return not flagged