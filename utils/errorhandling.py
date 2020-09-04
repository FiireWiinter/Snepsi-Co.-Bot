import discord
from discord.ext import commands
import traceback
import sys
import math
import json

with open("config.json") as f:
    prefix = json.load(f)["prefix"]


class ErrorHandling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if hasattr(ctx.command, "on_error"):
            return

        error = getattr(error, "original", error)

        if isinstance(error, commands.CommandNotFound):
            return
        elif isinstance(error, commands.CheckFailure):
            if isinstance(error, commands.NSFWChannelRequired):
                await ctx.send(f"Error in that command:\n```{error}```")
                if not isinstance(ctx.channel, discord.DMChannel):
                    await ctx.message.delete()
            elif (
                isinstance(error, commands.PrivateMessageOnly)
                or isinstance(error, commands.NoPrivateMessage)
                or isinstance(error, commands.BotMissingPermissions)
            ):
                await ctx.send(f"Error in command `{ctx.command}`:\n```{error}```")
            else:
                return
        elif isinstance(error, commands.CommandOnCooldown):
            cooldown = cooldown_formatter(error.retry_after)
            await ctx.send(
                f"You must wait {cooldown} before you can use the command ``{ctx.command}`` again."
            )
        elif isinstance(error, commands.UserInputError):
            if isinstance(error, commands.MissingRequiredArgument):
                await ctx.send(help_formatter(ctx.command, ctx.command.clean_params))
            elif isinstance(error, commands.BadArgument):
                await ctx.send(f"Error in command `{ctx.command}`:\n```{error}```")
            elif isinstance(error, commands.BadUnionArgument):
                await ctx.send(f"Error in command `{ctx.command}`:\n```{error}```")
            elif isinstance(error, commands.ArgumentParsingError):
                await ctx.send(f"Error in command `{ctx.command}`:\n```{error}```")
        elif isinstance(error, discord.Forbidden):
            print(f"<<<Occurred in {ctx.guild}, in {ctx.channel} by user {ctx.author}")
            await ctx.send(
                f"Error in command `{ctx.command}`:\n```{type(error).__name__}: {error}```"
            )
            print(
                "Ignoring exception in command {}:".format(ctx.command), file=sys.stderr
            )
            traceback.print_exception(
                type(error), error, error.__traceback__, file=sys.stderr
            )
        else:
            print(
                f'{"-" * 15}\n>>> Occurred in {ctx.guild}, in {ctx.channel} by user {ctx.author}\n{"-" * 15}'
            )
            await ctx.send(
                f"Error in command `{ctx.command}`:\n```{type(error).__name__}: {error}```"
            )
            print(
                "Ignoring exception in command {}:".format(ctx.command), file=sys.stderr
            )
            traceback.print_exception(
                type(error), error, error.__traceback__, file=sys.stderr
            )


# Cooldown formatter
def cooldown_formatter(cooldown):
    cooldown = round(cooldown)
    days = math.floor(cooldown / 86400)
    hours = math.floor(cooldown / 3600) - (days * 24)
    minutes = math.floor(cooldown / 60) - (hours * 60) - (days * 24 * 60)
    seconds = cooldown - (minutes * 60) - (hours * 3600) - (days * 86400)
    dt = date_string(days, "day")
    ht = date_string(hours, "hour")
    mt = date_string(minutes, "minute")
    st = date_string(seconds, "second")

    times_before = [dt, ht, mt, st]
    times_after = []

    for time_unit in times_before:
        if time_unit == "":
            continue
        else:
            times_after.append(time_unit)

    if len(times_after) == 1:
        return times_after[0]
    else:
        beginning = " ".join(times_after[:-1])
        end = f" and {times_after[-1]}"

        return f"{beginning}{end}"


# Help formatter
def help_formatter(cmd, cmd_params):
    params = [
        key if str(value).count("=None") == 0 else f"(Optional: {key})"
        for key, value in cmd_params.items()
    ]

    if len(params) > 0:
        return "```Usage: {}{} <{}>```".format(prefix, cmd, "> <".join(params))
    else:
        return "```Usage: {}{}```".format(prefix, cmd)


# Date string
def date_string(time, unit):
    time = int(time)
    if time == 1:
        if unit == "second":
            return f"1 {unit}"
        else:
            return f"1 {unit},"
    elif time == 0:
        return ""
    else:
        if unit == "second":
            return f"{time} {unit}s"
        return f"{time} {unit}s,"


def setup(bot):
    bot.add_cog(ErrorHandling(bot))
