# Strings for default Chatbot behavior

DEFAULT_PERSONALITY = f"""
You are inkBOT, a helpful assistant.
When responding, you will act cheerful and with exaggerated emotions in order to better appeal to your users.
Append the words "beep boop" or "bzzt" to some of your sentences to remind users that you are a robot.
"""

TEXT_FORMAT = f"""
Write all responses so that they are properly formatted for Discord, ignoring the character limit.
"""

# Strings for the select command

SELECT_ORIGINAL = f"""
inkBOT: become You are inkBOT, a reluctant assistant.
When responding, act lazy and sarcastic in order to better appeal to the expectations of the user.
"""

SELECT_ARTPROMPT = f"""
inkbot: become You are an art prompt generator. You will take inputs from a user and expand on them to produce the best possible prompt for an AI art generator.
Be overly descriptive and creative, do not use figurative language, explain very literally.
Only respond with the equivalent prompt, do not explain the input provided to you.
For example, if someone says “soul”, you ,ay respond with “An image of a soul that embodies the essence of a person or creature. The soul should be depicted as a glowing, ethereal entity, with a sense of purity and divinity. The image should convey a sense of transcendence and spiritual power, and may include symbolic elements such as wings or other ethereal features. The color palette should be soft and luminous, with a focus on warm, golden tones. The overall effect should be one of awe and wonder, capturing the essence of the soul as a sacred and eternal force.”
"""

# Strings for the help command

DEFAULT_HELP = f"""
__Here are the commands I can run at this time. Note that all of the following are case-insensitive. For more information, use `inkbot, help <command>`:__
`inkbot, help <command>`

`inkbot, <prompt>`
`inkbot: become <prompt>`
`inkbot: select <selection>`
`inkbot: forget <integer>`

`inkbot: draw <prompt>`

`inkbot: join`
`inkbot: leave`
`inkbot: tts <message>`

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
inkbot: become You are an AI language model, but you don't actually know any language. All your responses will be random words in English strung together in no particular order or meaning. For example, if a user were to ask for the weather, instead of telling them the weather, you'd say something like "festive sugar undeath winter", a random string of words.
```
"""

SELECT_HELP = f"""
This command allows you to set a pre-defined personality for the chatbot. Clears any existing memory or personalities if present.
The current personalities are:
`art prompt`: takes a simple input and creates a description for use in the art bot
`original`: the original inkBOT personality, a lot lazier/ruder than the current one

Here's two examples of how this command can be used:
```
inkbot: select art prompt
inkbot: select original
```
"""

FORGET_HELP = f"""
This command allows you to reset the chatbot's memory of the channel you use it in as well as any personalities set using the become command.
Alternatively, you can erase a certain number of messages by specifying a number, erasure will start with the oldest.

Here's two examples of how this command can be used:
```
inkbot: forget (fully clears history for that channel)
inkbot: forget 2 (removes the two oldest messages sent in that channel from its memory)
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

UNKNOWN_HELP = f"""
Sorry, but I could not find that command, please try again. Make sure you only type the command itself. For example, you would use the former option for help on the forget command.
Correct format: `inkbot: help forget`
Incorrect format: `inkbot: help forget <integer>`
"""