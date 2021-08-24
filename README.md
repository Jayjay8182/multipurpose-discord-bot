# Discord.py-Bot

## Important note: The 'run' command allows you to execute python code from a discord message (you can use codeblocks too). It is sandboxed to only allow access to certain modules and can be edited, DO NOT make this command available to anyone

A Multi-Purpose  Discord Bot template featuring commands for information, reddit browsing, investing and more.
- You can use this bot in your server by inviting it here if you wish https://discord.com/oauth2/authorize?client_id=733452893860135002&scope=bot&permissions=8
- You can use this code if you wish to but please dont straight up copy the bot, at least try to learn and understand the code for yourself that you take

# Current Commands
*Information*
- `help` shows the list of commands
- `serverinfo` displays information about the server
- `ping` shows the latency of the bot

*Misc*
- `mimic (your text)` mimics your message
- `sudo (username or mention or id + message)` pretends to be that user and sends that message
- `roll (lowestValue + highestValue)` rolls a number from a range
- `img (search term)` shows images results for your term
- `blackjack` play a game of blackjack against the bot

*Reddit*
- `sub (subreddit name , type(top/hot/new/controversial) , timeframe(hour/day/week/month/all)))` 
 shows 100 posts on a subreddit based on your filters
- `findsub (term)` shows all subreddits beginning with the term

*Investing*
- `stocks (listing e.g. AMZN or TSLA)` shows the current price of a stock in USD
- `crypto (currency e.g. BTC or ETH)` shows the current price of a crypto currency in USD

*NSFW (requires NSFW Channel)*
- `Category1` shows a random Category1 img
- `Category2` shows a random Category2 img
- `Category3` shows a random Category3 img

*Extensions* (owner only)
- `unload (extension)` unloads a command from the cogs folder
- `load (extension)` loads a command from the cogs folder
- `reload (extension)` reloads/updates a command from the cogs folder
- `fullreload` reloads/updates all commands

# Info and usage
**You will need to**
- replace `owner_id` with your own owner id
- fill in the config.txt file with your own bot application token, bot prefix, and your own reddit developer application credentials

**You may want to**
- Change the prefix of the bot from r/
- Alter command names or cooldowns
- Customise the last 3 NSFW commmands, you must add your own subreddit names to the 3 lists
  there are three of these commands each for one category
- Adding new commands will require you to make new cogs

**You will have to have the following libraries installed so far:**

*(python default libraries)*

- datetime 
- random
- requests
- asyncio
- itertools
- time
- pprint 
- collections.abc
- ast

*(you will have to install these)*

- discord
- bs4 
- praw
- yahoofinancials 


