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


async def send_long_message(message_content, channel):
    while message_content:
        # Split the message at the last newline character within the character limit
        split_index = message_content.rfind('\n', 0, 2000)
        if split_index == -1:
            # If there is no newline character within the limit, split at the character limit
            split_index = 2000

        part = message_content[:split_index]
        message_content = message_content[split_index:].lstrip('\n')

        # Send the message part
        await channel.send(part)


async def generate_response(system_content: list[str], user_content: str, channelid):
    try:
        # Store current time
        current_date = datetime.datetime.now().strftime("%B %d, %Y")
        current_time = datetime.datetime.now().strftime("%I:%M:%S %p")
        time_of_response = f"""The current date is {current_date}. The current time is {current_time}."""

        # Make a request to the OpenAI API
        completion_messages = system_content + [{"role": "user", "content": user_content}, {"role": "system", "content": time_of_response}]
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=completion_messages,
            top_p=0.1,
        )
    except InvalidRequestError:
        try:
            # Possible better solution, try recursion?
        
            # Delete 4 oldest prompts and responses
            for i in range(8):
                chat_histories[channelid].pop(2)
            
            # Attempt to generate the message again
            completion_messages = system_content + [{"role": "user", "content": user_content}]
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=completion_messages,
                top_p=0.1,
            )
        except InvalidRequestError:
            # If deleting the oldest messages still didn't work, return error
            return "RequestError"
        except RateLimitError:
            return "RateError"
    except RateLimitError:
        # Return the code for a rate limit eror
        return "RateError"
    
    
    # Process the API response
    return response.choices[0].message.content.strip()


async def is_message_safe(message):
    response = openai.Moderation.create(
        input = message
    )

    results = response["results"]
    flagged = results[0]["flagged"]
    logging.info(f"Were scanned contents flagged? {flagged}\n")
    return not flagged


async def freegamespost():
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