from discord.ext import commands
from discord.ext.commands import BucketType
import discord
import bot
from yahoofinancials import YahooFinancials
import random


class investingCOG(commands.Cog):
    def __init__(self, client):
        global bot_client
        self.client = client
        bot_client = client

    @commands.command()
    @commands.cooldown(rate=1, per=5, type=BucketType.user)
    async def stocks(self, ctx, stock):
        bot.command_used(ctx, "stocks")
        data = YahooFinancials(stock)
        if str(data.get_current_price()) != "None" and str(data.get_current_price()) != "":
            print(data.get_current_price())
            await ctx.send(f"**{stock.upper()} - USD**\nCurrent Value: `{str(data.get_current_price())}`\nDaily Low/High: `"
                           + f"{str(data.get_daily_low())} `/` {str(data.get_daily_high())}`\nYearly Low/High: `{str(data.get_yearly_low())} `/` {str(data.get_yearly_high())}`")
        else:
            await ctx.send("Invalid Listing, listings must be abbreviated e.g. AMZN or TSLA", delete_after=7)


    @commands.command()
    @commands.cooldown(rate=1, per=5, type=BucketType.user)
    async def crypto(self, ctx, coin, currency):
        bot.command_used(ctx, "crypto")
        data = YahooFinancials(coin+"-"+currency)
        if str(data) != "None" and str(data) != "":
            await ctx.send(f"**{coin.upper()} - {currency.upper()}**\nCurrent Value: `{str(data.get_current_price())}`\nDaily Low/High: `"
                           + f"{str(data.get_daily_low())} `/` {str(data.get_daily_high())}`\nYearly Low/High: `{str(data.get_yearly_low())} `/` {str(data.get_yearly_high())}`")
        else:
             await ctx.send("Invalid Listing or currency, listing and currency must be abbreviated e.g. ETH and GBP", delete_after=7)


def setup(client):
    client.add_cog(investingCOG(client))
