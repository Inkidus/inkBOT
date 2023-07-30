# commandsOther.py
# =============================================================================
# Last Modified:   07/29/2023 20:21 PM
# Description:     This file primarily focuses on other text-based commands
#                  which do not rely on OpenAI. 
# =============================================================================


from commandsSetup import free_game_ids, free_game_channels
from commandsStrings import *

import os
import yaml
import logging
import requests
import random
import asyncio


# saveYAML()
# -----------------------------------------------------------------------------
# Inputs:      The YAMl file the information is being stored to
#              The name which the dictionary should be stored under
#              The dictionary which is to be stored
# Outputs:     n/a
# Description: This function allows for information stored as a dictionary to
#              be stored in a specified YAML file.
# -----------------------------------------------------------------------------
def saveYAML(desiredFile, dictionaryName, desiredDictionary):
    with open(desiredFile, 'w') as file:
        file.write(
            yaml.dump(
                {dictionaryName: desiredDictionary},
                sort_keys=False
            )
        )


# sendLongMessage()
# -----------------------------------------------------------------------------
# Inputs:      The message this response is replying to
#              The contents of the reply
# Outputs:     n/a
# Description: This function will take a response which is over 2000 characters
#              and splits it into multiple replies based on the location of
#              linebreaks throughout the message
# -----------------------------------------------------------------------------
async def sendLongMessage(originalMessage, responseContents):
    while responseContents:
        splitIndex = responseContents.rfind('\n', 0, 2000)
        if splitIndex == -1:
            splitIndex = 2000
        
        responseSegment = responseContents[:splitIndex]
        responseContents = responseContents[splitIndex:].lstrip('\n')
        
        if originalMessage.author.bot:
            await originalMessage.reply(responseSegment, mention_author=True)
        else:
            await originalMessage.reply(responseSegment, mention_author=False)


# avatarPost()
# -----------------------------------------------------------------------------
# Inputs:      The discord message which used this command,
#              The representation of the bot
# Outputs:     n/a
# Description: This function takes the first person mentioned after the command
#              and allows the user to obtain their avatar.
# -----------------------------------------------------------------------------
async def avatarPost(originalMessage, theBot):
    mentionedUser = originalMessage.mentions[0]
    
    await originalMessage.reply(
        f"Here is {mentionedUser.mention}'s avatar\n"
        + mentionedUser.display_avatar.url,
        mention_author=False,
    )


# serverPost()
# -----------------------------------------------------------------------------
# Inputs:      The discord message which used this command,
#              The representation of the bot
# Outputs:     n/a
# Description: This function allows the user to obtain the icon of the server
#              the original message is sent in.
# -----------------------------------------------------------------------------
async def serverPost(originalMessage, theBot):
    try:
        await originalMessage.reply(
            f"Here is {originalMessage.guild.name}'s icon\n"
            + originalMessage.guild.icon.url,
            mention_author=False,
        )
    except:
        await originalMessage.reply(
            f"It doesn't seem like this server has an icon...",
            mention_author=False,
        )


# dicePost()
# -----------------------------------------------------------------------------
# Inputs:      The discord message which used this command
# Outputs:     n/a
# Description: This function allows the user to simulate a dice roll. Depending
#              on the input number of sides, certain messages will appear in
#              the place of warnings in the case of non-valid integers.
# -----------------------------------------------------------------------------
async def dicePost(originalMessage):
    async with originalMessage.channel.typing():
        # Extract the number of sides
        prompt = originalMessage.content[12:].strip()
        
        # If no input provided
        if not prompt:
            await originalMessage.reply(
                "Rolling... You rolled a "
                "[Rick](https://www.youtube.com/watch?v=dQw4w9WgXcQ)!\n"
                "(Please include a number next time!)"
            )
        
        # If some input was provided
        else:
            try:
                side_number = int(prompt)
                if side_number < 0:
                    roll_result = random.randint(side_number, -1)
                    await originalMessage.reply(
                        f"Rolling an anti-dice with {side_number} sides...\n"
                        f"You rolled a **{roll_result}**!"
                    )
                elif side_number == 0:
                    await originalMessage.reply(
                        f"Rolling a 0-sided dice...\nWhere did it go?"
                    )
                elif side_number == 1:
                    roll_result = random.randint(1, 20)
                    if roll_result == 1:
                        await originalMessage.reply(
                            f"Rolling a 1-sided dice...\nYou rolled a **1**!"
                        )
                    else:
                        await originalMessage.reply(
                            f"Rolling a 1-sided dice...\n"
                            f"You rolled a **{roll_result}**? Wait a second, "
                            f"who wrote on the one sided dice?!"
                        )
                elif side_number == 2:
                    roll_result = random.randint(1, 2)
                    if roll_result == 1:
                        await originalMessage.reply(
                            f"Rolling a 2-sided dice...\n"
                            f"You rolled a **Heads**, I mean **2**!"
                        )
                    else:
                        await originalMessage.reply(
                            f"Rolling a 2-sided dice...\n"
                            f"You rolled a **Tails**, I mean **1**!"
                        )
                else:
                    roll_result = random.randint(1, side_number)
                    await originalMessage.reply(
                        f"Rolling a {side_number}-sided dice...\n"
                        f"You rolled a **{roll_result}**!"
                    )
            except ValueError:
                await originalMessage.reply(
                    "I'm not sure if something with that many sides can even "
                    "exist..."
                )


# coinPost()
# -----------------------------------------------------------------------------
# Inputs:      The discord message which used this command,
# Outputs:     n/a
# Description: This function allows the user to simulate a coinflip. The odds
#              are even, but there is also a small chance that the coin will
#              land on its side (1/6001 chance)
# -----------------------------------------------------------------------------
async def coinPost(originalMessage):
    async with originalMessage.channel.typing():
        randomInt = random.randint(1, 6001)
        
        if randomInt == 3001:
            await originalMessage.reply(
                f'Flipping a coin...\nIt landed on **its side**?'
            )
        elif randomInt < 3001:
            await originalMessage.reply(
                f'Flipping a coin...\n**Heads**!'
            )
        elif randomInt > 3001:
            await originalMessage.reply(
                f'Flipping a coin...\n**Tails**!')
        else:
            await originalMessage.reply(
                f"Flipping a coin...\nHuh, the coin disappeared..."
            )


# freebiesPost()
# -----------------------------------------------------------------------------
# Inputs:      The discord message which used this command,
# Outputs:     n/a
# Description: This function will take the contents of toShareFreebies.txt and
#              formats it for a freebies post, then sends it to a pre-defined
#              list of channels.
# -----------------------------------------------------------------------------
async def freebiesPost(originalMessage, bot, free_game_channels):
    async with originalMessage.channel.typing():
        # Open the file where free games are stored
        with open("toShareFreebies.txt", "r") as file:
            lines = file.readlines()
        
        # Set up temporary variables
        deals = {}
        currentWebsite = None
        
        # Extract information from the file
        for line in lines:
            line = line.strip()
            if not line:
                continue
        
            if line.endswith(':'):
                currentWebsite = line[:-1]
                deals[currentWebsite] = []
            else:
                deals[currentWebsite].append(line)
        
        # Generate the message which will be sent
        response = "__Here's some new (temporary) freebies to add:__"
        for website, website_deals in deals.items():
            response += f"\n**From {website}:**\n"
            for deal in website_deals:
                response += f"{deal}\n"
        
        # For each channel saved, send the message
        for channel_id in free_game_channels:
            target_channel = bot.get_channel(channel_id)
            await target_channel.send(response)
        
        await originalMessage.reply(
            "Finished sending announcements",
            delete_after=10,
            mention_author=False
        )


# freebiesRead()
# -----------------------------------------------------------------------------
# Inputs:      The discord message which used this command
# Outputs:     n/a
# Description: This function allows toShareFreebies.txt to be read remotely
#              through discord.
# -----------------------------------------------------------------------------
async def freebiesRead(originalMessage):
    async with originalMessage.channel.typing():
        with open("toShareFreebies.txt", "r") as freeGamesFile:
            fileContents = freeGamesFile.read()
        await originalMessage.channel.send(
            f"Here are the current contents of toShareFreebies.txt:\n"
            f"```\n{fileContents}\n```",
            delete_after=30,
            mention_author=False,
        )


# freebiesWrite()
# -----------------------------------------------------------------------------
# Inputs:      The discord message which used this command
# Outputs:     n/a
# Description: This function allows toShareFreebies.txt to be updated remotely
#              through discord.
# -----------------------------------------------------------------------------
async def freebiesWrite(originalMessage):
    async with originalMessage.channel.typing():
        content = originalMessage.content.split("%%%")
        
        if len(content) >= 3:
            newContent = content[1].strip()
            with open("toShareFreebies.txt", "w") as freeGamesFile:
                freeGamesFile.write(newContent)
            await originalMessage.reply(
                "Freebies file was updated successfully!",
                delete_after=10,
                mention_author=False,
            )
        else:
            await originalMessage.reply(
                "Failed to update the freebies file, make sure to include the "
                "`%%%` markers around your desired text",
                delete_after=10,
                mention_author=False,
            )


# helpPost()
# -----------------------------------------------------------------------------
# Inputs:      The discord message which used this command
# Outputs:     n/a
# Description: This function allows the user to access a list of commands the
#              discord bot will respond to. If a specific command is specified,
#              more detailed information about the command will be provided.
# -----------------------------------------------------------------------------
async def helpPost(originalMessage):
    async with originalMessage.channel.typing():
        # Extract the context provided
        desiredHelp = originalMessage.content[12:].strip().lower()
        
        # Respond depending on the context provided
        if not desiredHelp:
            await originalMessage.channel.send(DEFAULT_HELP)
        elif desiredHelp == 'learn':
            await originalMessage.channel.send(LEARN_HELP)
        elif desiredHelp == 'forget':
            await originalMessage.channel.send(FORGET_HELP)
        elif desiredHelp == 'become':
            await originalMessage.channel.send(BECOME_HELP)
        elif desiredHelp == 'select':
            await originalMessage.channel.send(SELECT_HELP)
        elif desiredHelp == 'session start':
            await originalMessage.channel.send(START_SESSION_HELP)
        elif desiredHelp == 'session stop':
            await originalMessage.channel.send(STOP_SESSION_HELP)
        elif desiredHelp == 'session modify':
            await originalMessage.channel.send(MODIFY_SESSION_HELP)
        elif desiredHelp == 'draw':
            await originalMessage.channel.send(DRAW_HELP)
        elif desiredHelp == 'join':
            await originalMessage.channel.send(JOIN_HELP)
        elif desiredHelp == 'leave':
            await originalMessage.channel.send(LEAVE_HELP)
        elif desiredHelp == 'tts':
            await originalMessage.channel.send(TTS_HELP)
        elif desiredHelp == 'play':
            await originalMessage.channel.send(PLAY_HELP)
        elif desiredHelp == 'pause':
            await originalMessage.channel.send(PAUSE_HELP)
        elif desiredHelp == 'resume':
            await originalMessage.channel.send(RESUME_HELP)
        elif desiredHelp == 'stop':
            await originalMessage.channel.send(STOP_HELP)
        elif desiredHelp == 'skip':
            await originalMessage.channel.send(SKIP_HELP)
        elif desiredHelp == 'queue':
            await originalMessage.channel.send(QUEUE_HELP)
        elif desiredHelp == 'cancel':
            await originalMessage.channel.send(CANCEL_HELP)
        elif desiredHelp == 'avatar':
            await originalMessage.channel.send(AVATAR_HELP)
        elif desiredHelp == 'servericon':
            await originalMessage.channel.send(SERVERICON_HELP)
        elif desiredHelp == 'coinflip':
            await originalMessage.channel.send(COINFLIP_HELP)
        elif desiredHelp == 'roll':
            await originalMessage.channel.send(ROLL_HELP)
        else:
            await originalMessage.channel.send(UNKNOWN_HELP)