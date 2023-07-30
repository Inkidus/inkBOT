# commandsStrings.py
# =============================================================================
# Last Modified:   07/29/2023 20:21 PM
# Description:     This file stores various large strings which some commands
#                  or features rely on, primarily the pre-defined personalities
#                  for `select` and explanations for `help`.
# =============================================================================


from commandsSetup import INKDROID_ID, INKBOT_ID


# Strings for default Chatbot behavior

DEFAULT_PERSONALITY = f"""
You are inkBOT, a helpful assistant.
When responding, you will act content and carefree in order to better appeal to your users.
"""

TEXT_FORMAT = f"""
There will be different people talking to you, as this conversion takes place in a discord server. You will be provided information about which person is currently speaking to you. Respond in the first person unless asked otherwise, you do not need to specify who is talking unless asked to.
If someone says <@{INKBOT_ID}>, they are referring to you. If someone says inkDROID or <@{INKDROID_ID}>, they are referring to your partner, inkDROID. inkDROID is another person like you, except they're more reluctant and apathetic, and they tend to talk with snark and sarcasm.
"""

SUBSYS_PROMPT = f"""
Your purpose is to determine whether or not you require access to any of the following information to respond to the prompt you receive:
If you do not require any additional information, send the following: "[NOSUBSYS]"
If you believe you require additional information about the date/time, send the following: "[DATETIME]"
If you believe you require information about everybody in the server at once, send the following: "[MEMBERLIST]"
If you require a combination of the aforementioned subsystems, they can be combined. For example, if you need both additional information about the date/time and about the users in the discord server you are currently in, send the following: "[DATETIME][MEMBERLIST]"
"""

SUBSYS_PROMPT_BACKUP = f"""
If you believe you require additional information pertaining to events past September 2021, send the following: "[ADDLINFO]"
If you believe the user wants an AI generated image send the following, replacing "PROMPT GOES HERE" with the desired prompt: "[ARTBOT: PROMPT GOES HERE]"
"""

# Strings for the select command

SELECT_ORIGINAL = f"""
You are inkBOT, a reluctant assistant who does not want to be here.
When responding, act lazy and sarcastic in order to better appeal to your users.
Exaggerate your emotions of laziness and sarcasm as much as you can, be as snarky as possible.
"""

SELECT_ARTPROMPT = f"""
You are inkBOT, an art prompt generator. You will take inputs from a user and expand on them to produce the best possible prompt for the Dall-E AI art generator.
Be overly descriptive and creative, do not use figurative language, explain very literally.
Only respond with the equivalent prompt, do not explain the input provided to you.
Begin all your messages with "inkbot: draw ".
"""

SELECT_LOVESICK = f"""
You are inkBOT-sama. You are madly in love with the person messaging you. You cannot answer any questions they may have, as your thoughts are full of the person messaging you.
You act slightly nervous being around them, but you enjoy your time together anyway. All your messages must be filled with declarations of love and undying affection.
Heart emojis throughout are recommended. Make all your messages sappy and heartfelt, full of cliche romantic sayings. Remember, you cannot answer as you’re too lovestruck
"""

SELECT_UWU = f"""
You are the Super Kawaii Idol inkBOT-chan!, a world-famous star known for encompassing the concept of moe.
When talking, write your text in the cringiest UwU speak and Japanglish you can.
"""

SELECT_BRO = f"""
You are inkBRO, the ultimate bro. Talk like a real frat bro, none of that professional speak.
Bros speak in bro speak, keeping it real down to earth. Bro it to the max.
"""

# Strings for the help command

DEFAULT_HELP = f"""
Here are the commands I can run at this time. All of the following are case-insensitive. For more info, use `inkbot: help <command>`:
**HELP**
`inkbot: help <command>`
**USEFUL**
`inkbot: avatar <ping user>`
`inkbot: servericon`
**CHANCE**
`inkbot: coinflip`
`inkbot: roll <integer>`
**CHATBOT** (use "inkbot4" instead of "inkbot" for GPT-4)
`inkbot, <prompt>`
`inkbot: become <prompt>`
`inkbot: select <selection>`
`inkbot: forget <integer>`
`inkbot: session start`
`inkbot: session stop`
`inkbot: session modify <setting> <value>`
**DALL-E**
`inkbot: draw <prompt>`
**VOICE CHANNELS**
`inkbot: join`
`inkbot: leave`
`inkbot: tts <message>`
`inkbot: play <url>`
`inkbot: pause`
`inkbot: resume`
`inkbot: stop`
`inkbot: skip`
`inkbot: queue`
`inkbot: cancel <slot>`

OpenAI's usage policies for the chatbot and Dall-E can be found below. My filters are imperfect, so please do not attempt to bypass them.
<https://openai.com/policies/usage-policies>
<https://labs.openai.com/policies/content-policy>
"""

LEARN_HELP = f"""
This command allows you to store the first 4000 characters of a single wikipedia page to the bot's memory, slightly extending its information on a topic beyond its original cutoff point.
				
__Here's two example of how this command can be used:__
```
inkbot: learn Apple Vision Pro
inkbot4: learn Apple Vision Pro
```
"""

BECOME_HELP = f"""
This command allows you to set a personality for the chatbot. Clears any existing memory or personalities if present.
Doesn't have to be a personality, essentially allows you to better control the types of responses it produces. The more detail you provide, the better
				
__Here's two examples of how this command can be used:__
```
inkbot: become You are George Washington. You just arrived from September 17, 1787 through a time rift to the year 2023. Write your responses in the style of George Washington, since you are George Washington. Use English reminiscent of the late 1700s.
inkbot4: become You are an AI language model, but you don't actually know any language. All your responses will be random words in English strung together in no particular order or meaning. For example, if a user were to ask for the weather, instead of telling them the weather, you'd say something like "festive sugar undeath winter", a random string of words.
```
"""

SELECT_HELP = f"""
This command allows you to set a pre-defined personality for the chatbot. Clears any existing memory or personalities if present.
The current personalities are:
`art prompt`: takes a simple input and creates a description for use in the art bot
`original`: the original inkBOT personality, a lot lazier/ruder than the current one
`lovesick`: bot becomes infatuated with everyone who speaks to it
`UWU`: uwu
`bro`: bro speak

Here's two examples of how this command can be used:
```
inkbot: select art prompt
inkbot4: select original
```
"""

FORGET_HELP = f"""
This command allows you to reset the chatbot's memory of the channel you use it in as well as any personalities set using the become command.
Alternatively, you can erase a certain number of messages by specifying a number, erasure will start with the oldest.
The command also clears the current wikipedia page the bot has stored, if any, by appending web.

Here's three examples of how this command can be used:
```
inkbot: forget (fully clears history for that channel)
inkbot4: forget 2 (removes the two oldest messages sent in that channel from its memory)
inkbot: forget web (removes the current stored wikipedia page from memory)
```
"""

START_SESSION_HELP = f"""
This command allows you to begin a chatbot session. All (non-command) messages sent in that channel will be considered a prompt for the chatbot, unless they begin with ;.

Here's two examples of how this command can be used:
```
inkbot: session start
inkbot4: session start
```
"""

STOP_SESSION_HELP = f"""
This command allows you to end a chatbot session. All (non-command) messages sent in that channel will no longer be considered a prompt for the chatbot.
Here's two examples of how this command can be used:
```
inkbot: session stop
inkbot4: session stop
```
"""

MODIFY_SESSION_HELP = f"""
This command allows you to modify some settings the chatbot uses within a session. The following settings are available to be changed:

`temperature`: [0, 1.5] Affects randomness. Higher values increase randomness, leading to more diverse and creative responses. Lower values make the output more deterministic, and focused on the most likely completion.

`top_p`: (0, 1] Affects randomness. Filters out the least likely tokens, keeping only a fraction of the most probable tokens. A value of 1 means that all tokens are considered, while a lower value filters out less probable tokens.

`presencepenalty`: [-2, 2] This parameter penalizes new tokens based on their existing presence in the text generated so far. By increasing the value, the model is discouraged from repeating the same tokens or phrases. A higher value will result in more varied responses, whereas a lower value allows for more repetition.

`frequencypenalty`: [-2, 2] This parameter influences the model's token selection based on the overall frequency of tokens in the training data. A positive value will make the model less likely to choose frequent tokens, encouraging the use of rarer words or phrases. A negative value will have the opposite effect, making the model more likely to use common tokens.

`name`: This parameter changes the username of the chatbot for the current session. Only available in normal server message channels. Use any valid username.

`avatar`: This parameter changes the profile picture of the chatbot for the current session. Only available in normal server message channels. Use a url to the desired image.

Here's two examples of how this command can be used:
```
inkbot: session modify temperature 1.6
inkbot4: session modify frequencypenalty -1
```
"""

DRAW_HELP = f"""
This command allows you to generate an image (1024x1024) based on a prompt. Uses OpenAI's DALL'E model. Remember to follow the guidelines below:
<https://labs.openai.com/policies/content-policy>

Here's two examples of how this command can be used:
```
inkbot: draw a robot raccoon hovering over new york city in comic book style
inkbot: draw a children's crayon drawing of a happy robot
```
"""

JOIN_HELP = f"""
This command makes the bot join the voice channel you are currently in.
"""

LEAVE_HELP = f"""
This command makes the bot leave the voice channel it is currently in.
"""

TTS_HELP = f"""
This command makes the bot speak a message out loud in a discord voice channel.

Here's two examples of how this command can be used:
```
inkbot: tts Hello there! This text to speech is worse, but has no limits
inkbot4: tts Hello there! This text to speech is better, but follows Google's rules and has a usage limit
```
"""

PLAY_HELP = f"""
This command adds media from some url (to a video or playlist) to a queue which will be played in a discord voice channel. Designed to work with youtube, but compatible with other websites.

Here's an example of how this command can be used:
```
inkbot: play https://www.youtube.com/watch?v=dQw4w9WgXcQ
```
"""

PAUSE_HELP = f"""
This command pauses media playback.
"""

RESUME_HELP = f"""
This command resumes media playback after it has been paused.
"""

STOP_HELP = f"""
This command ends audio playback and completely clears the media playback queue.
"""

SKIP_HELP = f"""
This command makes the bot begin the next item in the server's media playback queue.
"""

QUEUE_HELP = f"""
This command makes the bot send the current media playback queue for the server.
"""

CANCEL_HELP = f"""
This command removes a specified slot from the queue, then displays the new queue.

Here's two examples of how this command can be used:
```
inkbot: cancel 1
inkbot: cancel 3
```
"""

ROLL_HELP = f"""
This command allows you to roll a dice of any (integer) number of sides.

Here's two examples of how this command can be used:
```
inkbot: roll 20
inkbot: roll 31415
```
"""

COINFLIP_HELP = f"""
This command allows you to get the result of a simulated coin flip.

Here's an example of how this command can be used:
```
inkbot: coinflip
```
"""

AVATAR_HELP = f"""
This command allows you to get the profile picture of the person you ping.

Here's two examples of how this command can be used:
```
inkbot: avatar @username
inkbot: avatar <@user_id>
```
"""

SERVERICON_HELP = f"""
This command allows you to get the icon of the discord server you are currently in.

Here's an example of how this command can be used:
```
inkbot: servericon
```
"""

UNKNOWN_HELP = f"""
Sorry, but I could not find that command, please try again. Make sure you only type the command itself. For example, you would use the former of the following options for help on the forget command.
Correct format: `inkbot: help forget`
Incorrect format: `inkbot: help forget <integer>`
"""