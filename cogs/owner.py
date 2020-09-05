import discord
from discord.ext import commands
import json

with open("config.json") as f:
    owners = json.load(f)["owners"]


def is_owner():
    async def predicate(ctx):
        return ctx.author.id in owners

    return commands.check(predicate)


class Owner(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # Tell the bot to say something
    @commands.command()
    @is_owner()
    async def say(self, ctx, *, message):
        await delmsg(ctx)
        await ctx.send(message)

    # Evaluate message
    @commands.command()
    @is_owner()
    async def ev(self, ctx, *, message):
        await delmsg(ctx)
        await ctx.send(eval(message))

    # Execute Python Code from Discord
    @commands.command()
    @is_owner()
    async def run(self, ctx, *, msg):
        msg = msg.replace("“", "\"")
        msg = msg.replace("‘", "'")
        exec(
            f"async def __ex(ctx): " +
            "".join(f"\n {l}" for l in msg.split("\n"))
        )
        return await locals()["__ex"](ctx)


async def delmsg(ctx):
    if not isinstance(ctx.channel, discord.DMChannel):
        try:
            await ctx.message.delete()
        except discord.Forbidden or discord.NotFound:
            return


def setup(bot):
    bot.add_cog(Owner(bot))
