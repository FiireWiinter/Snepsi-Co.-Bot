import discord
from discord.ext import commands
import datetime
import json

with open("config.json") as f:
    data = json.load(f)
    prefix = data["prefix"]
    owners = data["owners"]


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def help(self, ctx, cmd=None):
        client = self.bot
        creator = await client.fetch_user(315098355913064461)
        author = ctx.author

        if cmd is None:
            embed = discord.Embed(
                title=f"Type {prefix}help <command> for more info on a command!",
                description=f"Hi there! I'm {self.bot.user.name} and below you can see all the "
                            f"commands that I currently know.\n",
                color=discord.Color.blue(),
            )

            embed.set_author(name=author.display_name, icon_url=author.avatar_url)
            current_time = datetime.datetime.utcnow()
            embed.set_footer(
                text=f"A Discord bot made with ❤ by {creator.name}#{creator.discriminator}"
                f" ・ Uptime: {self.uptime(current_time)}."
            )

            cogs_list = []
            for cog in client.cogs:
                cog_ = client.get_cog(cog)
                cog_length = len(cog_.get_commands())
                cogs_list.append((cog, cog_length))

            cogs_list.sort(key=lambda tup: tup[1], reverse=True)
            client_cogs = [entry[0] for entry in cogs_list]

            for cog in client_cogs:
                cog = client.get_cog(cog)
                if author.id in owners:
                    cmd = '`, `'.join(c.name for c in cog.get_commands())
                else:
                    cmd = '`, `'.join(c.name for c in cog.get_commands() if c.hidden is False)
                cmd.replace("_", "")

                if cmd == "":
                    continue
                else:
                    cog_name = cog.__class__.__name__

                    embed.add_field(name=f"{cog_name}:", value=f"`{cmd}`", inline=False)

            try:
                await ctx.send(
                    f"{author.mention} I sent you a list of commands in DMs!"
                )
                await author.send(embed=embed)
            except discord.Forbidden:
                await ctx.send(
                    f"{author.mention} I couldn't DM you the help list. "
                    f"Please ensure that you have your DMs open and I am not blocked."
                )
        else:
            command = client.get_command(cmd)
            try:
                print(command.clean_params)
                help_msg = help_formatter(command, command.clean_params)
                desc = "```Description: {}```".format(command.description)
                await ctx.send(help_msg + desc)
            except AttributeError:
                await ctx.send(
                    f"That is not a valid command! Please do ``{prefix}help`` for a list of valid commands!"
                )

    # Up-time formatter
    def uptime(self, cur_time):
        elapsed_time = cur_time - self.bot.start_time
        days = divmod(elapsed_time.total_seconds(), 86400)
        hours = divmod(days[1], 3600)
        minutes = divmod(hours[1], 60)
        seconds = divmod(minutes[1], 1)

        dt = date_string(days[0], "day")
        ht = date_string(hours[0], "hour")
        mt = date_string(minutes[0], "minute")
        st = date_string(seconds[0], "second")

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


def setup(bot):
    bot.add_cog(Help(bot))
