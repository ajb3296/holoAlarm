import os
import discord
from discord import option
from discord.ext import commands
from discord.commands import slash_command

from bot.utils.database import channelDataDB
from bot.utils.language import i18n
from bot import LOGGER, BOT_NAME_TAG_VER, COLOR_CODE, OWNERS

lanPack = []
for file in os.listdir("bot/language"):
    if file.endswith(".json"):
        lanPack.append(file.replace(".json", ""))

class AlarmSet(commands.Cog):
    def __init__ (self, bot):
        self.bot = bot

    @slash_command()
    @option("table", description="알람 소스를 선택하세요", choices=["Hololive", "VROZ"])
    @option("onoff", description="이 채널에서의 알람을 켜거나 끕니다", choices=["ON", "OFF"])
    @option("language", description="언어를 선택합니다", choices=lanPack)
    async def alarmset (self, ctx, table: str, onoff: str, language: str):
        """ 이 채널에서 홀로라이브 스케쥴 알림을 켜거나 끕니다 """
        # 오너가 아닐 경우 관리자 권한이 있는지 확인
        if ctx.author.id not in OWNERS:
            if not ctx.author.guild_permissions.manage_messages:
                embed=discord.Embed(title="이 명령어는 서버의 관리자만이 사용할 수 있습니다!")
                embed.set_footer(text=BOT_NAME_TAG_VER)
                return await ctx.respond(embed=embed)

        # onoff를 소문자로 변환
        onoff = onoff.lower()

        # 땜빵
        if table == "hololive":
            table = "broadcastChannel"

        # 채널 알림 상태를 DB에 저장
        channelDataDB().channel_status_set(table, ctx.channel.id, onoff, language)

        if onoff == "on":
            msg_title = f":green_circle: {i18n(ctx.author.id, 'alarm_onoff', '이 채널에서 알람을 켰습니다')}"
        else:
            msg_title = f":red_circle: {i18n(ctx.author.id, 'alarm_onoff', '이 채널에서 알람을 껐습니다')}"
        embed=discord.Embed(title="알람 설정", description=msg_title, color=COLOR_CODE)

        embed.set_footer(text=BOT_NAME_TAG_VER)
        await ctx.respond(embed=embed)
    
    @slash_command()
    @option("table", description="알람이 켜져있는지 확인할 소스를 선택하세요", choices=["Hololive", "VROZ"])
    async def alarmstatus (self, ctx, table: str):
        """ 이 채널에서 해당 소스의 알람이 켜져있는지 확인합니다. """
        # 땜빵
        if table == "Hololive":
            table = "broadcastChannel"

        on_channel_list = channelDataDB().get_on_channel(table)
        if ctx.channel.id in on_channel_list:
            msg_title = f":green_circle: {i18n(ctx.author.id, 'alarm_onoff', '이 채널에서 알람이 켜져있습니다.')}"
        else:
            msg_title = f":red_circle: {i18n(ctx.author.id, 'alarm_onoff', '이 채널에서 알람이 꺼져있습니다.')}"
        embed=discord.Embed(title=i18n(ctx.author.id, 'alarm_onoff', '채널 알람 상태'), description=msg_title, color=COLOR_CODE)

        embed.set_footer(text=BOT_NAME_TAG_VER)
        await ctx.respond(embed=embed)

def setup(bot):
    bot.add_cog (AlarmSet(bot))
    LOGGER.info('AlarmSet loaded!')