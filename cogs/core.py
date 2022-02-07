import datetime
import os
import random
import aiosqlite
from difflib import SequenceMatcher
from pathlib import Path

import hikari
import lightbulb
from dotenv import load_dotenv
from imgurpython import ImgurClient
from imgurpython.helpers.error import ImgurClientError

import time_utils

env_path = Path(".") / ".env"
load_dotenv(dotenv_path=env_path)

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

imgurclient = ImgurClient(client_id, client_secret)

start_time = datetime.datetime.utcnow()
plugin = lightbulb.Plugin("Core")

is_vps = False


async def define_db():
    if not is_vps:
        dirr = os.path.dirname(__file__)
        db = await aiosqlite.connect(os.path.join(dirr, "D:/Coding/MObot/tags.db"))
    else:
        print("# VPS MODE")
        dirr = os.path.dirname(__file__)
        db = await aiosqlite.connect(os.path.join(dirr, "/root/mobot/tags.db"))
    sql = await db.cursor()
    return sql, db


@plugin.listener(lightbulb.CommandErrorEvent)
async def on_command_error(event):
    if isinstance(event.exception, lightbulb.NotEnoughArguments):
        embed = hikari.Embed(
            title=":x: Command Raised an Exception!",
            color=hikari.Colour.from_hex_code("ff0000")
        )
        embed.add_field(name="Error:", value=f"```\n{event.exception}\n```")
        embed.set_footer(text=f"{event.exception.__class__.__name__}")
        await event.context.respond(embed=embed)
    elif isinstance(event.exception, lightbulb.MissingRequiredPermission):
        embed = hikari.Embed(
            title=":x: Command Raised an Exception!",
            color=hikari.Colour.from_hex_code("ff0000")
        )
        embed.add_field(
            name="Error:",
            value="**You don't have enough permissions to do that!",
        )

        embed.set_footer(text=f"{event.exception.__class__.__name__}")
        await event.context.respond(embed=embed)
    elif isinstance(event.exception, lightbulb.CommandNotFound):
        suggestion = None
        for command_name, command in zip(event.app.prefix_commands.keys(), event.app.prefix_commands.values()):
            ratio = SequenceMatcher(None, event.exception.invoked_with, command_name).ratio()
            if ratio >= 0.7 and not command.hidden:
                suggestion = command
                break
        if suggestion is None:
            embed = hikari.Embed(
                title=":x: Command not found",
                color=hikari.Colour.from_hex_code("ff0000"),
                description="That command doesn't exist! Use `h.help` for a list of commands.",
            )

        else:
            embed = hikari.Embed(
                title=":x: Command not found",
                color=hikari.Colour.from_hex_code("ff0000"),
                description=f"That command doesn't exist! Did you mean `h.{suggestion.name}`?"
            )
        await event.context.respond(embed=embed)
    elif isinstance(event.exception, lightbulb.CommandIsOnCooldown):
        await event.context.respond(
            f":clock5: That command is on cooldown. Try again in **{int(event.exception.retry_after)}** seconds!")
    else:
        print(event.exception.__cause__)


@plugin.listener(hikari.StartedEvent)
async def on_ready(event):
    print("Bot is ready")


@plugin.listener(hikari.GuildJoinEvent)
async def on_guild_join(event):
    sql, db = await define_db()
    await sql.execute(f'create table if not exists "{event.guild_id}"("id" integer not null,'
                      '"tags_name" text not null, "tags_content" text not null, "tags_date" integer not null,'
                      ' "usage_count" integer not null')


@plugin.command
@lightbulb.option("content", "The content of the tag.", type=str, required=False,
                  modifier=lightbulb.OptionModifier.CONSUME_REST)
@lightbulb.option("name", "The name of the tag.", type=str, required=True)
@lightbulb.command("create", "Create a tag.")
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def create(ctx: lightbulb.Context):
    sql, db = await define_db()
    attachment = ctx.attachments
    compensation = datetime.timedelta(hours=9)
    now = datetime.datetime.now() + compensation

    await sql.execute(f'create table if not exists "{ctx.get_guild().id}"("id" integer not null,'
                      '"tags_name" text not null, "tags_content" text not null, "tags_date" integer not null,'
                      ' "usage_count" integer not null)')

    await sql.execute(f'select tags_name from "{ctx.get_guild().id}" where tags_name = "{ctx.options.name}"')
    if _ := sql.fetchone():
        await ctx.respond(f"Tag named `{ctx.options.name}` already exists!")
    elif attachment and not ctx.options.content:
        image_url = f"{ctx.attachments[0].url}"

        try:
            image = imgurclient.upload_from_url(image_url, config=None, anon=True)

            await sql.execute(
                f'insert into "{ctx.get_guild().id}"(id, tags_name, tags_content, tags_date, usage_count)'
                f'values(?,?,?,?,?)', (ctx.author.id, ctx.options.name, image["link"], now, 0)),
            await db.commit()

            await ctx.respond(f":white_check_mark: Created tag with the name `{ctx.options.name}`")
        except ImgurClientError as e:
            channel = ctx.bot.cache.get_guild_channel(713675042143076356)
            await channel.send(f"IMGUR API BRUTAL ERROR\n"
                               f"```{e.error_message} / {e.status_code}```\n"
                               f"<@444550944110149633>")
            await sql.execute(
                f'insert into "{ctx.get_guild().id}"(id, tags_name, tags_content, tags_date, usage_count)'
                f'values(?,?,?,?,?)', (ctx.author.id, ctx.options.name, ctx.attachments[0].url, now, 0)),
            await db.commit()

            await ctx.respond(f":white_check_mark: Created tag with the name `{ctx.options.name}`")
    else:
        await sql.execute(
            f'insert into "{ctx.get_guild().id}"(id, tags_name, tags_content, tags_date, usage_count)'
            f' values(?,?,?,?,?)',
            (ctx.author.id, ctx.options.name, ctx.options.content, now, 0))
        await db.commit()
        await ctx.respond(f":white_check_mark: Created tag with the name `{ctx.options.name}`")


@plugin.command
@lightbulb.add_cooldown(2, 5, lightbulb.UserBucket)
@lightbulb.option("tag", "The tag you want to see.", type=str, required=True)
@lightbulb.command("tag", "View a tag.")
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def tag(ctx: lightbulb.Context):
    sql, db = await define_db()
    await sql.execute(f'SELECT tags_content FROM "{ctx.get_guild().id}" WHERE tags_name= "{ctx.options.tag}"')
    if final := await sql.fetchone():
        await sql.execute(f'SELECT usage_count FROM "{ctx.get_guild().id}" WHERE tags_name= "{ctx.options.tag}"')
        finalf = await sql.fetchone()
        finaluc = finalf[0] + 1
        finalup = int(finaluc)

        await sql.execute(
            f'UPDATE "{ctx.get_guild().id}" set usage_count = "{finalup}" '
            f'WHERE tags_name = "{ctx.options.tag}"')
        await ctx.respond(final[0])
        await db.commit()
    else:
        await ctx.respond(f"Tag named `{ctx.options.tag}` doesn't exist!")


@plugin.command
@lightbulb.add_checks(lightbulb.has_guild_permissions(hikari.Permissions.MANAGE_MESSAGES))
@lightbulb.option("tag", "The tag you want to delete.", type=str, required=True)
@lightbulb.command("delete", "Delete a tag.")
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def delete(ctx: lightbulb.Context):
    sql, db = await define_db()
    user = ctx.author.id
    await sql.execute(f'SELECT tags_content FROM "{ctx.get_guild().id}" WHERE tags_name= "{ctx.options.tag}"')
    final = await sql.fetchone()

    await sql.execute(f'SELECT id FROM "{ctx.get_guild().id}" WHERE tags_name = "{ctx.options.tag}"')
    id1 = await sql.fetchone()

    if final:
        if id1[0] == user or ctx.author.id in [444550944110149633, 429935667737264139, 603635602809946113]:
            await sql.execute(f'DELETE from "{ctx.get_guild().id}" where tags_name = "{ctx.options.tag}"')
            await db.commit()
            await ctx.respond(f"Tag named `{ctx.options.tag}` deleted successfully")
        else:
            await ctx.respond(":x: You can't delete that tag! If you are the owner or an admin"
                              " of this server, please enter the support server and create ticket"
                              " so we can whitelist you about the tag deletement\n https://discord.gg/6PX24ZPnDt")
    else:
        await ctx.respond(f"Tag named `{ctx.options.tag}` doesn't exist!")


@plugin.command
@lightbulb.option("value", "The new value of that thing.", type=str, required=True,
                  modifier=lightbulb.OptionModifier.CONSUME_REST)
@lightbulb.option("tag", "The tag you're editing.", type=str, required=True)
@lightbulb.option("thing", "The thing to edit.", type=str, required=True)
@lightbulb.command("edit", "Edit a tag.")
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def edit(ctx: lightbulb.Context):
    sql, db = await define_db()
    user = ctx.author.id
    attachment = ctx.attachments
    await sql.execute(f'SELECT tags_content FROM "{ctx.get_guild().id}" WHERE tags_name= "{ctx.options.tag}"')
    final = await sql.fetchone()

    await sql.execute(f'SELECT id FROM "{ctx.get_guild().id}" WHERE tags_name = "{ctx.options.tag}"')
    id1 = await sql.fetchone()

    if final:
        if id1[0] == user or ctx.author.id in [444550944110149633, 429935667737264139, 603635602809946113]:
            if ctx.options.thing.lower() == "content":
                if attachment and not ctx.options.value:
                    image_url = ctx.attachments[0].url
                    image = imgurclient.upload_from_url(image_url, config=None, anon=True)
                    await sql.execute(
                        f'UPDATE "{ctx.get_guild().id}" set tags_content = "{image["link"]}" '
                        f'WHERE tags_name = "{ctx.options.tag}"')
                else:
                    await sql.execute(f'UPDATE "{ctx.get_guild().id}"'
                                      f' set tags_content = "{ctx.options.value}" WHERE tags_name = '
                                      f'"{ctx.options.tag}"')
                await db.commit()
                await ctx.respond(f"Tag named `{ctx.options.tag}` edited successfully")
            elif ctx.options.lower.lower() == "name":
                await sql.execute(
                    f'UPDATE "{ctx.get_guild().id}" set tags_name = "{ctx.options.value}" WHERE tags_name = '
                    f'"{ctx.options.tag}"')
                await db.commit()
                await ctx.respond(f"Tag named `{ctx.options.tag}` edited successfully")
            else:
                await ctx.respond(":x: That is not the correct formatting of the"
                                  " command! Do `h.help` for detailed help of the command.")
        else:
            await ctx.respond(":x: You can't delete that tag! If you are the owner or an admin"
                              " of this server, please enter the support server and create ticket"
                              " so we can whitelist you about the tag deletement\n https://discord.gg/6PX24ZPnDt")
    else:
        await ctx.respond(f"Tag named `{ctx.options.tag}` doesn't exist!")


@plugin.command
@lightbulb.command("list", "List all tags you own in this server.")
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def _list(ctx: lightbulb.Context):
    sql, db = await define_db()
    user = ctx.author.id
    await sql.execute(f'SELECT tags_name FROM "{ctx.get_guild().id}" WHERE id = {user}')
    final = list(await sql.fetchall())
    finallist = str(final)
    finalc = len(final)

    h = finallist.replace("('", "")
    h = h.replace("[", "")
    h = h.replace("',),", "\n")
    h = h.replace("',)]", "")

    if h == "]":
        embed = hikari.Embed(
            title="Tag List",
            colour=hikari.Colour.from_hex_code("9C59B6")
        )
        embed.add_field(name="**Tags:**", value="You don't own any lol")
    else:
        embed = hikari.Embed(
            title="Tag List",
            colour=hikari.Colour.from_hex_code("9C59B6")
        )
        embed.add_field(name="**Tags:**", value=h)
    embed.set_footer(text=f"Tag Count: {finalc}")
    await ctx.respond(embed=embed)


@plugin.command
@lightbulb.command("listall", "List all tags you own in this server.")
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def listall(ctx: lightbulb.Context):
    sql, db = await define_db()
    await sql.execute(f'SELECT tags_name FROM "{ctx.get_guild().id}"')
    final = list(await sql.fetchall())
    finalcount = len(final)

    finalstr = str(final)
    h = finalstr.replace("('", "")
    h = h.replace("[", "")
    h = h.replace("',)]", "")
    h = h.replace("',),", "\n")

    if h == "]":
        embed = hikari.Embed(
            title="Tag List",
            colour=hikari.Colour.from_hex_code("9C59B6")
        )
        embed.add_field(name="**Tags:**", value="there isnt any lol")
    else:
        embed = hikari.Embed(
            title="Tag List",
            colour=hikari.Colour.from_hex_code("9C59B6")
        )
        embed.add_field(name="**Tags:**", value=h)
    embed.set_footer(text=f"Tag Count: {finalcount}")
    await ctx.respond(embed=embed)


@plugin.command
@lightbulb.add_cooldown(2, 5, lightbulb.UserBucket)
@lightbulb.command("random", "Show a random tag from this server.")
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def _random(ctx: lightbulb.Context):
    sql, db = await define_db()
    await sql.execute(f'SELECT tags_name FROM "{ctx.get_guild().id}"')
    name = list(await sql.fetchall())
    the = random.choice(name)

    await sql.execute(f'SELECT tags_content FROM "{ctx.get_guild().id}" WHERE tags_name= "{the[0]}"')
    final = await sql.fetchone()

    await sql.execute(f'SELECT tags_name FROM "{ctx.get_guild().id}" WHERE tags_name= "{the[0]}"')
    tagname = await sql.fetchone()

    await sql.execute(f'SELECT id FROM "{ctx.get_guild().id}" WHERE tags_name= "{the[0]}"')
    owner = await sql.fetchone()
    user = ctx.bot.cache.get_user(owner[0])

    await ctx.respond(f"**Tags Name:** {tagname[0]}\n**Tags Owner:** {user}\n{final[0]}")


@plugin.command
@lightbulb.option("tag", "The tag to show info of.", type=str, required=True)
@lightbulb.command("info", "View information about a tag.")
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def info(ctx: lightbulb.Context):
    sql, db = await define_db()
    await sql.execute(f'SELECT id FROM "{ctx.get_guild().id}" WHERE tags_name = "{ctx.options.tag}"')
    ownerid = await sql.fetchone()

    await sql.execute(f'SELECT tags_date FROM "{ctx.get_guild().id}" WHERE tags_name = "{ctx.options.tag}"')
    date = await sql.fetchone()

    await sql.execute(f'SELECT tags_content FROM "{ctx.get_guild().id}" WHERE tags_name= "{ctx.options.tag}"')
    content = await sql.fetchone()

    await sql.execute(f'SELECT usage_count FROM "{ctx.get_guild().id}" WHERE tags_name= "{ctx.options.tag}"')
    count = await sql.fetchone()

    if content:
        embed = hikari.Embed(
            title=f"Tag Info of {ctx.options.tag}",
            colour=hikari.Colour.from_hex_code("9C59B6")
        )
        embed.add_field(name="Owner:", value=f"<@{ownerid[0]}>")
        embed.add_field(name="Creation Date:", value=date[0][:-7])
        embed.add_field(name="Times it got used:", value=count[0])
        await ctx.respond(embed=embed)
    else:
        await ctx.respond(":x: That tag doesn't seem to exist!")


@plugin.command
@lightbulb.command("about", "View information about MO.")
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def about(ctx: lightbulb.Context):
    user = ctx.bot.cache.get_user(444550944110149633)
    recoder = ctx.bot.cache.get_user(603635602809946113)
    embed = hikari.Embed(
        title="MOBot Info ",
        description="MO is a very powerful tag bot powered with SQLite",
        color=hikari.Colour.from_hex_code("9C59B6")
    )
    embed.add_field(name="Ping:", value=f"{round(ctx.bot.heartbeat_latency * 1000)}ms")
    embed.add_field(name="Command Count:", value=f"{len(ctx.bot.prefix_commands)}")
    embed.add_field(name="Made by:", value=f"{user}")
    embed.add_field(name="Recode by:", value=f"{recoder}")
    embed.add_field(name="Uptime", value=time_utils.get_bot_uptime(start_time))
    await ctx.respond(embed=embed)


@plugin.command
@lightbulb.add_checks(lightbulb.owner_only)
@lightbulb.command("sex", "31")
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def sex(ctx: lightbulb.Context):
    sql, db = await define_db()
    await sql.execute('ALTER TABLE "776135101196009492" ADD COLUMN "imgur_id"')
    await ctx.respond("done :flushed:")


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove_plugin(plugin)
