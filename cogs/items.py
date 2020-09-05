import discord
from discord.ext import commands, menus


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

    @commands.command()
    async def shop(self, ctx):
        await ShopMenu().start(ctx)

    # The Following commands are currently just placeholders, but will be replaced with actual code
    @commands.command()
    async def shop_add(self, ctx):
        await ctx.send(f"Adding a item to the shop (not really)")

    @commands.command()
    async def shop_remove(self, ctx, *, item):
        await ctx.send(f"Removing item {item} from the shop (not really)")

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
