import discord
from discord.ext import commands
from discord.commands import slash_command

from bot import LOGGER, BOT_NAME_TAG_VER, color_code

class About (commands.Cog) :
    def __init__ (self, bot) :
        self.bot = bot

    @slash_command()
    async def about (self, ctx) :
        """ 봇에 대한 소개 """
        embed=discord.Embed(title="봇 정보", description="홀로 스케쥴 봇이 사망해서 직접 만듦", color=color_code)
        embed.add_field(name="Developer", value="천상의나무", inline=True)
        embed.add_field(name="관련 링크", value="[Github](https://github.com/ajb3296/holoAlarm)\n[Hololive schedule](https://schedule.hololive.tv/)", inline=True)
        embed.set_footer(text=BOT_NAME_TAG_VER)
        await ctx.respond(embed=embed)

def setup (bot) :
    bot.add_cog (About (bot))
    LOGGER.info('About loaded!')