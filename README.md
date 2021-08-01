# Discord.py-Bot
A Multi-Purpose  Discord Bot template featuring commands for information, reddit browsing, investing and more.

# Current Commands
*Information*
`help` shows the list of commands
`serverinfo` displays information about the server
`ping` shows the latency of the bot

*Misc*
`mimic (your text)` mimics your message
`sudo (username or mention or id + message)` pretends to be that user and sends that message
`roll (lowestValue + highestValue)` rolls a number from a range
`img (search term)` shows images results for your term
`blackjack` play a game of blackjack against the bot

*Reddit*
`sub (subreddit name , type(top/hot/new/controversial) , timeframe(hour/day/week/month/all)))` 
 shows 100 posts on a subreddit based on your filters
`findsub (term)` shows all subreddits beginning with the term

*Investing*
`stocks (listing e.g. AMZN or TSLA)` shows the current price of a stock in USD
`crypto (currency e.g. BTC or ETH)` shows the current price of a crypto currency in USD

*NSFW (requires NSFW Channel)*
`Category1` shows a random Category1 img
`Category2` shows a random Category1 img
`Category3` shows a random Category1 img

# Info and usage
**You will need to**
- replace `owner_id` with your own owner id
- supply your own bot application token, the bot currently gets this from a file called token.txt on line 0
- supply your own reddit developer application credentials, the bot currently gets this from a file called token.txt on lines 2-6

**You may want to**
- Change the prefix of the bot from r/
- Alter command names or cooldowns
- Customise the last 3 NSFW commmands, you must add your own subreddit names to the 3 lists
  there are three of these commands each for one category

**You will have to have the following libraries installed so far:**
- discord
- datetime 
- random
- requests
- asyncio
- itertools
- bs4 
- ast
- time
- collections.abc
- praw
- yahoofinancials 
- pprint 

