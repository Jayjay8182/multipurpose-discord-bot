from discord.ext import commands
from discord.ext.commands import BucketType
import discord
import bot
import random
import praw


class redditCOG(commands.Cog):
    def __init__(self, client):
        global bot_client
        self.client = client
        bot_client = client

    # returns 100 reddit posts for the subname, popularity and timeframe
    # these posts are displayed in a scrolling embed
    @commands.command(pass_context=True)
    @commands.cooldown(rate=1, per=5, type=BucketType.user)
    async def sub(self, ctx, sub_name, type="top", timeframe="all"):
        error = False
        try:
            bot.command_used(ctx, "sub")
            sub = bot.reddit.subreddit(sub_name)
            time_filter = "all"
            filter = "top"
            subreddit_category_posts = sub.top("all", limit=100)

        except:
            await ctx.send("No sub found")
            error = True

        # set the time filter based on the input
        if not error:
            if str(timeframe).lower() == "hour":
                time_filter = "hour"
            elif str(timeframe).lower() == "day":
                time_filter = "day"
            elif str(timeframe).lower() == "week":
                time_filter = "week"
            elif str(timeframe).lower() == "month":
                time_filter = "month"

            # set the trend filter based on the input
            if str(type).lower() == "hot":
                subreddit_category_posts = sub.hot(limit=100)
                filter = "Hot"
            elif str(type).lower() == "new":
                time_filter = "all"
                subreddit_category_posts = sub.new(limit=100)
                filter = "New"
            elif str(type).lower() == "controversial":
                subreddit_category_posts = sub.controversial(time_filter, limit=100)
                filter = "Controversial"

            posts = []
            post_titles = []
            count = 0

            # append to list of posts and titles
            for submission in subreddit_category_posts:
                if not submission.stickied:
                    posts.append(submission.url)
                    post_titles.append(submission.title)

            # set reference to message and the template for the embed content
            message_template = f"**{filter} posts in {str(sub_name)} **\n**Timeframe: {time_filter} **\npost ` {str(count + 1)} / {str(len(posts))} `\n> {(post_titles[count])} \n {posts[count]}"
            reacted_message = await ctx.send(message_template)

            # add the reactions for scrolling
            for x in bot.reaction_emojis:
                await discord.Message.add_reaction(reacted_message, emoji=x)

            react_cross = False
            # check for reactions and update the embed based on the reaction (scroll)
            while not react_cross:
                check = Bot.reaction_check(message=reacted_message, author=ctx.author, emoji=('➡️', '⬅️', '⏪', '⏩', '🔀', '❌'))
                try:
                    reaction, user = await bot_client.wait_for('reaction_add', timeout=90.0, check=check)
                    if reaction.emoji == '➡️':
                        count += 1
                        if count == (len(posts)):
                            count = 0
                    elif reaction.emoji == '⬅️':
                        count -= 1
                        if count == -1:
                            count = (len(posts)-1)
                    elif reaction.emoji == '⏩':
                        count = (len(posts)-1)
                    elif reaction.emoji == '⏪':
                        count = 0
                    elif reaction.emoji == '🔀':
                        count = random.randint(0, len(posts))
                    elif reaction.emoji == '❌':
                        react_cross = True

                    await discord.Message.edit(reacted_message, content=f"**{filter} posts in {str(sub_name)} **\n**Timeframe: {time_filter} **\npost ` {str(count + 1)} / {str(len(posts))} `\n> {(post_titles[count])} \n {posts[count]}")

                # if the check for reactions has expired update the message and catch the error
                except:
                    await discord.Message.edit(reacted_message, content = message_template + "\n **-------------Timed Out-------------**")

    # returns all subreddits starting with the argument
    @commands.command(pass_context = True)
    @commands.cooldown(rate=1, per=5, type=BucketType.user)
    async def findsub(self, ctx, sub_name):
        bot.command_used(ctx, "find sub")
        subList = ""

        for subreddit in bot.reddit.subreddits.search_by_name(str(sub_name)):
            subList += subreddit.display_name+"\n"

        if subList != "":
            await ctx.send("Subreddits matching: `" + sub_name + "` ```" + subList + "```")
        else:
            await ctx.send("No subs found")


def setup(client):
    client.add_cog(redditCOG(client))
