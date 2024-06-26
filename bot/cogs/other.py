import discord
from discord.ext import commands
import subprocess
from discord.commands import slash_command

from bot.utils.language import i18n
from bot import LOGGER, BOT_NAME_TAG_VER, COLOR_CODE

class Other(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command()
    async def invite(self, ctx):
        """ 봇 초대 링크 전송 """
        link = f'https://discord.com/api/oauth2/authorize?client_id={self.bot.user.id}&permissions=8&scope=bot%20applications.commands' # 알리미 기능만 사용시 : 414464789568
        embed=discord.Embed(title="초대링크", description=i18n(ctx.author.id, "other", "봇을 초대할 다른 서버의 관리자라면 [링크]({link})를 클릭하면 됩니다.").format(link=link), color=COLOR_CODE)
        embed.set_footer(text=BOT_NAME_TAG_VER)
        await ctx.respond(embed=embed)

    @slash_command()
    async def uptime(self, ctx):
        """ 서버 업타임 """
        res = subprocess.check_output("uptime", shell=False, encoding='utf-8')
        embed=discord.Embed(title="Uptime", description="```%s```" %res.replace(',  ', '\n').replace(', ', '\n').replace(': ', ' : ')[1:], color=COLOR_CODE)
        embed.set_footer(text=BOT_NAME_TAG_VER)
        await ctx.respond(embed=embed)

def setup(bot):
    bot.add_cog(Other(bot))
    LOGGER.info('Other loaded!')