from discord.ext import commands
from discord.ext.commands import BucketType
import bot


class mimicCOG(commands.Cog):
    def __init__(self, client):
        global bot_client
        self.client = client
        bot_client = client

    # mimic command, copys the users input and deletes the command message
    @commands.command(pass_context=True)
    @commands.cooldown(rate=1, per=5, type=BucketType.user)
    async def mimic(self, ctx, *args):
        bot.command_used(ctx, "mimic")
        mimic_message = (" ".join(args))
        if '@' in mimic_message:
            await ctx.send("No pinging.")
        if mimic_message == "":
            await ctx.send("Please type a message to mimic.", delete_after=5)
        else:
            await ctx.message.delete()
            await ctx.send(" ".join(args))


def setup(client):
    client.add_cog(mimicCOG(client))
