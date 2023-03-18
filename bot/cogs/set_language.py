import os
import sqlite3
import discord
from discord.ext import commands
from discord.commands import slash_command, Option

from bot import LOGGER, BOT_NAME_TAG_VER, color_code

lanPack = []
for file in os.listdir("bot/language"):
    if file.endswith(".json"):
        lanPack.append(file.replace(".json", ""))

class Language (commands.Cog):
    def __init__ (self, bot):
        self.bot = bot
        self.userdata_db_path = "userdata.db"

    @slash_command()
    async def language (self, ctx, lang : Option(str, "Choose language pack.", choices=lanPack)):
        """ Apply the language pack. """
        if lang is None:
            files = ""
            for file in os.listdir("bot/language"):
                if file.endswith(".json"):
                    files = files + file.replace(".json", "") + "\n"

            embed=discord.Embed(title="Language packs", description=files, color=color_code)
            embed.set_footer(text=BOT_NAME_TAG_VER)
            return await ctx.respond(embed=embed)

        if not os.path.exists(f"bot/language/{lang}.json"):
            embed=discord.Embed(title="The language file does not exist!", color=color_code)
            embed.set_footer(text=BOT_NAME_TAG_VER)
            return await ctx.respond(embed=embed)

        conn = sqlite3.connect(self.userdata_db_path, isolation_level=None)
        c = conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS userdata (id integer PRIMARY KEY, language text)")
        # chack user data
        c.execute("SELECT * FROM userdata WHERE id=:id", {"id": str(ctx.author.id)})
        a = c.fetchone()
        if a is None:
            # add user data
            c.execute(f"INSERT INTO userdata VALUES({ctx.author.id}, '{lang}')")
            embed=discord.Embed(title="Language setting complete!", description=f"{lang}", color=color_code)
        else:
            # modify user data
            c.execute("UPDATE userdata SET language=:language WHERE id=:id", {"language": lang, 'id': ctx.author.id})
            embed=discord.Embed(title="Language setting complete!", description=f"{a[1]} --> {lang}", color=color_code)
        conn.close()

        embed.set_footer(text=BOT_NAME_TAG_VER)
        await ctx.respond(embed=embed)

def setup (bot):
    bot.add_cog (Language (bot))
    LOGGER.info('Language loaded!')