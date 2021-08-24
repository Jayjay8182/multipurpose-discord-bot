from discord.ext import commands
from discord.ext.commands import BucketType
import discord
import bot
from datetime import datetime


class serverinfoCOG(commands.Cog):
    def __init__(self, client):
        global bot_client
        self.client = client
        bot_client = client

    # server information command that displays key statistics about the server the user is in
    @commands.command(aliases=['info'])
    @commands.cooldown(rate=1, per=5, type=BucketType.user)
    async def serverinfo(self, ctx):
        bot.command_used(ctx, "server info")
        member_count = len(ctx.guild.members)

        serverInfoEmbed = discord.Embed(title=" Server Stats for "+str(ctx.guild), timestamp=datetime.utcnow(), color=0x7A6C6C)
        serverInfoEmbed.set_thumbnail(url=ctx.guild.icon_url)

        fields = [("ID", ctx.guild.id, True),
                            ("Owner", "\@"+str(ctx.guild.owner), True),
                            ("Region", ctx.guild.region, True),
                            ("Created at", ctx.guild.created_at.strftime("%d/%m/%Y %H:%M:%S"), True),
                            ("Text channels", len(ctx.guild.text_channels), True),
                            ("Voice channels", len(ctx.guild.voice_channels), True),
                            ("Members", str(member_count), True),
                            ("Boosts", str(ctx.guild.premium_subscription_count), True),
                            ("Roles", len(ctx.guild.roles), True)]

        for name, value, inline in fields:
            serverInfoEmbed.add_field(name=name, value=value, inline=inline)
        await ctx.channel.send(embed=serverInfoEmbed)


def setup(client):
    client.add_cog(serverinfoCOG(client))
