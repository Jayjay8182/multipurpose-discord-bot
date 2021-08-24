from discord.ext import commands
from discord.ext.commands import BucketType
import discord
import random
import asyncio
import Bot
import itertools
from datetime import datetime

# this command is messy and could probably be improved
# i put the command in a separate class to make sure each time it was called they were different instances
# this is so reactions only apply to a single blackjack game
class blackjackCOG(commands.Cog):
    def __init__(self, client):
        global bot_client
        self.client = client
        bot_client = client

    @commands.command(pass_context=True)
    @commands.cooldown(rate=1, per=5, type=BucketType.user)
    async def blackjack(self, ctx):
        instance = blackjack_game(ctx)


class blackjack_game():
    def __init__(self, ctx):
        self.ctx = ctx
        Bot.command_used(self.ctx, "blackjack")

        # creating the deck, player and dealer hands
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
        # start by drawing 2 cards
        await self.draw_card()
        await self.draw_card()

        if not self.game_over:
            # draw 1 card for the dealer and show both hands
            await self.dealer_hit()
            self.blackjack_embed = discord.Embed(title="BlackJack ♠️", description=(f"`Dealer's score: {str(self.dealer_score)}`\nDealer's hand is {str((self.dealer_hand[0])[0])} of {str((self.dealer_hand[0])[1])}\n\n"
                                                                            + f"`Your score: {str(self.player_score)}`\n Your hand is {str((self.player_hand[0])[0])} of {str((self.player_hand[0])[1])}"
                                                                            + f" and {str((self.player_hand[1])[0])} of {str((self.player_hand[1])[1])}"),
                                                                            timestamp=datetime.utcnow(), color=0x7A6C6C)

            self.blackjack_Msg = await self.ctx.channel.send(embed=self.blackjack_embed)

            # add the options to hit stand or stop
            await discord.Message.add_reaction(self.blackjack_Msg, emoji="🇭")
            await discord.Message.add_reaction(self.blackjack_Msg, emoji="🇸")
            await discord.Message.add_reaction(self.blackjack_Msg, emoji="🛑")

            # if the player has not stood, wait for them to hit or stand
            while not self.stand:
                self.check = Bot.reaction_check(message=self.blackjack_Msg, author=self.ctx.author, emoji=("🇭", "🇸", "🛑"))

                try:
                    self.reaction, self.user = await bot_client.wait_for('reaction_add', timeout=90.0, check=self.check)

                    # if they hit draw a card and update the embed to show the hands
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

                    # if they stand, start dealer turn
                    elif self.reaction.emoji == "🇸":
                        self.stand = True
                        await self.dealer_turn()
                        break

                    elif self.reaction.emoji == "🛑":
                        await discord.Message.delete(self.blackjack_Msg)
                except:
                    return

    # create a string of the deck in a nice format
    def format_deck(self, deck):
        deck_string = "\n"

        for x in deck:
            deck_string += f"{x[0]} of {x[1]}\n"

        return deck_string

    # function used to end the game with a specific message e.g. you bust!
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
        await self.end_with_message("You Bust, You Lose!")

    async def dealer_win(self):
        await self.end_with_message("Dealer wins with higher score")

    async def tie(self):
        await self.end_with_message("Tie!")

    # hit until score is bigger than the players or bust then show the appropriate game over msg
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

    # drawing a card for the player
    async def draw_card(self):
        self.card = random.choice(self.deck)
        self.player_hand.append(self.card)

        # aces will either ad 11 or 1 score depending on if the player will bust
        if self.card[0] == "ace":
            if (self.player_score + 11) < 22:
                self.player_score += 11

            else:
                self.player_score += 1

        # add 10 if the card is a royal
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

    # dealer hits untill they beat the player score after standing or bust
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


def setup(client):
    client.add_cog(blackjackCOG(client))
