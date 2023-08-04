import discord
from discord import option
from discord.ext import commands
from discord.commands import slash_command

from bot.utils.database import Muted
from bot.utils.language import i18n
from bot import LOGGER, BOT_NAME_TAG_VER, COLOR_CODE, OWNERS

class MuteCheck(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command()
    @option("onoff", description="이 채널에서의 뮤트 우회 시도 알림을 켜거나 끕니다", choices=["ON", "OFF"])
    @option("role", description="뮤트 역할을 입력하세요")
    async def mutealarmset(self, ctx, onoff: str, role: discord.Role):
        """ 이 채널에서의 뮤트 우회 시도 알림을 켜거나 끕니다 """
        # 오너가 아닐 경우 관리자 권한이 있는지 확인
        if ctx.author.id not in OWNERS:
            if not ctx.author.guild_permissions.manage_messages:
                embed=discord.Embed(title="이 명령어는 서버의 관리자만이 사용할 수 있습니다!")
                embed.set_footer(text=BOT_NAME_TAG_VER)
                return await ctx.respond(embed=embed)

        # onoff를 소문자로 변환
        onoff = onoff.lower()

        # 채널 알림 상태를 DB에 저장
        muted = Muted()
        muted.open()
        if onoff == "on":
            muted.enroll_guild(ctx.guild.id, ctx.channel.id, role.id)
            msg_title = f":green_circle: {i18n(ctx.author.id, 'alarm_onoff', '이 채널에서 알람을 켰습니다')}"
        else:
            muted.delete_guild(ctx.guild.id)
            msg_title = f":red_circle: {i18n(ctx.author.id, 'alarm_onoff', '이 채널에서 알람을 껐습니다')}"
        muted.close()

        embed=discord.Embed(title="알람 설정", description=msg_title, color=COLOR_CODE)

        embed.set_footer(text=BOT_NAME_TAG_VER)
        await ctx.respond(embed=embed)

def setup(bot):
    bot.add_cog(MuteCheck(bot))
    LOGGER.info('MuteCheck loaded!')