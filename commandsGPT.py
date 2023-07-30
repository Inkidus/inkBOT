# commandsGPT.py
# =============================================================================
# Last Modified:   07/29/2023 20:21 PM
# Description:     This file primarily focuses on commands which make use of
#                  OpenAI's API, as well as commands which are used to
#                  customize the information which is sent along with API
#                  calls. 
# =============================================================================


from commandsSetup import (chatHistories, chatSessions, webHistories,
                           OPENAI_API_KEY, defaultHistoryEntry, INKDROID_ID,
                           INKBOT_ID)
from commandsOther import saveYAML, sendLongMessage
from commandsStrings import *

import os
import logging
import discord
import openai
import requests
import datetime
import asyncio
import yaml
import json
import base64
import tiktoken

from openai.error import InvalidRequestError
from openai.error import RateLimitError
from openai.error import APIError
from openai.error import APIConnectionError
from openai.error import AuthenticationError
from openai.error import Timeout
from openai.error import ServiceUnavailableError


openai.api_key = OPENAI_API_KEY


# chatBecome()
# -----------------------------------------------------------------------------
# Inputs:      The discord message which used this command,
#              The specification of GPT-3.5-turbo or GPT-4
# Outputs:     n/a
# Description: This function will delete the current conversation history (or
#              creates it), then replaces the default personality info
#              provided alongside the prompt with a custom one
# -----------------------------------------------------------------------------
async def chatBecome(originalMessage, modelRequested):
    originalChannel = originalMessage.channel
    
    logging.info(
     f"User ID: {originalMessage.author.id} - Submitted New "
     f"Personality: {originalMessage.content}\n"
    )
    
    # Determine whether the user wants to modify GPT-3.5-turbo or GPT-4's
    # personality, then obtain the corresponding dictionary key
    if (modelRequested == "gpt-4"):
        dictionaryKey = originalChannel.id * -1
    else:
        dictionaryKey = originalChannel.id
    
    # Extract the new personality from the original message
    if originalMessage.content.lower().startswith('inkbot4:'):
        newPersonality = originalMessage.content[15:].strip()
    elif originalMessage.content.lower().startswith('inkbot:'):
        newPersonality = originalMessage.content[14:].strip()
    else:
        newPersonality = originalMessage.content
    
    # Store the new personality in the format expected by OpenAI
    customSystemMessage = [
        {"role": "system", "content": newPersonality},
        {"role": "system", "content": TEXT_FORMAT},
    ]
    
    # If there is no history stored for that model + channel,
    # Add the custom personality as the first entry in history
    if dictionaryKey not in chatHistories:
        chatHistories[dictionaryKey] = customSystemMessage.copy()
        
        saveYAML(
            "storedHistories.yaml",
            'chatHistories',
            chatHistories
        )
        
        await originalChannel.send("Successfully adopted my new "
        "personality.")
    
    # If history already exists for that model + channel,
    # Clear it, then add the custom personality as the first history entry
    else:
        chatHistories.pop(dictionaryKey)
        chatHistories[dictionaryKey] = customSystemMessage.copy()
        saveYAML("storedHistories.yaml", 'chatHistories', chatHistories)
        await originalChannel.send("Successfully cleared all "
        " memories of this channel and adopted my new personality.")


# chatSelect()
# -----------------------------------------------------------------------------
# Inputs:      The discord message which used this command,
#              The specification of GPT-3.5-turbo or GPT-4
# Outputs:     n/a
# Description: This function will call chatBecome() with a pre-defined argument
#              for the custom personality based on the user's selection.
# -----------------------------------------------------------------------------
async def chatSelect(originalMessage, modelRequested):
    originalChannel = originalMessage.channel
    tempMessage = originalMessage
    
    # Determine whether the user wants to modify GPT-3.5-turbo or GPT-4's
    # personality, then obtain additional argument
    if originalMessage.content.lower().startswith('inkbot4:'):
        userContent = originalMessage.content[15:].strip()
    elif originalMessage.content.lower().startswith('inkbot:'):
        userContent = originalMessage.content[14:].strip()
    else:
        userContent = originalMessage.content
    
    # If no further arguments provided, send reminder to include one
    if not userContent:
        await originalMessage.reply("Please include the pre-defined "
        "personality you would like me to adopt.")
        
    # Modify temp message contents with corresponding chatBecome() personality
    elif userContent.lower() == 'original':
        await originalChannel.send("> Changing personality to: original.")
        tempMessage.content = SELECT_ORIGINAL
    elif userContent.lower() == 'art prompt':
        await originalChannel.send("> Changing personality to: prompt writer")
        tempMessage.content = SELECT_ARTPROMPT
    elif userContent.lower() == 'lovesick':
        await originalChannel.send("> Changing personality to: lovesick")
        tempMessage.content = SELECT_LOVESICK
    elif userContent.lower() == 'uwu':
        await originalChannel.send("> Changing personality to: UWU")
        tempMessage.content = SELECT_UWU
    elif userContent.lower() == 'bro':
        await originalChannel.send("> Changing personality to: bro")
        tempMessage.content = SELECT_BRO
    
    # If argument did not correspond with a pre-defined personality, send error
    else:
        await originalMessage.reply("Sorry, that does not appear to be one of "
        "my pre-defined personalities.")
        return
    
    # Call chatBecome() with the modified tempMessage
    await chatBecome(tempMessage, modelRequested)


# chatLearn()
# -----------------------------------------------------------------------------
# Inputs:      The discord message which used this command,
#              The specification of GPT-3.5-turbo or GPT-4
# Outputs:     n/a
# Description: This function will take a specified article from Wikipedia
#              and store the first ~4000 characters of it to supplement a
#              GPT API request with additional information. Primary use is to
#              provide information past the knowledge cutoff.
# -----------------------------------------------------------------------------
async def chatLearn(originalMessage, modelRequested):
    # Determine whether the user wants to add info to GPT-3.5-turbo or GPT-4,
    # then obtain the corresponding dictionary key and subject
    if (modelRequested == "gpt-4"):
        dictionaryKey = originalMessage.channel.id * -1
        topic = originalMessage.content[14:].strip()
    else:
        dictionaryKey = originalMessage.channel.id
        topic = originalMessage.content[13:].strip()
    
    logging.info(
        f"User ID: {originalMessage.author.id} - "
        f"Requested wikipedia: {topic}\n"
    )
    
    # Make a call to wikipedia's API to obtain the wikipedia page for the topic
    response = requests.get(
        'https://en.wikipedia.org/w/api.php',
        params={
            'action': 'query',
            'format': 'json',
            'titles': topic,
            'prop': 'extracts',
            # 'exintro': True,
            'explaintext': True,
        }
    ).json()
    
    # Extract article text from result
    page = next(iter(response['query']['pages'].values()))
    page = page['extract']
    
    # Limit article text to ~4000 characters
    splitIndex = page.rfind('\n', 0, 4000)
    if splitIndex == -1:
        splitIndex = 4000
    page = page[:splitIndex]		
    
    # Store the result to webHistories + save its current contents
    webHistories[dictionaryKey] = ([
        {
            "role": "system",
            "content": 'Consider the following Wikipedia information: ' + page,
        }
    ])
    
    saveYAML("storedWebHistories.yaml", 'webHistories', webHistories)
    
    # Send confirmation
    await originalMessage.reply(f"Additional information was stored")
    
    return


# chatForget()
# -----------------------------------------------------------------------------
# Inputs:      The discord message which used this command,
#              The specification of GPT-3.5-turbo or GPT-4
# Outputs:     n/a
# Description: This function will clear the bot's memory of any conversations
#              people had with it in a specific channel, differentiating
#              between GPT-3.5-turbo conversations and GPT-4. A specific number
#              of messages may also be cleared if specified by the user.
#              The function can also be used to clear any additional 
#              information the bot stored from Wikipedia.
# -----------------------------------------------------------------------------
async def chatForget(originalMessage, modelRequested):
    originalChannel = originalMessage.channel
    
    async with originalChannel.typing():
        
        # Determine whether the user wants to clear GPT-3.5-turbo or GPT-4,
        # then obtain the corresponding dictionary key + additional arguments
        if (modelRequested == "gpt-4"):
            dictionaryKey = originalChannel.id * -1
            parameter = originalMessage.content[15:].strip()
        else:
            dictionaryKey = originalChannel.id
            parameter = originalMessage.content[14:].strip()
        
        # If the user wants to clear any additional Wikipedia information:
        if parameter == 'web':
            # Additional Wikipedia info exists for this channel + model
            if dictionaryKey in webHistories:
                webHistories.pop(dictionaryKey)
                saveYAML("storedWebHistories.yaml", 'webHistories',
                webHistories)
                
                await originalMessage.reply("Understood, clearing data "
                "obtained from the web in this channel", mention_author=False)
                
                return
            
            # Additional Wikipedia info does not exist for this channel + model
            else:
                await originalMessage.reply("Sorry, I couldn't find any data "
                "obtained from the web in this channel", mention_author=False)
                
                return
        
        # If no conversation history was found for the model in that channel:
        if dictionaryKey not in chatHistories:
            await originalMessage.reply("Sorry, I couldn't find any chat "
            "memory for this channel", mention_author=False)
            
            return
        
        # If no additional arguments were given:
        elif not parameter:
            chatHistories.pop(dictionaryKey)
            saveYAML("storedHistories.yaml", 'chatHistories', chatHistories)
            
            await originalMessage.reply("Understood, clearing chat "
            "memory from this channel and returning to my default personality",
            mention_author=False)
            
            return
        
        # If a certain number of exchanges to be cleared were specified:
        else:
            # Attempt to erase the specified number of exchanges:
            try:
                numToErase = int(parameter) * 2
                for i in range(numToErase):
                    chatHistories[dictionaryKey].pop(2)
                
                saveYAML(
                    "storedHistories.yaml",
                    'chatHistories',
                    chatHistories
                )

                await originalMessage.reply("Understood, clearing "
                f"{parameter} prompts and their responses from this channel",
                mention_author=False)
            
            # Exception: The argument was not an integer:
            except ValueError:
                await originalMessage.reply("Sorry, only integers can be "
                "specified, please try again", mention_author=False)
            
            # Exception: Argument was greater than amount of stored exchanges
            except IndexError:
                saveYAML(
                    "storedHistories.yaml",
                    'chatHistories',
                    chatHistories
                )
                await originalMessage.reply("There were less than "
                f"{parameter} exchanges in this channel, so chat memory was "
                "fully cleared", mention_author=False)


# chatSession()
# -----------------------------------------------------------------------------
# Inputs:      The discord message which used this command,
#              The specification of GPT-3.5-turbo or GPT-4
# Outputs:     n/a
# Description: This function will add the channel which the message was sent in
#              to the list of currently running "sessions", channels in which
#              the bot will reply to messages without explicitly calling it.
#              Sessions will also allow customization of other GPT parameters
#              and allow for a custom discord username/avatar through webhooks.
# -----------------------------------------------------------------------------
async def chatSession(originalMessage, modelRequested):
    # Only set up webhook for custom username/avatar in server text channels
    if originalMessage.channel.type is discord.ChannelType.text:
        webhook = await originalMessage.channel.create_webhook(
            name="inkBOTWebhook",
        )
    
    # Determine whether the user wants to create a session for GPT-3.5-turbo 
    # or GPT-4, then obtain the corresponding dictionary key
    if (modelRequested == "gpt-4"):
        dictionaryKey = originalMessage.channel.id * -1
    else:
        dictionaryKey = originalMessage.channel.id
    
    # Send warning if a session is already running in that channel
    if ((dictionaryKey in chatSessions) or ((-dictionaryKey) in chatSessions)):
        await originalMessage.channel.send("It seems like a session is "
        "already running in this channel, please end the current session "
        "before starting a new one")
    
    # Add channel information + default values for GPT/webhook to session list
    else:
        chatSessions[dictionaryKey] = (1, 0.1, 0, 0, False, "inkBOT",
        "https://cdn.discordapp.com/embed/avatars/0.png")
        saveYAML("storedSessions.yaml", 'sessionList', chatSessions)
        
        await originalMessage.channel.send("> Session started. All "
        " non-commands will now be considered prompts for the chatbot. Use "
        "`inkbot: session stop` to end your session")


# chatSessionEnd()
# -----------------------------------------------------------------------------
# Inputs:      The discord message which used this command,
#              The specification of GPT-3.5-turbo or GPT-4
# Outputs:     n/a
# Description: This function will remove the channel which the message was sent
#              in from the list of currently running "sessions". See
#              chatSesssion() for further explanation of what sessions are.
# -----------------------------------------------------------------------------
async def chatSessionEnd(originalMessage, modelRequested):
    # Determine whether the user wants to end a session for GPT-3.5-turbo 
    # or GPT-4, then obtain the corresponding dictionary key
    if (modelRequested == "gpt-4"):
        dictionaryKey = originalMessage.channel.id * -1
    else:
        dictionaryKey = originalMessage.channel.id
    
    # If a session for the corresponding GPT model is running, end it
    if dictionaryKey in chatSessions:
        # If in a server, delete the webhook which was created
        if originalMessage.channel.type is discord.ChannelType.text:
            webhooks = await originalMessage.channel.webhooks()
            for webhook in webhooks:
                if webhook.name == "inkBOTWebhook":
                    await webhook.delete()
        
        # Remove channel from session list
        chatSessions.pop(dictionaryKey)
        saveYAML("storedSessions.yaml", 'sessionList', chatSessions)
        
        await originalMessage.channel.send("The session has ended. Chatbot "
        " will no longer consider non-commands as prompts. Use `inkbot: "
        "session start` to begin a new session")
    
    # If a session for the other GPT model is running, send a warning
    elif (dictionaryKey * -1) in chatSessions:
        await originalMessage.channel.send("A session using that chatbot is "
        "not currently in place. Perhaps you meant inkbot/inkbot4?")
    
    # If no session is running in thaat channel, send a warning
    else:
        await originalMessage.channel.send("Sorry, it does not seem like a "
        "session is currently in place.")

 
# chatSessionModify()
# -----------------------------------------------------------------------------
# Inputs:      The discord message which used this command,
#              The specification of GPT-3.5-turbo or GPT-4
# Outputs:     n/a
# Description: This function allows customization of certain GPT parameters and
#              the discord username/avatar in sessions by allowing the user to
#              modify them one at a time. The parameter's value within the
#              session is modified based on the given value.
#              GPT parameter modification is artificially disabled for GPT-4
#              due to the cost of unpredictable behavior.
# -----------------------------------------------------------------------------
async def chatSessionModify(originalMessage, modelRequested):
    originalChannel = originalMessage.channel
    
    # Determine whether the user wants to modify a session for GPT-3.5-turbo 
    # or GPT-4, then obtain the corresponding dictionary key + desired settings
    if (modelRequested == "gpt-4"):
        dictionaryKey = originalChannel.id * -1
        userContent = originalMessage.content[23:].strip
    else:
        dictionaryKey = originalChannel.id
        userContent = originalMessage.content[22:].strip()
    
    # If there's no session for that model running in the channel, send warning
    if dictionaryKey not in chatSessions:
        await originalChannel.send("Please begin a session using `inkbot: "
        "session start` before using this command.")
        return
    
    # Obtain the session's current OpenAI + discord parameters
    (tempWanted, toppWanted, presenceWanted, frequencyWanted, customWanted,
    nameWanted, pictureWanted) = chatSessions[dictionaryKey]
    
    # Change the GPT temperature Setting if desired
    if userContent.lower().startswith('temperature'):
        if (modelRequested == "gpt-4"):
            await originalChannel.send(f"Sorry, but only custom names/avatars "
            "are available for GPT-4 at this time")
            return
        userContent = userContent[11:]
        tempWanted = float(userContent)
        if (tempWanted >= 0) and (tempWanted <= 1.5):
            toppWanted = 1
            await originalChannel.send(f"Setting temperature to {tempWanted}")
        else:
            await originalChannel.send(f"Value must be between [0,1.5]")
    
    # Change the GPT top_p Setting if desired
    elif userContent.lower().startswith('top_p'):
        if (modelRequested == "gpt-4"):
            await originalChannel.send(f"Sorry, but only custom names/avatars "
            "are available for GPT-4 at this time")
            return
        userContent = userContent[5:]
        toppWanted = float(userContent)
        if (toppWanted > 0) and (toppWanted <= 1):
            tempWanted = 1
            await originalChannel.send(f"Setting top_p to {toppWanted}")
        else:
            await originalChannel.send(f"Value must be between (0,1]")
            
    # Change the GPT presence_penalty Setting if desired
    elif userContent.lower().startswith('presencepenalty'):
        if (modelRequested == "gpt-4"):
            await originalChannel.send(f"Sorry, but only custom names/avatars "
            "are available for GPT-4 at this time")
            return
        userContent = userContent[15:]
        presenceWanted = float(userContent)
        if (presenceWanted >= -2) and (presenceWanted <= 2):
            await originalChannel.send(f"Setting presence_penalty to "
            f"{presenceWanted}")
        else:
            await originalChannel.send(f"Value must be between [-2,2]")
    
    # Change the GPT frequency_penalty Setting if desired
    elif userContent.lower().startswith('frequencypenalty'):
        if (modelRequested == "gpt-4"):
            await originalChannel.send(f"Sorry, but only custom names/avatars "
            "are available for GPT-4 at this time")
            return
        userContent = userContent[16:]
        frequencyWanted = float(userContent)
        if (frequencyWanted >= -2) and (frequencyWanted <= 2):
            await originalChannel.send(f"Setting frequency_penalty to "
            f"{frequencyWanted}")
        else:
            await originalChannel.send(f"Value must be between [-2, 2]")
    
    # Change the Discord Webhook's display name Setting if desired
    elif userContent.lower().startswith('name'):
        if originalChannel.type is not discord.ChannelType.text:
            await originalChannel.send(f"Sorry, custom names and avatars are " 
            "only available in normal server text channels")
            return
        nameWanted = userContent[5:]
        customWanted = True
        await originalChannel.send(f"Setting name to {nameWanted}")
        
    # Change the Discord Webhook's avatar Setting if desired
    elif userContent.lower().startswith('avatar'):
        if originalChannel.type is not discord.ChannelType.text:
            await originalChannel.send(f"Sorry, custom names and avatars are "
            "only available in normal server text channels")
            return
        pictureWanted = userContent[7:]
        customWanted = True
        await originalChannel.send(f"Setting avatar to {pictureWanted}")
    
    # If the desired setting to change was not found, send warning
    else:
        await originalChannel.send(f"Sorry, could not find that "
        "setting. The available settings are: `temperature`, `top_p`, "
        "`presencepenalty`, `frequencypenalty`, `name`, and `avatar`.")
    
    # Update session values
    chatSessions[dictionaryKey] = (tempWanted, toppWanted, presenceWanted,
    frequencyWanted, customWanted, nameWanted, pictureWanted)
    saveYAML("storedSessions.yaml", 'sessionList', chatSessions)


# chatPost()
# -----------------------------------------------------------------------------
# Inputs:      The discord message which used this command,
#              The specification of GPT-3.5-turbo or GPT-4
# Outputs:     n/a
# Description: This function will extract the prompt provided by the user in
#              their message and calls the GPT generation function with the 
#              relevant parameters. It also handles moderation, the final reply
#              to the response, and storage to history.
# -----------------------------------------------------------------------------
async def chatPost(originalMessage, modelRequested):
    originalChannel = originalMessage.channel
    
    async with originalChannel.typing():
        
        # Check if the prompt was safe
        promptSafe = await checkModeration(originalMessage)
        
        # If the prompt passes moderation, begin response generation process
        if promptSafe:
            
            # Extract the prompt to respond to from the original message
            if originalMessage.content.lower().startswith('inkbot,'):
                userContent = originalMessage.content[7:].strip()
            elif originalMessage.content.lower().startswith('inkbot4,'):
                userContent = originalMessage.content[8:].strip()
            else:
                userContent = originalMessage.content
            
            logging.info(
                f"User ID: {originalMessage.author.id} - "
                f"Submitted Prompt: {userContent}\n"
            )
            
            # Determine whether the user wants to use GPT-3.5-turbo or GPT-4,
            # then obtain the corresponding dictionary key
            if (modelRequested == "gpt-4"):
                dictionaryKey = originalChannel.id * -1
            else:
                dictionaryKey = originalChannel.id

            # If no history for that channel, create one
            if dictionaryKey not in chatHistories:
                chatHistories[dictionaryKey] = defaultHistoryEntry.copy()
            
            # If chatbot activated due to a session, obtain custom variables
            if dictionaryKey in chatSessions:
                (tempWanted, toppWanted, presenceWanted,
                 frequencyWanted, customWanted, nameWanted,
                 pictureWanted) = chatSessions[dictionaryKey]
            
            # If chatbot activated normally, use default GPT variables
            else:
                tempWanted = 1
                toppWanted = 0.1
                presenceWanted = 0
                frequencyWanted = 0
                customWanted = False
            
            # Obtain new date/time information
            currentDate = datetime.datetime.now().strftime("%B %d, %Y")
            currentTime = datetime.datetime.now().strftime("%I:%M:%S %p")
            responseDateTime = (f"The current date is {currentDate}."
            f"The current time is {currentTime} (Eastern Time).")
            
            # Obtain information about sender
            senderInformation = (f"The message comes from discord user "
            f"\"{originalMessage.author.global_name}\", who goes by the nickname "
            f"\"{originalMessage.author.nick}\" in your current server. If they "
            f"asked you to call them by a different name, please do so.")
            
            # Generate a response from OpenAI and scan it
            response = await generateCompletion(
                originalMessage, dictionaryKey, userContent, responseDateTime,
                senderInformation, modelRequested, tempWanted, toppWanted,
                presenceWanted, frequencyWanted
            )
            
            tempMessage = originalMessage
            tempMessage.content = response
            responseSafe = await checkModeration(tempMessage)

            if responseSafe:
                
                logging.info(f"Response: {response}\n")
                
                # Artificially limit GPT-4 history size to save cost
                # If GPT-4, check if there are 12 or more things in history
                if ((len(chatHistories[dictionaryKey]) >= 12) and 
                     (modelRequested == "gpt-4")):
                    # Erase two oldest items in GPT-4 exchange history
                    # Excludes personality + message format information
                    for i in range(2):
                        chatHistories[dictionaryKey].pop(2)
                
                # Extend chatHistories with new message/response exchange
                chatHistories[dictionaryKey].extend([
                    {"role": "user", "content": senderInformation
                      + f"\nThe message sent was: " + userContent},
                    {"role": "assistant", "content": response},
                ])
                
                # Save the updated contents of chatHistories to its YAML file
                saveYAML(
                    "storedHistories.yaml",
                    'chatHistories',
                    chatHistories
                )
                
                # If this is a session and a custom name/avatar have been set
                if (customWanted):
                    # Send as the customized profile
                    webhooks = await originalChannel.webhooks()
                    for webhook in webhooks:
                        if webhook.name == "inkBOTWebhook":
                            await webhook.send(
                                response,
                                username=nameWanted,
                                avatar_url=pictureWanted,
                            )
                    return
                
                # Add delay if called by bot
                if originalMessage.author.bot:
                    asyncio.sleep(10)
                
                # Use sendLongMessage if the response is over 2000 characters
                if len(response) > 2000:
                    await sendLongMessage(originalMessage, response)
                
                # If response was under 2000 characters, reply normally
                else:
                    if originalMessage.author.bot:
                        await originalMessage.reply(response,
                        mention_author=True)
                    else:
                        await originalMessage.reply(response,
                        mention_author=False)
            
            # If the response fails moderation
            else:
                logging.info(f"Unsafe Response Generated: {response}\n")
                await originalMessage.reply("Sorry, my generated response was "
                "unsafe, I'm not allowed to send this", mention_author=False)
        
        # If the prompt fails moderation
        else:
            logging.info(
                f"User ID: {originalMessage.author.id} - "
                f"Submitted Unsafe Prompt: {originalMessage.content}\n"
            )
            
            await originalMessage.channel.send(f"Sorry, your prompt was "
            f" unsafe. Please review the usage policy:\n "
            f"<https://openai.com/policies/usage-policies>")


# generateCompletion()
# -----------------------------------------------------------------------------
# Inputs:      
# Outputs:     A string with the response from OpenAI (or an error message)
# Description: This function takes multiple parameters and uses them to request
#              a completion from OpenAI's GPT API. The completion request runs
#              twice, first to determine if the bot needs to attach additional
#              information to the request, then to actually generate it.
# -----------------------------------------------------------------------------
async def generateCompletion(originalMessage, dictionaryKey, messageText,
responseDateTime, senderInformation, modelWanted, tempWanted, toppWanted,
presenceWanted, frequencyWanted):	
    
    # Set up variable to store data to send to determine sub-system inclusion
    subsystemCheckText = ([{"role": "system", "content": SUBSYS_PROMPT}]
                          + [{"role": "user", "content": messageText}])
    
    # Set up variable to store data to send for completion
    # No matter what, will always include history and the prompt, may include
    # additional web information
    if dictionaryKey not in webHistories:
        completionText = (chatHistories[dictionaryKey]
                          + [{"role": "user", "content": messageText}])
    else:
        completionText = (chatHistories[dictionaryKey]
                          + webHistories[dictionaryKey]
                          + [{"role": "user", "content": messageText}])
    
    # Run prompt through Completions API to determine sub-system inclusion
    try:
        subSysCompletion = await openai.ChatCompletion.acreate(
            model='gpt-4',
            messages=subsystemCheckText,
            temperature=1,
            top_p=1,
            presence_penalty=0,
            frequency_penalty=0
        )
    
    # If something went wrong with sub-system inlusion check, alert sender
    except:
        subSysCompletion = "[ERROR]"
    
    # Set up variable to store sub-system inclusion results
    # Sender Information being treated as a sub-system which is always on
    compSubSys = [{"role": "system", "content": senderInformation}]
    
    # If ran into ERROR, continue but without additional information
    if subSysCompletion == "[ERROR]":
        compSubSys = ([{"role": "system", "content": ("Requsted supplemental "
        "information could not be obtained due to an error.")}])
        
        await originalMessage.channel.send(f"> **Error Retrieving "
        f"Additional Info:** Attempting Response Anyway...")
        
        logging.info(f"Subsystem check resulted in [ERROR]\n")
    
    # If DATETIME requested, add date/time information to the prompt
    if "[DATETIME]" in subSysCompletion.choices[0].message.content.strip():
        compSubSys = ([{"role": "system", "content": responseDateTime}]
                      + compSubSys)
        
        await originalMessage.channel.send(f"> **Retrieved Additional Info:**"
        f" Current date and time")
        
        logging.info(f"Retrieved [DATETIME]\n")
    
    # If MEMBERLIST requested, add non-bot member information to the prompt
    if "[MEMBERLIST]" in subSysCompletion.choices[0].message.content.strip():
        memberList = "These people are in the discord server with you:\n\n"
        
        for member in originalMessage.guild.members:
            if ((not member.bot) or (member.id == INKDROID_ID) or
               (member.id == INKBOT_ID)):
                nickname = member.nick if member.nick else member.display_name
                memberList += (f"{member.name}, who also goes by {nickname}."
                f"If necessary, their ID is {member.id}.\n\n")
        
        compSubSys = [{"role": "system", "content": memberList}] + compSubSys
        
        await originalMessage.channel.send(f"> **Retrieved Additional Info:**"
        f" Server Member List")
        
        logging.info(f"Retrieved [MEMBERLIST]\n")
    
    # Add sub-system results to the data to send for completion
    completionText = compSubSys + completionText
        
    # Predict completionText token count
    encoding = tiktoken.encoding_for_model(modelWanted)
    tokenPrediction = 0
    for message in completionText:
        tokenPrediction += 4
        for role, content in message.items():
            tokenPrediction += len(encoding.encode(content))
    
    logging.info(f"Predicted Prompt Token Count {tokenPrediction} \n")
    
    # Erase items from memory + re-compile if token prediction surpasses limit
    if (tokenPrediction >= 4000):
        # Delete items from memory
        for i in range(8):
            chatHistories[dictionaryKey].pop(2)
        
        # Send warning
        await originalMessage.channel.send(f"> **Warning:** Prompt will "
        f"exceed my token limit, a few prompts/responses have been deleted "
        f"from memory to make room for the prompt and response")
        
        # Re-compile data to send to OpenAI
        if dictionaryKey not in webHistories:
            completionText = (chatHistories[dictionaryKey]
                            + [{"role": "user", "content": messageText}])
        else:
            completionText = (chatHistories[dictionaryKey]
                            + webHistories[dictionaryKey]
                            + [{"role": "user", "content": messageText}])
        
        completionText = compSubSys + completionText
    
    # Attempt to generate a response
    try:
        Completion = await openai.ChatCompletion.acreate(
            model=modelWanted,
            messages=completionText,
            temperature=tempWanted,
            top_p=toppWanted,
            presence_penalty=presenceWanted,
            frequency_penalty=frequencyWanted
        )
    except InvalidRequestError:
        return ("Something went wrong, most likely related to memory. Try "
            "`inkbot: forget` then try again")
    except APIError:
        return ("There is currently an issue with the OpenAI Servers. See "
        "https://status.openai.com/")
    except APIConnectionError:
        return ("There was an issue connecting to the OpenAI Servers, try "
        "again later")
    except RateLimitError:
        return ("Sorry, the rate limit has been or budget for this month has "
        "been exceeded. Please try again, if this message continues to "
        "appear, it it most likely the latter option")
    except Timeout:
        return "Sorry, the request timed out, please try again"
    except ServiceUnavailableError:
        return ("There is currently an issue with the OpenAI Servers. See "
        "https://status.openai.com/")
    except AuthenticationError:
        return "There appears to be a problem with the API key"
    
    # If the response is likely to have cut off in the middle, warn the sender
    if (Completion.usage.total_tokens >= 4097):
        await originalMessage.channel.send(f"> **Warning:** It is very "
        "likely that this response has cut off randomly in the middle.")
    
    logging.info(f"\nPrompt Tokens: {Completion.usage.prompt_tokens}")
    logging.info(f"Completion Tokens: {Completion.usage.completion_tokens}")
    logging.info(f"Total Tokens: {Completion.usage.total_tokens}\n")
    
    return Completion.choices[0].message.content.strip()


# checkModeration()
# -----------------------------------------------------------------------------
# Inputs:      A discord message
# Outputs:     A boolean value
# Description: This function takes a discord message and returns false if the
#              prompt's contents pass OpenAI's Moderations Endpoint.
#              If an error occurs in the process, the function defaults to 
#              considering the message flagged.
# -----------------------------------------------------------------------------
async def checkModeration(inputMessage):
    try:
        response = await openai.Moderation.acreate(inputMessage.content)

        results = response["results"]
        flagged = results[0]["flagged"]
        
        logging.info(f"Were scanned contents flagged? {flagged}\n")
        
        return not flagged
    
    
    except APIError:
        await inputMessage.reply(
        "There is currently an issue with the OpenAI Servers. Please "
        "disregard the following message about being flagged, and see the "
        "following page for more information: https://status.openai.com/")
    except APIConnectionError:
        await inputMessage.reply("There was an issue connecting to the OpenAI "
        "Servers, please try again later. Please disregard the following "
        "message about being flagged.")
    except RateLimitError:
        await inputMessage.channel.send("Sorry, the rate limit has been "
        "exceeded or you have exceeded the budget for this month, please try "
        "again. If this message continues to appear, the latter option is "
        "likely. Please disregard the following message about being flagged.")
    except Timeout:
        await inputMessage.reply("Sorry, the request timed out, please try "
        "again. Please disregard the following message about being flagged.")
    except ServiceUnavailableError:
        await inputMessage.reply("There is currently an issue with the OpenAI "
        "Servers. Please disregard the following message about being flagged, "
        "and see the following page for more information: "
        "https://status.openai.com/")
    except AuthenticationError:
        await inputMessage.reply("There appears to be a problem with the API " 
        "key. Please disregard the following message about being flagged.")
    
    # If here, then there was some error checking the message. Return false,
    # the prompt was "not safe", to prevent further response generation
    return False


# dallePost()
# -----------------------------------------------------------------------------
# Inputs:      The discord message which used this command
# Outputs:     n/a
# Description: This function will generate an image using OpenAI's DALL·E based
#              on a prompt provided by the user. The prompt must pass
#              moderation in order for generation to occur.
#              The generated image will be 1024x1024 pixels.
# -----------------------------------------------------------------------------
async def dallePost(originalMessage):
    
    originalChannel = originalMessage.channel
    
    async with originalChannel.typing():
        # Attempt to generate the image:
        try:
            thePrompt = originalMessage.content[12:].strip()

            # Send the prompt to OpenAI's API
            resultImage = await openai.Image.acreate(
                prompt = thePrompt, 
                n = 1, 
                size = "1024x1024" # Can be 256, 512, 1024
            )
            
            # Store the request + response
            logging.info(
                f"User ID: {originalMessage.author.id} - "
                f"Requested Image: {originalMessage.content}\n"
                f"Received {resultImage['data'][0]['url']}\n"
            )
            
            # Send the result
            await originalChannel.send("> **Prompt:** " + thePrompt)
            await originalChannel.send(resultImage['data'][0]['url'])
        
        # If generation fails due to the prompt failing moderation:
        except InvalidRequestError:
            await originalMessage.reply("Sorry, your prompt was unsafe. "
            "Please review the content policy: "
            "<https://labs.openai.com/policies/content-policy>")
            
            logging.info(
                f"User ID: {originalMessage.author.id} - "
                f"Requested Unsafe Image Prompt: {originalMessage.content}"
            )