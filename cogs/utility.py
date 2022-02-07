import os
import platform
import random
import sys

import hikari
import psutil
import lightbulb
from hurry.filesize import size

plugin = lightbulb.Plugin("Utility")


@plugin.command
@lightbulb.command("help", "View MO help.")
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def _help(ctx: lightbulb.Context):
    embed = hikari.Embed(
        title="MOBot Help",
        colour=hikari.Colour.from_hex_code("9C59B6")
    )
    embed.add_field(name="tag <tag>", value="Shows you the specified tag")
    embed.add_field(name="create <name> <content>", value="Creates a tag")
    embed.add_field(name="delete <tag>", value="Deletes a tag")
    embed.add_field(name="edit <name/content> <tag> <value>", value="Edits the name or the content of "
                                                                    "a tag you own")
    embed.add_field(name="list", value="Gives a list of the tags you've created")
    embed.add_field(name="listall", value="Gives a list of the tags (all of them)")
    embed.add_field(name="ping", value="Gives the latency")
    embed.add_field(name="info <tag>", value="Gives info about a tag")
    embed.add_field(name="about", value="About the bot")
    embed.add_field(name="random", value="Gives a random tag")
    embed.add_field(name="credits", value="Bots credits")
    embed.add_field(name="invite", value="Invite link for MO")
    embed.add_field(name="support", value="Support server for MO")
    embed.add_field(name="vote", value="Vote link for MO")
    embed.add_field(name="patreon", value="Patreon page link for MO")
    embed.set_thumbnail("https://cdn.discordapp.com/avatars/7738394075969618"
                        "03/c32e9d106e4204ca6e68f2ec5b959c32.webp?size=1024")
    await ctx.respond(embed=embed)


@plugin.command
@lightbulb.command("ping", "View MO's latency.")
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def ping(ctx):
    await ctx.send(f"**{round(ctx.bot.heartbeat_latency * 1000)}ms**")


@plugin.command
@lightbulb.add_checks(lightbulb.guild_only)
@lightbulb.add_checks(lightbulb.owner_only)
@lightbulb.command("sudo", "Developer commands for MO.")
@lightbulb.implements(lightbulb.PrefixCommandGroup, lightbulb.SlashCommandGroup)
async def sudo(ctx: lightbulb.Context):
    await ctx.respond("\nthis is the list of the sudo commands:\n"
                      "reload - reloads the cogs\n"
                      "fuckoff / die - shuts the bot down\n"
                      "servers - gives the server count\n"
                      "system - gives system info")


@sudo.child
@lightbulb.add_checks(lightbulb.guild_only)
@lightbulb.add_checks(lightbulb.owner_only)
@lightbulb.command("reload", "Reload cogs.")
@lightbulb.implements(lightbulb.PrefixSubCommand, lightbulb.SlashSubCommand)
async def reload(ctx: lightbulb.Context):
    await ctx.respond("reloading cogs lol")
    try:
        for element in os.listdir("cogs"):
            if element != "__pycache__":
                ctx.bot.reload_extensions(f"cogs.{element.replace('.py', '')}")
        await ctx.respond("done :flushed:")
    except Exception as e:
        await ctx.respond(repr(e))


@sudo.child
@lightbulb.add_checks(lightbulb.guild_only)
@lightbulb.add_checks(lightbulb.owner_only)
@lightbulb.command("servers", "Show amount of guilds MO is in.")
@lightbulb.implements(lightbulb.PrefixSubCommand, lightbulb.SlashSubCommand)
async def servers(ctx: lightbulb.Context):
    await ctx.respond(len(await ctx.bot.rest.fetch_my_guilds()))


@sudo.child
@lightbulb.add_checks(lightbulb.guild_only)
@lightbulb.add_checks(lightbulb.owner_only)
@lightbulb.command("die", "Kill MO, so it won't run anymore.")
@lightbulb.implements(lightbulb.PrefixSubCommand, lightbulb.SlashSubCommand)
async def die(ctx: lightbulb.Context):
    sad = ["goodbye cruel world :pensive: :v:", "why you do this to me :sob:", "bro...",
           "fuck off i dont need you :rage:"]
    await ctx.respond(random.choice(sad))
    sys.exit(0)


@sudo.child
@lightbulb.add_checks(lightbulb.guild_only)
@lightbulb.add_checks(lightbulb.owner_only)
@lightbulb.command("h", "h")
@lightbulb.implements(lightbulb.PrefixSubCommand, lightbulb.SlashSubCommand)
async def h(ctx: lightbulb.Context):
    await ctx.respond("hhhhhhhhhhhhh")


@sudo.child
@lightbulb.add_checks(lightbulb.guild_only)
@lightbulb.add_checks(lightbulb.owner_only)
@lightbulb.command("system", "Show system information of MO.")
@lightbulb.implements(lightbulb.PrefixSubCommand, lightbulb.SlashSubCommand)
async def system(ctx: lightbulb.Context):
    embed = hikari.Embed(
        title="Bot System Information",
        color=hikari.Colour.from_hex_code("9C59B6")
    )

    embed.add_field(name="‎", value="**CPU**", inline=False)
    embed.add_field(name="CPU Usage", value=str(psutil.cpu_percent()) + "%")
    embed.add_field(name="Logical CPU Count", value=str(psutil.cpu_count()))

    mem = psutil.virtual_memory()
    embed.add_field(name="‎", value="**Memory**", inline=False)
    embed.add_field(name="Total Memory", value=size(mem.total) + "B")
    embed.add_field(name="Available Memory", value=size(mem.available) + "B")
    embed.add_field(name="Memory Usage", value=str(mem.percent) + "%")

    disk = psutil.disk_usage("/")
    embed.add_field(name="‎", value="**Disk**", inline=False)
    embed.add_field(name="Total Space", value=size(disk.total) + "B")
    embed.add_field(name="Used Space", value=size(disk.used) + "B")
    embed.add_field(name="Free Space", value=size(disk.free) + "B")
    embed.add_field(name="Disk Usage", value=str(disk.percent) + "%")

    net = psutil.net_io_counters()
    embed.add_field(name="‎", value="**Network**", inline=False)
    embed.add_field(name="Packets Sent", value=str(net.packets_sent))
    embed.add_field(name="Packets Received", value=str(net.packets_recv))
    embed.add_field(name="Bytes Sent", value=size(net.bytes_sent) + "B")
    embed.add_field(name="Bytes Received", value=size(net.bytes_recv) + "B")

    embed.add_field(name="‎", value="**OS**", inline=False)
    embed.add_field(name="System", value=platform.system())
    if len(platform.release()) != 0:
        embed.add_field(name="Release", value=platform.release())
    else:
        embed.add_field(name="Release", value="???")
    if len(platform.version()) != 0:
        embed.add_field(name="Version", value=platform.version())
    else:
        embed.add_field(name="Release", value="???")

    await ctx.respond(embed=embed)


@plugin.command
@lightbulb.command("credits", "Show the credits.")
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def _credits(ctx: lightbulb.Context):
    makufon = ctx.bot.cache.get_user(444550944110149633)
    human = ctx.bot.cache.get_user(429935667737264139)
    lunah = ctx.bot.cache.get_user(603635602809946113)
    embed = hikari.Embed(
        title=":busts_in_silhouette: MOBot Credits",
        description="These are the epic people who made MOBot possible",
        colour=hikari.Colour.from_hex_code("9C59B6")
    )
    embed.add_field(name="<:verified_dev:935128864596824084> Developer:", value=str(makufon))
    embed.add_field(name="<:verified_dev:935128864596824084> Recoder:", value=str(lunah))
    embed.add_field(name=":star: Special Thanks:", value=f"{lunah}\n{human}")
    embed.add_field(name=":computer: Library:", value=f"Hikari {hikari.__version__}")
    embed.add_field(name=":floppy_disk:  DB Used:", value="SQLite")
    embed.set_footer(text="Bots name and icon by GD level MO by MenhHue and Knots (ID: 62090339)")
    await ctx.respond(embed=embed)


@plugin.command
@lightbulb.command("invite", "Invite MO.")
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def invite(ctx: lightbulb.Context):
    await ctx.respond("**You can add MO to your servers with using this link:** https://bit.ly/2UewLw5")


@plugin.command
@lightbulb.command("support", "Join the support server for MO (dead).")
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def support(ctx: lightbulb.Context):
    await ctx.respond("**Here is the invite link for the support server of MO:** https://discord.gg/6PX24ZPnDt")


@plugin.command
@lightbulb.command("vote", "Vote for MO (dead?).")
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def vote(ctx: lightbulb.Context):
    await ctx.respond("**Here is the vote link for MO:** https://top.gg/bot/773839407596961803/vote")


@plugin.command
@lightbulb.command("patreon", "Support MO on our Patreon (dead!).")
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def patreon(ctx: lightbulb.Context):
    await ctx.respond("**Here is our Patreon page, I put a lot of time in the bot and would appreciate your support.**"
                      "\nhttps://www.patreon.com/mobot")


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove_plugin(plugin)
