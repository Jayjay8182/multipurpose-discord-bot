from discord.ext import commands
from discord.ext.commands import BucketType
import Bot
import random


class diceCOG(commands.Cog):
    def __init__(self, client):
        global bot_client
        self.client = client
        bot_client = client

    # dice roll command that takes a range from the user
    @commands.command(aliases=['dice'])
    @commands.cooldown(rate=1, per=5, type=BucketType.user)
    async def roll(self, ctx, lValue, hValue):
        Bot.command_used(ctx, "roll")
        roll = random.randint(int(lValue), int(hValue))
        await ctx.send("you rolled `"+ str(roll)+ "`")


def setup(client):
    client.add_cog(diceCOG(client))
