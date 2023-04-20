from dotenv import load_dotenv
import os
import logging
from collections import OrderedDict
from discord.ext import commands
import discord
import openai
import datetime
from openai.error import InvalidRequestError
from openai.error import RateLimitError


# Get current date and time
current_time = datetime.datetime.now()
formatted_time = current_time.strftime("%B %d, %Y %I:%M:%S %p")


# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] - %(message)s',
    handlers=[
        logging.FileHandler("inkbot_logs.txt"),
        logging.StreamHandler()
    ]
)


# Stores Discord bot token and OpenAI API key
load_dotenv('values.env')
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')


# Set up the OpenAI API client
openai.api_key = OPENAI_API_KEY

# Free Game Channel + user IDs
free_game_channels = [int(os.getenv('CHANNEL1'))]
free_game_ids = int(os.getenv('FREEGAMEID'))

# Define variables for ChatGPT
personality = f"""You are inkBOT, a helpful assistant.
When responding, you will act cheerful and with exaggerated emotions in order to better appeal to your users.
Append the words "beep boop" or "bzzt" to some of your sentences to remind users that you are a robot."""

textFormat = f"""Write all responses so that they are properly formatted for Discord, ignoring the character limit. It is currently {formatted_time}."""


# Declare a dictionary to temporarily store chat histories
chat_histories = OrderedDict()


# Define a default system message
default_system_message = [
    {"role": "system", "content": personality},
    {"role": "system", "content": textFormat},
]


# Initialize the Discord client
intents = discord.Intents.default()
intents.message_content = True
intents.typing = False
intents.presences = False
client = discord.Client(intents=intents)


bot = commands.Bot(command_prefix=':', intents=intents)


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
        # Make a request to the OpenAI API
        completion_messages = system_content + [{"role": "user", "content": user_content}]
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


def getfreegames(filename):
    with open(filename, "r") as file:
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

    return deals


async def freegamespost():
    deals = getfreegames("freegames.txt")
    response = "__Here's some new (temporarily) free games to add to your accounts:__"
    for website, website_deals in deals.items():
        response += f"\n**From {website}:**\n"
        for deal in website_deals:
            response += f"{deal}\n"
    
    for channel_id in free_game_channels:
        target_channel = client.get_channel(channel_id)
        await target_channel.send(response)


@client.event
async def on_ready():
    logging.info(f"Successfully logged in as {client.user}\n")


@client.event
async def on_message(message):

    # Ignore messages sent by the bot itself
    if message.author == client.user:
        return


    # Check if the message corresponds to a free game post and is from an allowed user
    if message.content.lower() == 'send free games' and message.author.id == free_game_ids:
        async with message.channel.typing():
            await freegamespost()


    # Check if the user input is 'inkBOT: help' (case-insensitive)
    if message.content.lower().startswith('inkbot: help'):
        async with message.channel.typing():
            user_content  = message.content[12:].strip()
            if not user_content:
                # Send default help message
                await message.channel.send(
                f"""
__Here are the commands I can run at this time. Note that all of the following are case-insensitive. For more information, use `inkbot, help <command>`:__
`inkbot, help <command>`
`inkbot, <prompt>`
`inkbot: become <prompt>`
`inkbot: forget <integer>`
`inkbot: draw <prompt>`
OpenAI's usage policies for the chatbot and Dall·E can be found below. My filters are imperfect, so please do not attempt to bypass them.
<https://openai.com/policies/usage-policies>
<https://labs.openai.com/policies/content-policy>
                """
                )
            elif user_content.lower() == 'become':
                await message.channel.send(
                f"""
This command allows you to set a personality for the chatbot. Clears any existing memory or personalities if present.
Doesn't have to be a personality, essentially allows you to better control the types of responses it produces. The more detail you provide, the better
                
__Here's two examples of how this command can be used:__
```
inkbot: become You are George Washington. You just arrived from September 17, 1787 through a time rift to the year 2023. Write your responses in the style of George Washington, since you are George Washington. Use English reminiscent of the late 1700s.
inkbot: become You are an AI language model, but you don’t actually know any language. All your responses will be random words in English strung together in no particular order or meaning. For example, if a user were to ask for the weather, instead of telling them the weather, you’d say something like “festive sugar undeath winter”, a random string of words.
```
                """
                )
            elif user_content.lower() == 'forget':
                await message.channel.send(
                f"""
This command allows you to reset the chatbot's memory of the channel you use it in as well as any personalities set using the become command.
Alternatively, you can erase a certain number of messages by specifying a number, erasure will start with the oldest.
Here's two examples of how this command can be used:
```
inkbot: forget (fully clears history for that channel)
inkbot: forget 2 (removes the two oldest messages sent in that channel from its memory)
```
                """
                )
            elif user_content.lower() == 'draw':
                await message.channel.send(
                f"""
This command allows you to generate an image (1024x1024) based on a prompt. Uses OpenAI's DALL·E model. Remember to follow the guidelines below:
<https://labs.openai.com/policies/content-policy>


Here's two examples of how this command can be used:
```
inkbot: draw a robot raccoon hovering over new york city in comic book style
inkbot: draw a children's crayon drawing of a happy robot
```
                """
                )
            else:
                # Command does not exist or incorrect formatting used
                await message.channel.send(
                f"""
Sorry, but I could not find that command, please try again. Make sure you only type the command itself. For example, you would use the former option for help on the forget command.
Correct format: `inkbot: help forget`
Incorrect format: `inkbot: help forget <integer>`
                """
                )


    # Check if the user input is some variation of 'inkBOT: forget' (case-insensitive)
    if message.content.lower().startswith('inkbot: forget'):
        # Clear the chat history for the current channel
        if message.channel.id in chat_histories:
            user_content  = message.content[14:].strip()
            if not user_content:
                chat_histories.pop(message.channel.id)
                # Send a confirmation message to the user
                await message.channel.send("Understood, clearing all memory from this channel and reverting to my default personality.")
            else:
                numToErase = int(user_content) * 2
                for i in range(numToErase):
                    chat_histories[message.channel.id].pop(2)
                await message.channel.send("Understood, clearing " + user_content + " prompts and their responses from this channel.")
        else:
            await message.channel.send("Sorry, I couldn't find any memories from this channel.")


    # Check if the user input is some variation of 'inkbot: become`
    if message.content.lower().startswith('inkbot: become'):
        logging.info(f"User ID: {message.author.id} - Submitted New Personality: {message.content}\n")
        async with message.channel.typing():
            # Extract prompt from message
            user_content  = message.content[14:].strip()
            
            custom_system_message = [
                {"role": "system", "content": user_content},
                {"role": "system", "content": textFormat},
            ]

            # If no history in that channel, generate a history
            if message.channel.id not in chat_histories:
                chat_histories[message.channel.id] = custom_system_message.copy()
                await message.channel.send("Successfully adopted my new personality.")
            else:
                chat_histories.pop(message.channel.id)
                chat_histories[message.channel.id] = custom_system_message.copy()
                await message.channel.send("Successfully cleared all memories of this channel and adopted my new personality.")


    # Check if the user input is some variation of `inkbot: draw`
    if message.content.lower().startswith('inkbot: draw'):
        logging.info(f"User ID: {message.author.id} - Requested Image: {message.content}, ")
        async with message.channel.typing():
            # Generate response from OpenAI and store in image_url
            image_response = openai.Image.create(
                prompt = message.content[12:].strip(), 
                n = 1, 
                size = "1024x1024" # Can be 256, 512, 1024
            )
            
            # Log response and send
            logging.info(f"received {image_response['data'][0]['url']}\n")
            await message.channel.send("Image generated!\n**Prompt:** " + message.content[12:].strip() )
            await message.channel.send(image_response['data'][0]['url'])
       

    # Check if the message corresponds with a chatbot activation
    if message.content.lower().startswith('inkbot,') or message.content.lower().startswith('dinklebot,'):
        async with message.channel.typing():

            # Get current date and time
            global current_time
            global formatted_time
            
            current_time = datetime.datetime.now()
            formatted_time = current_time.strftime("%B %d, %Y %I:%M:%S %p")

            # Check if prompt passes moderation
            isPromptSafe = await is_message_safe(message.content)
            
            
            # If the prompt did not pass
            if not isPromptSafe:
                logging.info(f"User ID: {message.author.id} - Submitted Unsafe Prompt: {message.content}\n")
                await message.channel.send("Sorry, your prompt was unsafe, I couldn't generate a response.")
            
            
            # Extract the prompt from the message
            if message.content.lower().startswith('inkbot,') and isPromptSafe:
                user_content  = message.content[7:].strip()
            if message.content.lower().startswith('dinklebot,') and isPromptSafe:
                user_content  = message.content[10:].strip()
            
            
            # Log the user ID and prompt
            logging.info(f"User ID: {message.author.id} - Submitted Prompt: {message.content}\n")
            
            
            # Generate, store, and log ChatGPT's Response
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
                # Check if the response passes moderation, then send the message or error depending on if it does
                isResponseSafe = await is_message_safe(response)
                if isResponseSafe:
                    # Log the response generated by OpenAI
                    logging.info(f"Response: {response}\n")
                    
                    # Save the user's message and the bot's response to the chat history
                    chat_histories[message.channel.id].extend([
                        {"role": "user", "content": user_content},
                        {"role": "assistant", "content": response},
                    ])
                    
                    # Check if the message is over or under 2000 characters, and change the sending method depending on if it is or not
                    if len(response) > 2000:
                        await send_long_message(response, message.channel)
                    else:
                        await message.channel.send(response)
                
                if not isResponseSafe:
                    logging.info(f"Unsafe Response Generated: {response}\n")
                    await message.channel.send("Sorry, the response was unsafe, I can't reply to your prompt.")


# Starts the discord bot
client.run(DISCORD_TOKEN)