import os
from collections.abc import Sequence
from datetime import datetime
from pprint import pprint
import praw
import discord
from discord.ext import commands


# reading discord api token from file
def read_token():
    with open("token.txt", "r") as f:
        lines = f.readlines()
        return lines[0].strip()


# creating an instance of the reddit api from file
with open("token.txt", "r") as f:
    lines = f.readlines()
    reddit = praw.Reddit(
         client_id=lines[2].strip(),
         client_secret=lines[3].strip(),
         username=lines[4].strip(),
         password=lines[5].strip(),
         user_agent=lines[6].strip())

# creating variables for discord api interaction
token = read_token()
client = commands.Bot(command_prefix=['r/', 'R/', '@chungus', '@Chungus'], case_insensitive=True)  # setting multiple prefixes
client.config_token = read_token()
client.remove_command('help')  # removing the default help command to replace with our own COG
reaction_emojis = ["⏪", "⬅️", "➡️", "⏩", "🔀", "❌"]  # list of emotes used for scrolling embeds which can be reused


# function that runs when any command is used, logs this to console and other details
def command_used(context, command):
    print(f"\n{command} was used in {context.guild} in {context.channel} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} by {context.author} \n message: {context.message}")


# stuff that occurs when the bot connects
# logging the servers the bot is in and the current latency
@client.event
async def on_ready():
    await client.change_presence(activity=discord.Streaming(name="r/help", url="https://twitch.tv/jayjay8182"))
    print("bot connected")
    print("current latency "+str(int(client.latency*1000))+"ms")
    print(f"bot is in {len(client.guilds)} guilds:")
    pprint(client.guilds)
    print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")


#  error handling
#  this catches all errors but can be overridden for specific commands
#  errors will tell the user if they need to do anything
#  if the error is not caught by the general catches then it is logged to console for debugging
@client.event
async def on_command_error(ctx, error):
    # nothing is done if a command is not found, i find those messages annoying
    if isinstance(error, commands.CommandNotFound):
        return

    # if a command is on cooldown show the cooldown rounded
    elif isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"This command is on cooldown, try again after {round(error.retry_after)} seconds.", delete_after=3)

    # if permissions are missing tell them what they are
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send(f"You're missing permissons for this command, specifically {error.missing_perms}", delete_after=13)

    # if the bot is missing permissions tell them what they are
    elif isinstance(error, commands.BotMissingPermissions):
        await ctx.send(f"I am missing permissions for this command, specifically {error.missing_perms}.", delete_after=13)

    # if the command requires nsfw but was called in a non nsfw channel tell them
    elif isinstance(error, commands.NSFWChannelRequired):
        await ctx.send(f"{error.channel} is not an NSFW channel.", delete_after=5)

    # if there are missing command parameters, specify them
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"Missing command argument/s {error.args}", delete_after=5)

    # if command arguments can't be parsed (likely user error) say which ones
    elif isinstance(error, commands.ArgumentParsingError):
        await ctx.send(f"Error parsing command argument/s: {error.args}", delete_after=5)

    # if there are unexpected quotes in command arguments tell them
    elif isinstance(error, commands.UnexpectedQuoteError):
        await ctx.send(f"Unexpected quote in command arguments: {error.quote}", delete_after=5)

    # if there are bad command arguments, specify them
    elif isinstance(error, commands.BadArgument):
        await ctx.send(f"Bad command argument/s: {error.args}", delete_after=5)

    # if the command is disabled tell them
    elif isinstance(error, commands.DisabledCommand):
        await ctx.send(f"Command is disabled", delete_after=5)

    # if there are too many arguments tell them
    elif isinstance(error, commands.TooManyArguments):
        await ctx.send(f"Too many command arguments: {error.args}", delete_after=5)

    # if there is an invalid input tell them
    elif isinstance(error, commands.UserInputError):
        await ctx.send("Something about your input was wrong, please check your input and try again", delete_after=5)

    # if all above error checks fail, log the error and extra details for debugging
    else:
        await ctx.send("Something unexpected occurred, this was logged.", delete_after=13)
        print(f"\n{error} \n guild: {ctx.guild} \n channel: {ctx.channel} \n author: {ctx.author} message: {ctx.message}")


#  function for scrolling embed
def make_sequence(seq):
    if seq is None:
        return ()
    if isinstance(seq, Sequence) and not isinstance(seq, str):
        return seq
    else:
        return (seq,)


#  function for scrolling embed, returns true if the checks pass e.g. the correct emoji is used
def reaction_check(message=None, emoji=None, author=None, ignore_bot=True):
    message = make_sequence(message)
    message = tuple(m.id for m in message)
    emoji = make_sequence(emoji)
    author = make_sequence(author)
    def check(reaction, user):
        if ignore_bot and user.bot:
            return False
        if message and reaction.message.id not in message:
            return False
        if emoji and reaction.emoji not in emoji:
            return False
        if author and user not in author:
            return False
        return True
    return check

# load / reload / unload COGs during runtime
# allows new commands to be added without restarting

# load
@commands.is_owner()
@client.command()
async def load(ctx, extension):
    client.load_extension(f'Cogs.{extension}')
    await ctx.send(f'loaded extension {extension}')

# unload
@commands.is_owner()
@client.command()
async def unload(ctx, extension):
    client.unload_extension(f'Cogs.{extension}')
    await ctx.send(f'unloaded extension {extension}')

# unload then load (reload)
@commands.is_owner()
@client.command()
async def reload(ctx, extension):
    client.unload_extension(f'Cogs.{extension}')
    client.load_extension(f'Cogs.{extension}')
    await ctx.send(f'reloaded extension {extension}')

# unload and load all cogs (full reload)
@commands.is_owner()
@client.command()
async def fullreload(ctx):
    for filename in os.listdir('./Cogs'):
        if filename.endswith('.py'):
            client.unload_extension(f'Cogs.{filename[:-3]}')
            client.load_extension(f'Cogs.{filename[:-3]}')


# load every cog in cogs directory on starting the bot
for filename in os.listdir('./Cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'Cogs.{filename[:-3]}')

# run the bot
client.run(client.config_token)
