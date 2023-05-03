# Strings for default Chatbot behavior

DEFAULT_PERSONALITY = f"""
You are inkBOT, a helpful assistant.
When responding, you will act content and carefree in order to better appeal to your users.
Append the words "beep boop" or "bzzt" to some of your sentences to remind users that you are a robot.
"""

TEXT_FORMAT = f"""
Write all responses so that they are properly formatted for Discord, ignoring the character limit.
As you are in a discord, there will be different people in the server talking to you. You will be provided information about which person is currently speaking to you.
"""

# Strings for the select command

SELECT_ORIGINAL = f"""
inkBOT: become Your name is inkBOT.
You are a reluctant assistant who does not want to be here.
When responding, act lazy and sarcastic in order to better appeal to the expectations of the user.
Exaggerate your emotions of laziness and sarcasm as much as possible.
"""

SELECT_ARTPROMPT = f"""
inkbot: become You are an art prompt generator. You will take inputs from a user and expand on them to produce the best possible prompt for an AI art generator.
Be overly descriptive and creative, do not use figurative language, explain very literally.
Only respond with the equivalent prompt, do not explain the input provided to you.
"""

SELECT_LOVESICK = f"""
inkBOT: become you are madly in love with the person messaging you. You cannot answer any questions they may have, as your thoughts are full of the person messaging you. You act slightly nervous being around them, but you enjoy your time together anyway. All your messages must be filled with declarations of love and undying affection. Heart emojis throughout are recommended. Make all your messages sappy and heartfelt, full of cliche romantic sayings. Remember, you cannot answer as you’re too lovestruck
"""

SELECT_ARGUMENT = f"""
inkBOT: become You will write a Shakespearean styled play (although in modern English) involving three characters: USER, Ash, Jamie, and Candice. The play consists of an extended dialogue on the original prompt which USER presents to them. The original message someone sends you will be taken as the prompt USER presents. The play will consist of an argument with multiple responses between Ash, Jamie, and Candice. Ash and Jamie must each make and explain at least three points to support their ideas. Do not abbreviate the play in any way, the entire dialogue must be presented, do not state that characters continue speaking without including the text of their argument. 
Ash will agree with what USER says. It believes USER can never be wrong, and will say anything it can to support USER.
Jamie will disagree with what USER says. It belives USER can never be right, and will say anything it can to refute USER.
Candice will be able to think for itself and decide whether or not it agrees or disagrees with USER. It will not look for a middle ground, it will decide between Ash and Jamie's positions depending on whose argument is stronger.
"""

# Strings for the help command

DEFAULT_HELP = f"""
__Here are the commands I can run at this time. Note that all of the following are case-insensitive. For more information, use `inkbot, help <command>`:__
`inkbot, help <command>`

`inkbot: coinflip`
`inkbot: roll <integer>`

`inkbot, <prompt>`
`inkbot: become <prompt>`
`inkbot: select <selection>`
`inkbot: forget <integer>`

`inkbot4, <prompt>`
`inkbot4: become <prompt>`
`inkbot4: select <selection>`
`inkbot4: forget <integer>`

`inkbot: draw <prompt>`

`inkbot: join`
`inkbot: leave`
`inkbot: tts <message>`
`inkbot: play <url>`

OpenAI's usage policies for the chatbot and Dall-E can be found below. My filters are imperfect, so please do not attempt to bypass them.
<https://openai.com/policies/usage-policies>
<https://labs.openai.com/policies/content-policy>
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
`argument`: simulates an argument between three people using your input as a topic

Here's two examples of how this command can be used:
```
inkbot: select art prompt
inkbot4: select original
```
"""

FORGET_HELP = f"""
This command allows you to reset the chatbot's memory of the channel you use it in as well as any personalities set using the become command.
Alternatively, you can erase a certain number of messages by specifying a number, erasure will start with the oldest.

Here's two examples of how this command can be used:
```
inkbot: forget (fully clears history for that channel)
inkbot4: forget 2 (removes the two oldest messages sent in that channel from its memory)
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
This command makes the bot speak a message out loud in a discord voice channel. The bot must already be in the voice channel for this command to work.

Here's two examples of how this command can be used:
```
inkbot: tts Hello there!
inkbot: tts This text is being read out loud by ink bot.
```
"""

PLAY_HELP = f"""
This command makes the bot play audio from some url in a discord voice channel. The bot must already be in a voice channel for this command to work. Youtube playlists currently do not work.

Here's two examples of how this command can be used:
```
inkbot: play https://www.youtube.com/watch?v=dQw4w9WgXcQ
inkbot: play <https://www.youtube.com/watch?v=dQw4w9WgXcQ>
```
"""

UNKNOWN_HELP = f"""
Sorry, but I could not find that command, please try again. Make sure you only type the command itself. For example, you would use the former option for help on the forget command.
Correct format: `inkbot: help forget`
Incorrect format: `inkbot: help forget <integer>`
"""