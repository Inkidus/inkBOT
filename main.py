from functions import *
from strings import *


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] - %(message)s',
    handlers=[
        logging.FileHandler("inkbot_logs.txt"),
        logging.StreamHandler()
    ]
)


load_dotenv('values.env')
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

openai.api_key = OPENAI_API_KEY


free_game_channels = [
    int(os.getenv('CHANNEL1')),
    int(os.getenv('CHANNEL2')),
    int(os.getenv('CHANNEL3')),
    int(os.getenv('CHANNEL4')),
    int(os.getenv('CHANNEL5')),
    int(os.getenv('CHANNEL6'))
]

free_game_ids = int(os.getenv('FREEGAMEID'))


chat_histories = OrderedDict()

default_system_message = [
    {"role": "system", "content": DEFAULT_PERSONALITY},
    {"role": "system", "content": TEXT_FORMAT},
]


intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.typing = False
intents.presences = False
client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix=':', intents=intents)


@client.event
async def on_ready():
    logging.info(f"Successfully logged in as {client.user}\n")


@client.event
async def on_message(message):
    if message.author == client.user:
        return


    if message.content.lower() == 'send free games' and message.author.id == free_game_ids:
        async with message.channel.typing():
            await freegamespost()


    if message.content.lower().startswith('inkbot: help'):
        async with message.channel.typing():
            user_content  = message.content[12:].strip()
            if not user_content:
                await message.channel.send(DEFAULT_HELP)
            elif user_content.lower() == 'become':
                await message.channel.send(BECOME_HELP)
            elif user_content.lower() == 'forget':
                await message.channel.send(FORGET_HELP)
            elif user_content.lower() == 'draw':
                await message.channel.send(DRAW_HELP)
            elif user_content.lower() == 'join':
                await message.channel.send(JOIN_HELP)
            elif user_content.lower() == 'leave':
                await message.channel.send(LEAVE_HELP)
            elif user_content.lower() == 'tts':
                await message.channel.send(TTS_HELP)
            else:
                await message.channel.send(UNKNOWN_HELP)

    if message.content.lower() == 'inkbot: join':
        if message.author.voice is not None:
            try:
                voice_client = await message.author.voice.channel.connect()
                await message.channel.send(f"Understood, joining {message.author.voice.channel.name} as soon as possible...")
            except discord.errors.ClientException:
                await message.channel.send("I'm sorry, it appears I am already in another voice channel")
        else:
            await message.channel.send("I'm sorry, but you do not appear to be in a voice channel at this time")
    
    if message.content.lower() == 'inkbot: leave':
        if message.guild.voice_client:
            await message.guild.voice_client.disconnect()
            await message.channel.send(f"Alright, leaving the voice chat now...")
        else:
            await message.channel.send("I'm sorry, but I do not appear to be connected to a voice channel at this time")

    if message.content.lower().startswith('inkbot: tts'):
        if not message.author.voice:
            await message.channel.send("You're not in a voice channel.")
        if not message.guild.voice_client:
            await message.channel.send("I'm sorry, but I do not appear to be connected to a voice channel at this time")
            
        user_content  = message.content[11:].strip()
        await text_to_speech(user_content, message)


    if message.content.lower().startswith('inkbot: forget'):
        if message.channel.id in chat_histories:
            user_content  = message.content[14:].strip()
            if not user_content:
                chat_histories.pop(message.channel.id)
                await message.channel.send("Understood, clearing all memory from this channel and reverting to my default personality.")
            else:
                numToErase = int(user_content) * 2
                for i in range(numToErase):
                    chat_histories[message.channel.id].pop(2)
                await message.channel.send("Understood, clearing " + user_content + " prompts and their responses from this channel.")
        else:
            await message.channel.send("Sorry, I couldn't find any memories from this channel.")


    if message.content.lower().startswith('inkbot: become'):
        logging.info(f"User ID: {message.author.id} - Submitted New Personality: {message.content}\n")
        async with message.channel.typing():
            user_content  = message.content[14:].strip()
            
            custom_system_message = [
                {"role": "system", "content": user_content},
                {"role": "system", "content": TEXT_FORMAT},
            ]

            if message.channel.id not in chat_histories:
                chat_histories[message.channel.id] = custom_system_message.copy()
                await message.channel.send("Successfully adopted my new personality.")
            else:
                chat_histories.pop(message.channel.id)
                chat_histories[message.channel.id] = custom_system_message.copy()
                await message.channel.send("Successfully cleared all memories of this channel and adopted my new personality.")


    if message.content.lower().startswith('inkbot: draw'):
        async with message.channel.typing():
            try:
                image_response = openai.Image.create(
                    prompt = message.content[12:].strip(), 
                    n = 1, 
                    size = "1024x1024" # Can be 256, 512, 1024
                )
                

                logging.info(f"User ID: {message.author.id} - Requested Image: {message.content}, ")
                logging.info(f"received {image_response['data'][0]['url']}\n")
                await message.channel.send("Image generated!\n**Prompt:** " + message.content[12:].strip() )
                await message.channel.send(image_response['data'][0]['url'])
            except InvalidRequestError:
                await message.channel.send("Sorry, your prompt was unsafe, I couldn't generate an image.")
                logging.info(f"User ID: {message.author.id} - Submitted Unsafe Image Prompt: {message.content}, ")
       

    if message.content.lower().startswith('inkbot,') or message.content.lower().startswith('dinklebot,'):
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


client.run(DISCORD_TOKEN)