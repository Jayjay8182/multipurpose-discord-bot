from discord.ext import commands
from discord.ext.commands import BucketType
import discord
import bot
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import random


class imgCOG(commands.Cog):
    def __init__(self, client):
        global bot_client
        self.client = client
        bot_client = client

    # img command, uses web scraping to store images in a list and allows the user to scroll through them by adding reactions
    @commands.command(pass_context = True)
    @commands.cooldown(rate=1, per=5, type=BucketType.user)
    async def img(self, ctx, *args):
        bot.command_used(ctx, "img")
        term = (" ".join(args))
        url = 'https://bing.com/images/search?q=' + term + '&safeSearch=off' + '&count=100' + '&mkt=en-US' + '&adlt_set=off'
        user_agent_img = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0"
        headers = {"user-agent": user_agent_img}
        page = requests.get(url, headers=headers)
        soup = BeautifulSoup(page.content, "html.parser")
        count = 0
        link_list = []
        results = soup.find_all('a',class_='iusc', limit=100)

        for i in results:
            link_list.append(eval(i['m'])['murl'])

        img_embed = discord.Embed(title="Image results for "+str(term), description=('img `'+str(count+1)+'/'+str(len(link_list))+'`'), timestamp=datetime.utcnow(), color=0x7A6C6C)
        img_embed.set_image(url=link_list[count])
        reacted_message = await ctx.channel.send(embed=img_embed)

        for x in bot.reaction_emojis:
            await discord.Message.add_reaction(reacted_message, emoji=x)

        react_cross = False
        while not react_cross:
            check = bot.reaction_check(message=reacted_message, author=ctx.author, emoji=('➡️', '⬅️', '⏪', '⏩', '🔀', '❌'))
            try:
                reaction, user = await bot_client.wait_for('reaction_add', timeout=90.0, check=check)
                if reaction.emoji == '➡️':
                    count += 1
                    if count == (len(link_list)):
                        count = 0
                elif reaction.emoji == '⬅️':
                    count -= 1
                    if count == -1:
                        count = (len(link_list)-1)
                elif reaction.emoji == '⏪':
                    count = 0
                elif reaction.emoji == '⏩':
                    count = (len(link_list)-1)
                elif reaction.emoji == '🔀':
                    count = random.randint(0, len(link_list))
                elif reaction.emoji == '❌':
                    react_cross = True
                    await discord.Message.delete(reacted_message)
                await update_img_search(reacted_message, link_list, count, term)

            except:
                img_embed = discord.Embed(title="Image results for "+str(term),  description=('Timed Out'),timestamp=datetime.utcnow(), color=0x7A6C6C)
                await discord.Message.edit(reacted_message, embed=img_embed)


async def update_img_search(msg, list, index, query):
        img_embed = discord.Embed(title="Image results for "+str(query),  description=('img `'+str(index+1)+'/'+str(len(list))+'`'),timestamp=datetime.utcnow(), color=0x7A6C6C)
        img_embed.set_image(url=list[index])
        await discord.Message.edit(msg, embed=img_embed)


def setup(client):
    client.add_cog(imgCOG(client))
