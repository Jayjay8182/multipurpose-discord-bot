import discord
from discord.ext import commands
from datetime import datetime
import random
import requests
import asyncio
import itertools
from bs4 import BeautifulSoup
import ast
import time
from collections.abc import Sequence
import praw
from discord.ext.commands import BucketType
from yahoofinancials import YahooFinancials
from pprint import pprint
import r6statsapi


# reading token from file
def read_token():
    with open("token.txt", "r") as f:
        lines = f.readlines()
        return lines[0].strip()


# defining stuff
token = read_token()
client = commands.Bot(command_prefix=['r/', 'R/', '@chungus', '@Chungus'], case_insensitive=True)
client.config_token = read_token()
client.remove_command('help')
owner_id = ""
reaction_emojis = ["⏪", "⬅️", "➡️", "⏩", "🔀", "❌"]


def command_used(context, command):
    print(f"\n{command} was used in {context.guild} in {context.channel} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} by {context.author} \n message: {context.message}")


# stuff that occurs on connecting
@client.event
async def on_ready():
    await client.change_presence(activity=discord.Streaming(name="r/help", url="https://twitch.tv/jayjay8182"))
    print("bot connected")
    print("current latency "+str(int(client.latency*1000))+"ms")
    print(f"bot is in {len(client.guilds)} guilds:")
    pprint(client.guilds)
    print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")

#  error handling
@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return

    elif isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"This command is on cooldown, try again after {round(error.retry_after)} seconds.", delete_after=3)

    elif isinstance(error, commands.MissingPermissions):
        await ctx.send(f"You're missing permissons for this command, specifically {error.missing_perms}", delete_after=13)

    elif isinstance(error, commands.BotMissingPermissions):
        await ctx.send(f"I am missing permissions for this command, specifically {error.missing_perms}.", delete_after=13)

    elif isinstance(error, commands.NSFWChannelRequired):
        await ctx.send(f"{error.channel} is not an NSFW channel.", delete_after=5)

    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"Missing command argument/s {error.args}", delete_after=5)

    elif isinstance(error, commands.ArgumentParsingError):
        await ctx.send(f"Error parsing command argument/s: {error.args}", delete_after=5)

    elif isinstance(error, commands.UnexpectedQuoteError):
        await ctx.send(f"Unexpected quote in command arguments: {error.quote}", delete_after=5)

    elif isinstance(error, commands.BadArgument):
        await ctx.send(f"Bad command argument/s: {error.args}", delete_after=5)

    elif isinstance(error, commands.DisabledCommand):
        await ctx.send(f"Command is disabled", delete_after=5)

    elif isinstance(error, commands.TooManyArguments):
        await ctx.send(f"Too many command arguments: {error.args}", delete_after=5)

    elif isinstance(error, commands.UserInputError):
        await ctx.send("Something about your input was wrong, please check your input and try again", delete_after=5)

    else:
        await ctx.send("Something unexpected occurred, this was logged.", delete_after=13)
        print(f"\n{error} \n guild: {ctx.guild} \n channel: {ctx.channel} \n author: {ctx.author} message: {ctx.message}")


#  function for scrolling embed
def make_sequence(seq):
    if seq is None:
        return ()
    if isinstance(seq, Sequence) and not isinstance(seq, str):
        return seq
    else:
        return (seq,)


#  function for scrolling embed, returns true if the checks pass e.g. the correct emoji is used
def reaction_check(message=None, emoji=None, author=None, ignore_bot=True):
    message = make_sequence(message)
    message = tuple(m.id for m in message)
    emoji = make_sequence(emoji)
    author = make_sequence(author)
    def check(reaction, user):
        if ignore_bot and user.bot:
            return False
        if message and reaction.message.id not in message:
            return False
        if emoji and reaction.emoji not in emoji:
            return False
        if author and user not in author:
            return False
        return True
    return check


# bot commands
# mimic command, copys the users input and deletes the command message
@client.command(pass_context=True)
@commands.cooldown(rate=1, per=5, type=BucketType.user)
async def mimic(ctx, *args):
    command_used(ctx, "mimic")
    mimic_message = (" ".join(args))
    if '@' in mimic_message:
        await ctx.send("No pinging.")
    if mimic_message == "":
        await ctx.send("Please type a message to mimic.", delete_after=5)
    else:
        await ctx.message.delete()
        await ctx.send(" ".join(args))

#  =================================================== blackjack command ==========================================================  #
@client.command(pass_context=True)
@commands.cooldown(rate=1, per=5, type=BucketType.user)
async def blackjack(ctx):
    instance = blackjack_game(ctx)


class blackjack_game():
    def __init__(self, ctx):
        self.ctx = ctx
        command_used(self.ctx, "blackjack")

        self.game_over = False
        self.vals = [2, 3, 4, 5, 6, 7, 8, 9, 10, 'jack', 'queen', 'king', 'ace']
        self.suits = ['spades', 'clubs', 'hearts', 'diamonds']
        self.player_hand = []
        self.player_score = 0

        self.stand = False

        self.dealer_hand = []
        self.dealer_score = 0

        self.deck = list(itertools.product(self.vals, self.suits))
        random.shuffle(self.deck)

        self.loop = asyncio.get_event_loop()
        self.loop.create_task(self.start_game())

    async def start_game(self):
        await self.draw_card()
        await self.draw_card()

        if not self.game_over:
            await self.dealer_hit()
            self.blackjack_embed = discord.Embed(title="BlackJack ♠️", description=(f"`Dealer's score: {str(self.dealer_score)}`\nDealer's hand is {str((self.dealer_hand[0])[0])} of {str((self.dealer_hand[0])[1])}\n\n"
                                                                            + f"`Your score: {str(self.player_score)}`\n Your hand is {str((self.player_hand[0])[0])} of {str((self.player_hand[0])[1])}"
                                                                            + f" and {str((self.player_hand[1])[0])} of {str((self.player_hand[1])[1])}"),
                                            timestamp=datetime.utcnow(), color=0x7A6C6C)

            self.blackjack_Msg = await self.ctx.channel.send(embed=self.blackjack_embed)

            await discord.Message.add_reaction(self.blackjack_Msg, emoji="🇭")
            await discord.Message.add_reaction(self.blackjack_Msg, emoji="🇸")
            await discord.Message.add_reaction(self.blackjack_Msg, emoji="🛑")


            while not self.stand:
                self.check = reaction_check(message=self.blackjack_Msg, author=self.ctx.author, emoji=("🇭", "🇸", "🛑"))

                try:
                    self.reaction, self.user = await client.wait_for('reaction_add', timeout=90.0, check=self.check)
                    if self.reaction.emoji == "🇭":
                        await self.draw_card()
                        if not self.game_over:
                            self.dealer_hand_format = self.format_deck(self.dealer_hand)
                            self.player_hand_format = self.format_deck(self.player_hand)

                            self.player_score_str = str(self.player_score)
                            self.dealer_score_str = str(self.dealer_score)

                            self.blackjack_embed = discord.Embed(title="Blackjack ♠️", description=(f"`Dealer's score: {self.dealer_score_str}`\nDealer's hand is {self.dealer_hand_format}\n" +
                                                                                            f"`Your score: {self.player_score_str}`\nYour hand is {self.player_hand_format}\n"), timestamp=datetime.utcnow(), color=0x7A6C6C)
                            await discord.Message.edit(self.blackjack_Msg, embed=self.blackjack_embed)

                    elif self.reaction.emoji == "🇸":
                        self.stand = True
                        await self.dealer_turn()
                        break

                    elif self.reaction.emoji == "🛑":
                        await discord.Message.delete(self.blackjack_Msg)
                except:
                    return

    def format_deck(self, deck):
        deck_string = "\n"

        for x in deck:
            deck_string += f"{x[0]} of {x[1]}\n"

        return deck_string

    async def end_with_message(self, message):
        self.dealer_hand_format = self.format_deck(self.dealer_hand)
        self.player_hand_format = self.format_deck(self.player_hand)
        self.player_score_str = str(self.player_score)
        self.dealer_score_str = str(self.dealer_score)
        self.blackjack_embed = discord.Embed(title="Blackjack ♠️", description=(f"`Dealer's score: {self.dealer_score_str}`\nDealer's hand is {self.dealer_hand_format}\n" +
                                                                                            f"`Your score: {self.player_score_str}`\nYour hand is {self.player_hand_format}\n **{message}**"), timestamp=datetime.utcnow(), color=0x7A6C6C)
        await discord.Message.edit(self.blackjack_Msg, embed=self.blackjack_embed)
        await discord.Message.clear_reactions(self.blackjack_Msg)
        (self.reaction, self.user).cancel()
        self.game_over = True

    async def bust(self):
        print(self.player_hand)
        print(self.player_score)
        await self.end_with_message("You Bust, You Lose!")

    async def dealer_win(self):
        await self.end_with_message("Dealer wins with higher score")
        print(self.dealer_hand)
        print(self.dealer_score)

    async def tie(self):
        print(self.dealer_hand, self.dealer_score)
        await self.end_with_message("Tie!")

    async def dealer_turn(self):
        while self.dealer_score < self.player_score and self.dealer_score < 22 or self.dealer_score == self.player_score and self.dealer_score < 22:
            await self.dealer_hit()
            if not self.game_over:
                if self.dealer_score > self.player_score and self.dealer_score < 22:
                    await self.dealer_win()
                    break
                elif self.dealer_score > 21 and self.player_score > 21:
                    await self.tie()
                    break
                elif self.dealer_score == 21 and self.player_score == 21:
                    await self.tie()
                    break
            else:
                break

        if not self.game_over:
            if self.dealer_score > 21:
                await self.dealer_bust()

            if self.dealer_score == 21 and self.player_score == 21:
                await self.tie()

    async def dealer_bust(self):
        if self.player_score == self.dealer_score:
            await self.tie()
        else:
            await self.end_with_message("You won, dealer bust!")

    async def full21(self, player):
        if player == "player":
            await self.end_with_message("You won, Blackjack!")
            self.game_over = True

        elif player == "dealer":
            if self.player_score == self.dealer_score:
                await self.tie()
            else:
                await self.end_with_message("Dealer wins, Blackjack!")
                self.game_over = True

    async def draw_card(self):
        self.card = random.choice(self.deck)
        self.player_hand.append(self.card)

        if self.card[0] == "ace":
            if (self.player_score + 11) < 22:
                self.player_score += 11

            else:
                self.player_score += 1

        elif type(self.card[0]) is str:
            if (self.player_score + 10) > 21:
                self.player_score += 10
                await self.bust()
            else:
                self.player_score += 10

        else:
            if (self.player_score + int(self.card[0])) > 21:
                self.player_score += int(self.card[0])
                await self.bust()

            else:
                self.player_score += int(self.card[0])

        if self.player_score == 21:
            await self.full21("player")

    async def dealer_hit(self):
        self.card = random.choice(self.deck)
        self.dealer_hand.append(self.card)

        if self.card[0] == "ace":
            if (self.dealer_score + 11) < 22:
                self.dealer_score += 11

            else:
                self.dealer_score += 1

        elif type(self.card[0]) is str:
            self.dealer_score += 10

        else:
            self.dealer_score += int(self.card[0])

        if self.dealer_score == 21:
            await self.full21("dealer")


async def update_img_search(msg, list, index, query):
    img_embed = discord.Embed(title="Image results for "+str(query),  description=('img `'+str(index+1)+'/'+str(len(list))+'`'),timestamp=datetime.utcnow(), color=0x7A6C6C)
    img_embed.set_image(url=list[index])
    await discord.Message.edit(msg, embed=img_embed)


# img command, uses web scraping to store images in a list and allows the user to scroll through them by adding reactions
@client.command(pass_context = True)
@commands.cooldown(rate=1, per=5, type=BucketType.user)
async def img(ctx, *args):
    command_used(ctx, "img")
    term = (" ".join(args))
    url = 'https://bing.com/images/search?q=' + term + '&safeSearch=off' + "&FORM=HDRSC2" + '&count=100' + '&mkt=en-US' + '&adlt_set=off'
    user_agent = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.134 Safari/537.36"
    headers = {"user-agent": user_agent}
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.content, "html.parser")
    count = 0
    link_list = []
    results = soup.find_all('a',class_='iusc')

    for i in results:
        link_list.append(eval(i['m'])['murl'])

    img_embed = discord.Embed(title="Image results for "+str(term), description=('img `'+str(count+1)+'/'+str(len(link_list))+'`'), timestamp=datetime.utcnow(), color=0x7A6C6C)
    img_embed.set_image(url=link_list[count])
    reacted_message = await ctx.channel.send(embed=img_embed)

    for x in reaction_emojis:
        await discord.Message.add_reaction(reacted_message, emoji=x)

    react_cross = False
    while not react_cross:
        check = reaction_check(message=reacted_message, author=ctx.author, emoji=('➡️', '⬅️', '⏪', '⏩', '🔀', '❌'))
        try: 
            reaction, user = await client.wait_for('reaction_add', timeout=90.0, check=check)
            if reaction.emoji == '➡️':
                count += 1
                if count == (len(link_list)):
                    count = 0
                await update_img_search(reacted_message, link_list, count, term)
            elif reaction.emoji == '⬅️':    
                count -= 1
                if count == -1:
                    count = (len(link_list)-1)
                await update_img_search(reacted_message, link_list, count, term)
            elif reaction.emoji == '⏪':
                count = 0
                await update_img_search(reacted_message, link_list, count, term)
            elif reaction.emoji == '⏩':
                count = (len(link_list)-1)
                await update_img_search(reacted_message, link_list, count, term)
            elif reaction.emoji == '🔀':
                count = random.randint(0, len(link_list))
                await update_img_search(reacted_message, link_list, count, term)
            elif reaction.emoji == '❌':
                react_cross = True
                await discord.Message.delete(reacted_message)

        except:
            img_embed = discord.Embed(title="Image results for "+str(term),  description=('Timed Out'),timestamp=datetime.utcnow(), color=0x7A6C6C)
            await discord.Message.edit(reacted_message, embed=img_embed)


def insert_returns(body):
    # insert return stmt if the last expression is a expression statement
    if isinstance(body[-1], ast.Expr):
        body[-1] = ast.Return(body[-1].value)
        ast.fix_missing_locations(body[-1])

    # for if statements, we insert returns into the body and the orelse
    if isinstance(body[-1], ast.If):
        insert_returns(body[-1].body)
        insert_returns(body[-1].orelse)

    # for with blocks, again we insert returns into the body
    if isinstance(body[-1], ast.With):
        insert_returns(body[-1].body)


# command that runs python code in code blocks and sends the output
@client.command()
@commands.cooldown(rate=1, per=5, type=BucketType.user)
async def run(ctx, *, cmd):
    command_used(ctx, "run")
    if str(ctx.message.author.id) == owner_id:
        fn_name = "_eval_expr"

        cmd = cmd.strip("` ")

        # add a layer of indentation
        cmd = "\n".join(f"    {i}" for i in cmd.splitlines())

        # wrap in async def body
        body = f"async def {fn_name}():\n{cmd}"

        parsed = ast.parse(body)
        body = parsed.body[0].body

        insert_returns(body)

        env = {
            'bot': ctx.bot,
            'discord': discord,
            'commands': commands,
            'ctx': ctx,
            'time': time,
            'client': client,
            '__import__': __import__,
            'reddit': reddit
        }
        exec(compile(parsed, filename="<ast>", mode="exec"), env)

        result = (await eval(f"{fn_name}()", env))
        await ctx.send(result)
    else:
        await ctx.send("This command is reserved for the owner")


# dice roll command that takes a range from the user
@client.command()
@commands.cooldown(rate=1, per=5, type=BucketType.user)
async def roll(ctx, lValue, hValue):
    command_used(ctx, "roll")
    roll = random.randint(int(lValue), int(hValue))
    await ctx.send("you rolled `"+ str(roll)+ "`")


# server information command that displays key statistics about the server the user is in
@client.command()
@commands.cooldown(rate=1, per=5, type=BucketType.user)
async def server_info(ctx):
    command_used(ctx, "server info")
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


# help command which sends the list of commands
@client.command()
@commands.cooldown(rate=1, per=5, type=BucketType.user)
async def help(ctx):
    command_used(ctx, "help")
    with open("commands.txt", 'r') as file:
        commands = file.read()
        commands_embed = discord.Embed(color=0x7A6C6C)
        commands_embed.add_field(name="Commands", value=commands, inline=False)
        commands_embed.set_thumbnail(url=client.user.avatar_url)
        await ctx.channel.send(embed=commands_embed)


# sudo command to mimic user using a webhook
@client.command()
@commands.cooldown(rate=1, per=5, type=BucketType.user)
async def sudo(ctx, user, *message):
    command_used(ctx, "sudo")
    user_to_copy = ctx.author

    if ctx.message.mentions:
        user_to_copy = ctx.message.mentions[0]
    else:
        for member in ctx.guild.members:
            if member.id == user or client.get_user(member.id).name == user or member.display_name == user:
                user_to_copy = member
                break

    sudo_text = " ".join(message)
    await ctx.message.delete()
    webhook = await ctx.channel.create_webhook(name=user_to_copy.display_name)
    await webhook.send(content=sudo_text, avatar_url=user_to_copy.avatar_url)
    await webhook.delete()


# shows the bots ping
@client.command()
@commands.cooldown(rate=1, per=5, type=BucketType.user)
async def ping(ctx):
    command_used(ctx, "ping")
    await ctx.send("`"+str(int(client.latency*1000))+"`ms")
    
#  ======================================== Reddit Commands ========================================  #
with open("token.txt", "r") as f:
    lines = f.readlines()
        
reddit = praw.Reddit(client_id=lines[2].strip(),
                     client_secret=lines[3].strip(),
                     username=lines[4].strip(),
                     password=lines[5].strip(),
                     user_agent=lines[6].strip())

# returns 100 reddit posts for the subname, popularity and timeframe
@client.command(pass_context=True)
@commands.cooldown(rate=1, per=5, type=BucketType.user)
async def sub(ctx, sub_name, type="top", timeframe="all"):
    command_used(ctx, "sub")
    sub = reddit.subreddit(sub_name)
    time_filter = "all"
    filter = "top"
    subreddit_category_posts = sub.top("all", limit=100)

    if str(timeframe).lower() == "hour":
        time_filter = "hour"
    elif str(timeframe).lower() == "day":
        time_filter = "day"
    elif str(timeframe).lower() == "week":
        time_filter = "week"
    elif str(timeframe).lower() == "month":
        time_filter = "month"
    elif str(timeframe).lower() == "all":
        time_filter = "all"

    if str(type).lower() == "top":
        subreddit_category_posts = sub.top(time_filter, limit=100)
        filter = "Top"
    elif str(type).lower() == "hot":
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

    for submission in subreddit_category_posts:
        if not submission.stickied:
            posts.append(submission.url)
            post_titles.append(submission.title)

    message_template = f"**{filter} posts in {str(sub_name)} **\n**Timeframe: {time_filter} **\npost ` {str(count + 1)} / {str(len(posts))} `\n> {(post_titles[count])} \n {posts[count]}"
    reacted_message = await ctx.send(message_template)

    for x in reaction_emojis:
        await discord.Message.add_reaction(reacted_message, emoji=x)

    react_cross = False
    while not react_cross:
        check = reaction_check(message=reacted_message, author=ctx.author, emoji=('➡️', '⬅️', '⏪', '⏩', '🔀', '❌'))
        try: 
            reaction, user = await client.wait_for('reaction_add', timeout=90.0, check=check)
            if reaction.emoji == '➡️':
                count += 1
                if count == (len(posts)):
                    count = 0
                await discord.Message.edit(reacted_message, content=message_template)
            elif reaction.emoji == '⬅️':
                count -= 1
                if count == -1:
                    count = (len(posts)-1)
                await discord.Message.edit(reacted_message, content=message_template)
            elif reaction.emoji == '⏩':
                count = (len(posts)-1)
                await discord.Message.edit(reacted_message, content=message_template)
            elif reaction.emoji == '⏪':
                count = 0
                await discord.Message.edit(reacted_message, content=message_template)
            elif reaction.emoji == '🔀':
                count = random.randint(0, len(posts))
                await discord.Message.edit(reacted_message, content=message_template)
            elif reaction.emoji == '❌':
                react_cross = True
                await discord.Message.delete(reacted_message)

        except:
            await discord.Message.edit(reacted_message, content = message_template + "\n ** Timed Out **")


@client.command(pass_context = True)
@commands.cooldown(rate=1, per=5, type=BucketType.user)
async def find_sub(ctx, sub_name):
    command_used(ctx, "find sub")
    subList = ""
    
    for subreddit in reddit.subreddits.search_by_name(str(sub_name)):
        subList += subreddit.display_name+"\n"
        
    if subList != "":
        await ctx.send("Subreddits matching: `" + sub_name + "` ```" + subList + "```")
    else:
        await ctx.send("No subs found")


#  ======================================== Crypto Commands ========================================  #
@client.command()
@commands.cooldown(rate=1, per=5, type=BucketType.user)
async def stocks(ctx, stock):
    command_used(ctx, "stocks")
    data = YahooFinancials(stock)
    if str(data.get_current_price()) != "None" and str(data.get_current_price()) != "":
        print(data.get_current_price())
        await ctx.send(f"**{stock.upper()} - USD**\nCurrent Value: `{str(data.get_current_price())}`\nDaily Low/High: `"
                       + f"{str(data.get_daily_low())} `/` {str(data.get_daily_high())}`\nYearly Low/High: `{str(data.get_yearly_low())} `/` {str(data.get_yearly_high())}`")
    else:
        await ctx.send("Invalid Listing, listings must be abbreviated e.g. AMZN or TSLA", delete_after=7)


@client.command()
@commands.cooldown(rate=1, per=5, type=BucketType.user)
async def crypto(ctx, coin, currency):
    command_used(ctx, "crypto")
    data = YahooFinancials(coin+"-"+currency)
    if str(data) != "None" and str(data) != "":
        await ctx.send(f"**{coin.upper()} - {currency.upper()}**\nCurrent Value: `{str(data.get_current_price())}`\nDaily Low/High: `"
                       + f"{str(data.get_daily_low())} `/` {str(data.get_daily_high())}`\nYearly Low/High: `{str(data.get_yearly_low())} `/` {str(data.get_yearly_high())}`")
    else:
         await ctx.send("Invalid Listing or currency, listing and currency must be abbreviated e.g. ETH and GBP", delete_after=7)

#  ======================================== NSFW Commands from Reddit ========================================  #

category1_subreddits = []
category2_subreddits = []
category3_subreddits = []


@client.command()
@commands.cooldown(rate=1, per=5, type=BucketType.user)
@commands.is_nsfw()
async def category1(ctx):
    command_used(ctx, "category1")
    posts = []
    for submission in reddit.subreddit(random.choice(category1_subreddits)).top(random.choice(("month", "year", "all")), limit=100):
        posts.append(submission)
    
    post = random.choice(posts)
    
    if "redgif" in post.url or "imgur" in post.url:
        await ctx.send("**Here's some Ass from r/"+str(post.subreddit)+"**\n"+post.url)
    else:
        embed = discord.Embed(title="Here's some Ass from r/"+str(post.subreddit), timestamp=datetime.utcnow(), color=0x7A6C6C)
        embed.set_image(url=post.url)
        await ctx.send(embed=embed)


@client.command()
@commands.cooldown(rate=1, per=5, type=BucketType.user)
@commands.is_nsfw()
async def category2(ctx):
    command_used(ctx, "category2")
    posts = []
    for submission in reddit.subreddit(random.choice(category2_subreddits)).top(random.choice(("month", "year", "all")), limit=100):
        posts.append(submission)
    
    post = random.choice(posts)
    
    if "redgif" in post.url or "imgur" in post.url:
        await ctx.send("**Here's some Boobs from r/"+str(post.subreddit)+"**\n"+post.url)
    else:
        embed = discord.Embed(title="Here's some Boobs from r/"+str(post.subreddit), timestamp=datetime.utcnow(), color=0x7A6C6C)
        embed.set_image(url=post.url)
        await ctx.send(embed=embed)


@client.command()
@commands.cooldown(rate=1, per=5, type=BucketType.user)
@commands.is_nsfw()
async def category3(ctx):
    command_used(ctx, "category3")
    posts = []
    for submission in reddit.subreddit(random.choice(category3_subreddits)).top(random.choice(("month", "year", "all")), limit=100):
        posts.append(submission)
    
    post = random.choice(posts)
    
    if "redgif" in post.url or "imgur" in post.url:
        await ctx.send("**Here's some Pussy from r/"+str(post.subreddit)+"**\n"+post.url)
    else:
        embed = discord.Embed(title="Here's some Pussy from r/"+str(post.subreddit), timestamp=datetime.utcnow(), color=0x7A6C6C)
        embed.set_image(url=post.url)
        await ctx.send(embed=embed)


client.run(client.config_token)
