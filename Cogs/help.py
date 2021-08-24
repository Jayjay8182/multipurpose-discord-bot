from discord.ext import commands
from discord.ext.commands import BucketType
import discord
import bot


class helpCOG(commands.Cog):
    def __init__(self, client):
        global bot_client
        self.client = client
        bot_client = client

    # help command which sends the list of commands
    # this is done from a text file
    @commands.command(aliases=['commands', 'prefix'])
    @commands.cooldown(rate=1, per=5, type=BucketType.user)
    async def help(self, ctx):
        bot.command_used(ctx, "help")
        with open("commands.txt", 'r') as file:
            commands = file.read()
            commands_embed = discord.Embed(color=0x7A6C6C)
            commands_embed.add_field(name="Commands", value=commands, inline=False)
            commands_embed.set_thumbnail(url=bot_client.user.avatar_url)
            await ctx.channel.send(embed=commands_embed)


def setup(client):
    client.add_cog(helpCOG(client))
