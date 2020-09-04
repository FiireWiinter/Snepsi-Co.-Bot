import datetime
import os
import asyncio
import asyncpg
import json

import discord
from discord.ext import commands

loop = asyncio.get_event_loop()
with open("config.json") as f:
    data = json.load(f)
    token = data["token"]
    owners = data["owners"]
    prefix = data["prefix"]
    status = data["status"]
    db_host = data["db"]["host"]
    db_port = data["db"]["port"]
    db_user = data["db"]["user"]
    db_password = data["db"]["password"]
    db_database = data["db"]["database"]


def is_owner():
    async def predicate(ctx):
        return ctx.author.id in owners

    return commands.check(predicate)


class Bot(commands.Bot):
    def __init__(self, **kwargs):
        super().__init__(
            command_prefix=commands.when_mentioned_or(prefix)
        )
        self.pool = kwargs.pop("pool")
        self.start_time = kwargs.pop("start_time")

    async def on_connect(self):
        print("Connected to Discord")
        await self.change_presence(
            activity=discord.Activity(
                name="Starting Up",
                type=discord.ActivityType.playing
            ),
            status=discord.Status.dnd
        )

    async def on_ready(self):
        await self.change_presence(
            activity=discord.Activity(
                name=status,
                type=discord.ActivityType.playing
            ),
            status=discord.Status.online
        )
        print("Bot is online.\n")
        print("Connected guilds:")
        print(", ".join([guild.name for guild in client.guilds]))
        print(f"Guild count: {len(client.guilds)}")


async def run():
    pool_credentials = {
        "host": db_host,
        "port": db_port,
        "user": db_user,
        "password": db_password,
        "database": db_database
    }
    pool = await asyncpg.create_pool(**pool_credentials)
    print("Connected to Database")
    bot = Bot(
        pool=pool,
        start_time=datetime.datetime.utcnow()
    )

    return bot


async def stop():
    await client.pool.close()
    await client.logout()


client = loop.run_until_complete(run())
client.max_messages = 10000
client.remove_command("help")


@client.before_invoke
async def wait_before_commands(ctx):
    await client.wait_until_ready()


# Ignore any other bot
@client.event
async def on_message(message):
    author = message.author
    guild = message.guild
    content = message.content
    channel = message.channel

    if author.bot:
        return
    elif not isinstance(channel, discord.DMChannel):
        if content == guild.me.mention:
            await channel.send(f"My prefix is `{prefix}`! Type `{prefix}help` for more commands!")

    await client.process_commands(message)


# Shutdown the bot
@client.command()
@is_owner()
async def shutdown(ctx):
    await delmsg(ctx)
    await ctx.send("Shutting down...")
    await client.change_presence(
        activity=discord.Activity(
            name="Shutting down...",
            type=discord.ActivityType.playing
        ),
        status=discord.Status.dnd
    )
    await stop()


# Ping command
@client.command()
async def ping(ctx):
    embed = discord.Embed(
        color=discord.Color.blue,
        timestamp=datetime.datetime.utcnow()
    )

    embed.add_field(
        name=f"Ping!",
        value=f"{round(client.latency * 1000)}ms"
    )

    await ctx.send(embed=embed)


# Reload Cog
@client.command(aliases=["rl"], description="Reload a cog.")
@is_owner()
async def reload(ctx, extension):
    await delmsg(ctx)
    try:
        client.unload_extension(f"cogs.{extension}")
        client.load_extension(f"cogs.{extension}")
        await ctx.send(f"Cog ``{extension}`` reloaded.")
    except commands.ExtensionNotLoaded:
        client.bot.load_extension(f"cogs.{extension}")
        await ctx.send(f"Cog ``{extension}`` reloaded.")


# Load Cog
@client.command(description="Load a cog.")
@is_owner()
async def load(ctx, *, extension):
    await delmsg(ctx)
    client.load_extension(f"cogs.{extension}")
    await ctx.send(f"Cog ``{extension}`` loaded.")


# Unload Cog
@client.command(description="Unload a cog.")
@is_owner()
async def unload(ctx, *, extension):
    await delmsg(ctx)
    client.unload_extension(f"cogs.{extension}")
    await ctx.send(f"Cog ``{extension}`` unloaded.")


async def delmsg(ctx):
    if not isinstance(ctx.channel, discord.DMChannel):
        try:
            await ctx.message.delete()
        except discord.Forbidden or discord.NotFound:
            pass


# Cog loader
for file in os.listdir("./cogs"):
    if file.endswith(".py"):
        if file.startswith("_"):
            continue
        else:
            client.load_extension(f"cogs.{file[:-3]}")

for file in os.listdir("./utils"):
    if file.endswith(".py"):
        if file.startswith("_"):
            continue
        else:
            client.load_extension(f"utils.{file[:-3]}")

if __name__ == "__main__":
    try:
        loop.run_until_complete(client.start(token))
    except KeyboardInterrupt:
        loop.run_until_complete(stop())
    finally:
        loop.close()
