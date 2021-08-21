from discord.ext import commands
from discord.ext.commands import BucketType
import Bot


# sends the latency of the bot
class pingCOG(commands.Cog):
    def __init__(self, client):
        global bot_client
        self.client = client
        bot_client = client

    # shows the bots ping
    @commands.command()
    @commands.cooldown(rate=1, per=5, type=BucketType.user)
    async def ping(self, ctx):
        Bot.command_used(ctx, "ping")
        await ctx.send("`"+str(int(bot_client.latency*1000))+"`ms")


def setup(client):
    client.add_cog(pingCOG(client))
