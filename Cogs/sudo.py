from discord.ext import commands
from discord.ext.commands import BucketType
import Bot


class sudoCOG(commands.Cog):
    def __init__(self, client):
        global bot_client
        self.client = client
        bot_client = client

    # sudo command to mimic user using a webhook
    # a web hook is created in the channel the command was used
    # the web hooks name and icon is set to the target user
    # the web hook sends the desired message and is then deleted
    @commands.command()
    @commands.cooldown(rate=1, per=5, type=BucketType.user)
    async def sudo(self, ctx, user, *message):
        Bot.command_used(ctx, "sudo")
        user_to_copy = ctx.author

        if ctx.message.mentions:
            user_to_copy = ctx.message.mentions[0]
        else:
            for member in ctx.guild.members:
                if member.id == user or bot_client.get_user(member.id).name == user or member.display_name == user:
                    user_to_copy = member
                    break

        sudo_text = " ".join(message)
        await ctx.message.delete()
        webhook = await ctx.channel.create_webhook(name=user_to_copy.display_name)
        await webhook.send(content=sudo_text, avatar_url=user_to_copy.avatar_url)
        await webhook.delete()


def setup(client):
    client.add_cog(sudoCOG(client))
