from discord.ext import commands
from discord.ext.commands import BucketType
import discord
import Bot
import random
from datetime import datetime


class nsfwCOG(commands.Cog):
    def __init__(self, client):
        self.client = client
        # lists that should contain names of subreddit for each command to pull images/gifs from
        # more can be added, they should ideally contain a "theme" or "category"
        self.category1_subreddits = []
        self.category2_subreddits = []
        self.category3_subreddits = []


# these three commands call the nsfw function
# the nsfw function will pull a random img from a post
# the post is pulled from a list of 100 posts from a random subreddit pulled from one of the lists
    @commands.command()
    @commands.cooldown(rate=1, per=5, type=BucketType.user)
    @commands.is_nsfw()
    async def category1(self, ctx):
        await self.nsfw("category1", ctx, self.category1_subreddits)

    @commands.command()
    @commands.cooldown(rate=1, per=5, type=BucketType.user)
    @commands.is_nsfw()
    async def category2(self, ctx):
        await self.nsfw("category2", ctx, self.category2_subreddits)

    @commands.command()
    @commands.cooldown(rate=1, per=5, type=BucketType.user)
    @commands.is_nsfw()
    async def category3(self, ctx):
        await self.nsfw("category3", ctx, self.category3_subreddits)

    async def nsfw(self, category, ctx, subs):
        Bot.command_used(ctx, category)
        posts = []
        for submission in Bot.reddit.subreddit(random.choice(subs)).top(random.choice(("month", "year", "all")), limit=100):
            posts.append(submission)
            posts.append(submission)

        post = random.choice(posts)

        if "redgif" in post.url or "imgur" in post.url:
            await ctx.send(f"**Here's some {category} from r/"+str(post.subreddit)+"**\n"+post.url)
        else:
            embed = discord.Embed(title=f"Here's some {category} from r/"+str(post.subreddit), timestamp=datetime.utcnow(), color=0x7A6C6C)
            embed.set_image(url=post.url)
            await ctx.send(embed=embed)


def setup(client):
    client.add_cog(nsfwCOG(client))
