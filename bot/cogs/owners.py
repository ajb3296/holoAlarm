import math
import discord
from discord.ext import commands, pages
from discord.commands import slash_command

from bot import LOGGER, BOT_NAME_TAG_VER, color_code, DebugServer, BOT_NAME
from bot.utils.database import channelDataDB

class Owners(commands.Cog):
    def __init__ (self, bot):
        self.bot = bot

    @slash_command(permissions=[commands.is_owner().predicate], guild_ids=DebugServer)
    async def serverlist(self, ctx):
        """ 봇이 들어가 있는 모든 서버 리스트를 출력합니다. """
        page = 10
        # 페이지 지정값이 없고, 총 서버수가 10 이하일 경우
        if len(self.bot.guilds) <= page:
            embed = discord.Embed(title = f"{BOT_NAME} (이)가 들어가 있는 서버목록", description=f"**{len(self.bot.guilds)}개**의 서버", color=color_code)
            srvr = str()
            for i in self.bot.guilds:
                srvr = srvr + f"**{i}** - **{i.member_count}명**\n"
            embed.add_field(name="​", value=srvr, inline=False)
            embed.set_footer(text=BOT_NAME_TAG_VER)
            return await ctx.respond(embed = embed)

        # 서버수가 10개 이상일 경우

        # 총 페이지수 계산
        botguild = self.bot.guilds
        allpage = math.ceil(len(botguild) / page)

        pages_list = []
        for i in range(1, allpage+1):
            srvr = ""
            numb = (page * i)
            numa = numb - page
            for a in range(numa, numb):
                try:
                    srvr = srvr + f"**{botguild[a]}** - **{botguild[a].member_count}명**\n"
                except IndexError:
                    break

            pages_list.append(
                [
                    discord.Embed(title = f"{BOT_NAME} (이)가 들어가 있는 서버목록", description=f"**{len(self.bot.guilds)}개**의 서버\n\n{srvr}")
                ]
            )
        paginator = pages.Paginator(pages=pages_list)
        await paginator.respond(ctx.interaction, ephemeral=False)

    @slash_command(permissions=[commands.is_owner().predicate], guild_ids=DebugServer)
    async def alarmchlist(self, ctx):
        """ 알람이 켜져있는 모든 채널 리스트를 출력합니다. """
        page = 10
        alarm_ch_list = channelDataDB().get_on_channel("broadcastChannel")
        # 페이지 지정값이 없고, 총 서버수가 10 이하일 경우
        if len(alarm_ch_list) <= page:
            embed = discord.Embed(title = f"알람이 켜져있는 채넣", description=f"**{len(alarm_ch_list)}개**의 채널", color=color_code)
            srvr = str()
            for i in alarm_ch_list:
                target_channel = self.bot.get_channel(i)
                srvr = srvr + f"{target_channel.guild} - {target_channel}\n"
            embed.add_field(name="​", value=srvr, inline=False)
            embed.set_footer(text=BOT_NAME_TAG_VER)
            return await ctx.respond(embed = embed)

        # 서버수가 10개 이상일 경우

        # 총 페이지수 계산
        allpage = math.ceil(len(alarm_ch_list) / page)

        pages_list = []
        for i in range(1, allpage+1):
            srvr = ""
            numb = (page * i)
            numa = numb - page
            for a in range(numa, numb):
                try:
                    target_channel = self.bot.get_channel(alarm_ch_list[a])
                    srvr = srvr + f"{target_channel.guild} - {target_channel}\n"
                except IndexError:
                    break

            pages_list.append(
                [
                    discord.Embed(title = "알람이 켜져있는 채널", description=f"**{len(alarm_ch_list)}개**의 채널\n\n{srvr}")
                ]
            )
        paginator = pages.Paginator(pages=pages_list)
        await paginator.respond(ctx.interaction, ephemeral=False)

    @slash_command(permissions=[commands.is_owner().predicate], guild_ids=DebugServer)
    async def banstartswitch(self, ctx, server_id = None, *, startswitch):
        await ctx.defer()
        print(self.bot.guilds)
        if server_id is None:
            server_id = ctx.guild.id
        else:
            if self.bot.guilds not in server_id:
                embed=discord.Embed(title=f':warning: 해당 서버에 들어가있지 않습니다.', color=color_code)
                embed.set_footer(text=BOT_NAME_TAG_VER)
                await ctx.followup.send(embed=embed)

def setup(bot):
    bot.add_cog (Owners(bot))
    LOGGER.info('Owners loaded!')