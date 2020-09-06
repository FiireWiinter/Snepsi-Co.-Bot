import discord
from discord.ext import commands, menus
import json

with open("config.json") as f:
    data = json.load(f)
    prefix = data["prefix"]
    money_per_message = data["economy"]["money_per_message"]
    money_emoji = data["economy"]["currency_emoji"]


class ShopMenu(menus.Menu):
    async def send_initial_message(self, ctx, channel):
        return await channel.send("Click on the reactions!")

    @menus.button("⏮")
    async def on_start(self, payload):
        print(payload)
        if payload.event_type == "REACTION_REMOVE":
            return
        await self.message.remove_reaction(payload.emoji, payload.member)
        # await self.message.edit(content=f"{self.ctx.author} pressed start!")
        await self.message.channel.send(f"{self.ctx.author} pressed beginning!")

    @menus.button("◀")
    async def on_left(self, payload):
        print(payload)
        if payload.event_type == "REACTION_REMOVE":
            return
        await self.message.remove_reaction(payload.emoji, payload.member)
        # await self.message.edit(content=f"{self.ctx.author} pressed left!")
        await self.message.channel.send(f"{self.ctx.author} pressed left!")

    @menus.button("▶")
    async def on_right(self, payload):
        print(payload)
        if payload.event_type == "REACTION_REMOVE":
            return
        await self.message.remove_reaction(payload.emoji, payload.member)
        # await self.message.edit(content=f"{self.ctx.author} pressed right!")
        await self.message.channel.send(f"{self.ctx.author} pressed right!")

    @menus.button("⏭")
    async def on_end(self, payload):
        print(payload)
        if payload.event_type == "REACTION_REMOVE":
            return
        await self.message.remove_reaction(payload.emoji, payload.member)
        # await self.message.edit(content=f"{self.ctx.author} pressed end!")
        await self.message.channel.send(f"{self.ctx.author} pressed ending!")

    @menus.button("🛑")
    async def on_stop(self, payload):
        print(payload)
        if payload.event_type == "REACTION_REMOVE":
            return
        await self.message.clear_reactions()
        # await self.message.edit(content=f"{self.ctx.author} pressed stop!")
        await self.message.channel.send(f"{self.ctx.author} pressed stop!")
        self.stop()


class Items(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Give users money on talking
    @commands.Cog.listener()
    async def on_message(self, message):
        author = message.author
        if author.bot:
            return
        if isinstance(message.channel, discord.DMChannel):
            return
        if message.content.startswith(prefix):
            return

        async with self.bot.pool.acquire() as db:
            r = await db.fetchrow("SELECT * FROM users WHERE ID=$1", author.id)
            if r:  # User is already in the system
                await db.execute(
                    "UPDATE users SET money=money+$1 WHERE ID=$2",
                    money_per_message, author.id
                )
            else:  # User is not in the System
                await db.execute(
                    "INSERT INTO users (ID, money, bank, items) VALUES ($1, $2, $3, $4)",
                    author.id, money_per_message, 0, "{}"
                )

    # Check your current balance
    @commands.command(aliases=["bal", "money"])
    async def balance(self, ctx):
        async with self.bot.pool.acquire() as db:
            embed = discord.Embed(
                title="Balance",
                color=discord.Color.blue()
            )

            r = await db.fetchrow("SELECT * FROM users WHERE ID=$1", ctx.author.id)
            if r:  # User is already in the System
                cash = r["money"]
                bank = r["bank"]
                net = cash + bank
                embed.add_field(name="Cash:", value=f"{money_emoji} {cash}")
                embed.add_field(name="Bank:", value=f"{money_emoji} {bank}")
                embed.add_field(name="Net Worth:", value=f"{money_emoji} {net}")
            else:  # User is not in the System
                embed.add_field(name="Cash:", value=f"{money_emoji} 0")
                embed.add_field(name="Bank:", value=f"{money_emoji} 0")
                embed.add_field(name="Net Worth:", value=f"{money_emoji} 0")
            await ctx.send(embed=embed)

    # Deposit Money from your Pockets into your Bank
    @commands.command(aliases=["dep"])
    async def deposit(self, ctx, amount: int):
        async with self.bot.pool.acquire() as db:
            r = await db.fetchrow("SELECT * FROM users WHERE ID=$1", ctx.author.id)
            if r:
                money = r["money"]
                bank = r["bank"]
                if amount <= money:
                    await db.execute(
                        "UPDATE users SET money=money-$1, bank=bank+$1 WHERE ID=$2",
                        amount, ctx.author.id
                    )
                    await ctx.send(
                        f"Deposited {amount} to your Account!\n"
                        f"You now have {money - amount} in your Pockets!\n"
                        f"You now have {bank + amount} on your Bank Account!"
                    )
                else:
                    await ctx.send("You don't have that much money in your pockets!")
            else:
                return await ctx.send("You don't have money to deposit")

    # Withdraw Money from your Bank into your Pockets
    @commands.command(aliases=["with"])
    async def withdraw(self, ctx, amount: int):
        async with self.bot.pool.acquire() as db:
            r = await db.fetchrow("SELECT * FROM users WHERE ID=$1", ctx.author.id)
            if r:
                money = r["money"]
                bank = r["bank"]
                if amount <= bank:
                    await db.execute(
                        "UPDATE users SET money=money+$1, bank=bank-$1 WHERE ID=$2",
                        amount, ctx.author.id
                    )
                    await ctx.send(
                        f"Withdrew {amount} from your Account!\n"
                        f"You now have {money + amount} in your Pockets!\n"
                        f"You now have {bank - amount} on your Bank Account!"
                    )
                else:
                    await ctx.send("You don't have that much money in your Bank Account!")
            else:
                return await ctx.send("You don't have money to withdraw")

    # Display the Shop
    @commands.command()
    async def shop(self, ctx):
        await ShopMenu().start(ctx)

    # The Following commands are currently just placeholders, but will be replaced with actual code
    @commands.command()
    async def buy(self, ctx, *, item):
        await ctx.send(f"Buying item {item} from the shop (not really)")

    @commands.command()
    async def use(self, ctx, *, item):
        await ctx.send(f"Using item {item} from your inventory (not really)")

    @commands.command(aliases=["inv"])
    async def inventory(self, ctx):
        await ctx.send("Showing inventory (not really)")


def setup(bot):
    bot.add_cog(Items(bot))
