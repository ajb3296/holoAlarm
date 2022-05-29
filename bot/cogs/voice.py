import discord
import asyncio
from discord.ext import commands
import sqlite3
from discord.commands import slash_command

from bot.utils.language import i18n
from bot import LOGGER, BOT_NAME_TAG_VER, color_code, OWNERS, VOICE_DB

class Voice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.voice_db = VOICE_DB

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        conn = sqlite3.connect(self.voice_db, isolation_level=None)
        c = conn.cursor()
        guildID = member.guild.id
        c.execute("SELECT voiceChannelID FROM guild WHERE guildID = ?", (guildID,))
        voice=c.fetchone()
        if voice is None:
            pass
        else:
            voiceID = voice[0]
            try:
                if after.channel.id == voiceID:
                    c.execute("SELECT * FROM voiceChannel WHERE userID = ?", (member.id,))
                    cooldown=c.fetchone()
                    if cooldown is None:
                        pass
                    else:
                        embed=discord.Embed(title=f':warning: {i18n(member.id, "voice", "채널을 너무 빨리 생성하면 15초의 재사용 대기시간이 발생합니다!")}', color=color_code)
                        embed.set_footer(text=BOT_NAME_TAG_VER)
                        await member.send(embed=embed)
                        await asyncio.sleep(15)
                    c.execute("SELECT voiceCategoryID FROM guild WHERE guildID = ?", (guildID,))
                    voice=c.fetchone()
                    c.execute("SELECT channelName, channelLimit FROM userSettings WHERE userID = ?", (member.id,))
                    setting=c.fetchone()
                    c.execute("SELECT channelLimit FROM guildSettings WHERE guildID = ?", (guildID,))
                    guildSetting=c.fetchone()
                    if setting is None:
                        name = f"{member.name}'s channel"
                        if guildSetting is None:
                            limit = 0
                        else:
                            limit = guildSetting[0]
                    else:
                        if guildSetting is None:
                            name = setting[0]
                            limit = setting[1]
                        elif guildSetting is not None and setting[1] == 0:
                            name = setting[0]
                            limit = guildSetting[0]
                        else:
                            name = setting[0]
                            limit = setting[1]
                    categoryID = voice[0]
                    id = member.id
                    category = self.bot.get_channel(categoryID)
                    channel2 = await member.guild.create_voice_channel(name,category=category)
                    channelID = channel2.id
                    await member.move_to(channel2)
                    await channel2.set_permissions(self.bot.user, connect=True,read_messages=True)
                    await channel2.edit(name= name, user_limit = limit)
                    c.execute("INSERT INTO voiceChannel VALUES (?, ?)", (id,channelID))
                    
                    def check(a,b,c):
                        return len(channel2.members) == 0
                    await self.bot.wait_for('voice_state_update', check=check)
                    await channel2.delete()
                    await asyncio.sleep(3)
                    c.execute('DELETE FROM voiceChannel WHERE userID=?', (id,))
            except Exception as e:
                print(e)
        conn.close()

    @slash_command()
    async def setup(self, ctx, category_name, voice_channel_name):
        """ 초기 설정 """
        conn = sqlite3.connect(self.voice_db, isolation_level=None)
        c = conn.cursor()
        guildID = ctx.guild.id
        userId = ctx.author.id
        if ctx.author.guild_permissions.manage_messages or userId in OWNERS:
            new_cat = await ctx.guild.create_category_channel(category_name)
            try:
                channel = await ctx.guild.create_voice_channel(voice_channel_name, category=new_cat)
                c.execute("SELECT * FROM guild WHERE guildID = ? AND ownerID=?", (guildID, userId))
                voice=c.fetchone()
                if voice is None:
                    c.execute ("INSERT INTO guild VALUES (?, ?, ?, ?)",(guildID, userId, channel.id, new_cat.id))
                else:
                    c.execute ("UPDATE guild SET guildID = ?, ownerID = ?, voiceChannelID = ?, voiceCategoryID = ? WHERE guildID = ?",(guildID, userId, channel.id, new_cat.id, guildID))

                embed=discord.Embed(title=f':white_check_mark: {i18n(ctx.author.id, "voice", "모든 설정이 완료되었으며 사용할 준비가 되었습니다!")}', color=color_code)
                embed.set_footer(text=BOT_NAME_TAG_VER)
                await ctx.respond(embed=embed)
            except Exception as e:
                embed=discord.Embed(title=f':warning: {i18n(ctx.author.id, "voice", "이름을 제대로 입력하지 않았습니다.")} {e}', description=i18n(ctx.author.id, "voice", "`/setup` 명령어를 다시 사용하세요!"), color=color_code)
                embed.set_footer(text=BOT_NAME_TAG_VER)
                await ctx.respond(embed=embed)

        else:
            embed=discord.Embed(title=f':warning: {i18n(ctx.author.id, "voice", "서버 관리자만 봇을 설정할 수 있습니다!")}', color=color_code)
            embed.set_footer(text=BOT_NAME_TAG_VER)
            await ctx.respond(embed=embed)
        conn.close()

    @slash_command()
    async def setlimit(self, ctx, num):
        """ 기본 채널 리미트 설정 """
        conn = sqlite3.connect(self.voice_db, isolation_level=None)
        c = conn.cursor()
        if ctx.author.guild_permissions.manage_messages or ctx.author.id in OWNERS:
            c.execute("SELECT * FROM guildSettings WHERE guildID = ?", (ctx.guild.id,))
            voice=c.fetchone()
            if voice is None:
                c.execute("INSERT INTO guildSettings VALUES (?, ?, ?)", (ctx.guild.id,f"{ctx.author.name}'s channel",num))
            else:
                c.execute("UPDATE guildSettings SET channelLimit = ? WHERE guildID = ?", (num, ctx.guild.id))

            embed=discord.Embed(title=f':white_check_mark: {i18n(ctx.author.id, "voice", "서버의 기본 채널 리미트를 변경했습니다!")}', color=color_code)
            embed.set_footer(text=BOT_NAME_TAG_VER)
            await ctx.respond(embed=embed)
        else:
            embed=discord.Embed(title=f':warning: {i18n(ctx.author.id, "voice", "서버 관리자만 봇을 설정할 수 있습니다!")}', color=color_code)
            embed.set_footer(text=BOT_NAME_TAG_VER)
            await ctx.respond(embed=embed)
        conn.close()

    @setup.error
    async def info_error(self, ctx, error):
        print(error)

    @slash_command()
    async def lock(self, ctx):
        """ 음성채널 잠금 """
        conn = sqlite3.connect(self.voice_db, isolation_level=None)
        c = conn.cursor()
        id = ctx.author.id
        c.execute("SELECT voiceID FROM voiceChannel WHERE userID = ?", (id,))
        voice=c.fetchone()
        if voice is None:
            embed=discord.Embed(title=f':warning: {i18n(ctx.author.id, "voice", "채널의 주인이 아닙니다!")}', color=color_code)
            embed.set_footer(text=BOT_NAME_TAG_VER)
            await ctx.respond(embed=embed)
        else:
            channelID = voice[0]
            role = ctx.guild.default_role
            channel = self.bot.get_channel(channelID)
            await channel.set_permissions(role, connect=False)
            embed=discord.Embed(title=f':lock: {i18n(ctx.author.id, "voice", "음성채널을 잠궜습니다!")}', color=color_code)
            embed.set_footer(text=BOT_NAME_TAG_VER)
            await ctx.respond(embed=embed)
        conn.close()

    @slash_command()
    async def unlock(self, ctx):
        """ 음성채널 잠금해제 """
        conn = sqlite3.connect(self.voice_db, isolation_level=None)
        c = conn.cursor()
        id = ctx.author.id
        c.execute("SELECT voiceID FROM voiceChannel WHERE userID = ?", (id,))
        voice=c.fetchone()
        if voice is None:
            embed=discord.Embed(title=f':warning: {i18n(ctx.author.id, "voice", "채널의 주인이 아닙니다!")}', color=color_code)
            embed.set_footer(text=BOT_NAME_TAG_VER)
            await ctx.respond(embed=embed)
        else:
            channelID = voice[0]
            role = ctx.guild.default_role
            channel = self.bot.get_channel(channelID)
            await channel.set_permissions(role, connect=True)
            embed=discord.Embed(title=f':unlock: {i18n(ctx.author.id, "voice", "음성채널의 잠금을 풀었습니다!")}', color=color_code)
            embed.set_footer(text=BOT_NAME_TAG_VER)
            await ctx.respond(embed=embed)
        
        conn.close()

    @slash_command()
    async def permit(self, ctx, member : discord.Member):
        """ 잠긴 음성채널에 멤버 초대 """
        conn = sqlite3.connect(self.voice_db, isolation_level=None)
        c = conn.cursor()
        userId = ctx.author.id
        c.execute("SELECT voiceID FROM voiceChannel WHERE userID = ?", (userId,))
        voice=c.fetchone()
        if voice is None:
            embed=discord.Embed(title=f':warning: {i18n(ctx.author.id, "voice", "채널의 주인이 아닙니다!")}', color=color_code)
            embed.set_footer(text=BOT_NAME_TAG_VER)
            await ctx.respond(embed=embed)
        else:
            channelID = voice[0]
            channel = self.bot.get_channel(channelID)
            await channel.set_permissions(member, connect=True)

            embed=discord.Embed(title=f':white_check_mark: {i18n(ctx.author.id, "voice", "{member}님에게 채널에 접근한 권한을 줬어요!").format(member=member.name)}', color=color_code)
            embed.set_footer(text=BOT_NAME_TAG_VER)
            await ctx.respond(embed=embed)
        conn.close()

    @slash_command()
    async def reject(self, ctx, member : discord.Member):
        """ 잠긴 음성채널에서 멤버의 접근권한 뺏기 """
        conn = sqlite3.connect(self.voice_db, isolation_level=None)
        c = conn.cursor()
        userId = ctx.author.id
        guildID = ctx.guild.id
        c.execute("SELECT voiceID FROM voiceChannel WHERE userID = ?", (userId,))
        voice=c.fetchone()
        if voice is None:
            embed=discord.Embed(title=f':warning: {i18n(ctx.author.id, "voice", "채널의 주인이 아닙니다!")}', color=color_code)
            embed.set_footer(text=BOT_NAME_TAG_VER)
            await ctx.respond(embed=embed)
        else:
            channelID = voice[0]
            channel = self.bot.get_channel(channelID)
            for members in channel.members:
                if members.id == member.id:
                    c.execute("SELECT voiceChannelID FROM guild WHERE guildID = ?", (guildID,))
                    voice=c.fetchone()
                    channel2 = self.bot.get_channel(voice[0])
                    await member.move_to(channel2)
            await channel.set_permissions(member, connect=False,read_messages=True)

            embed=discord.Embed(title=f':x: {i18n(ctx.author.id, "voice", "{member}님에게서 채널에 접근한 권한을 뺏었어요!").format(member=member.name)}', color=color_code)
            embed.set_footer(text=BOT_NAME_TAG_VER)
            await ctx.respond(embed=embed)
        conn.close()

    @slash_command()
    async def limit(self, ctx, limit):
        """ 채널 리미트 설정 """
        conn = sqlite3.connect(self.voice_db, isolation_level=None)
        c = conn.cursor()
        userId = ctx.author.id
        c.execute("SELECT voiceID FROM voiceChannel WHERE userID = ?", (userId,))
        voice=c.fetchone()
        if voice is None:
            embed=discord.Embed(title=f':warning: {i18n(ctx.author.id, "voice", "채널의 주인이 아닙니다!")}', color=color_code)
            embed.set_footer(text=BOT_NAME_TAG_VER)
            await ctx.respond(embed=embed)
        else:
            channelID = voice[0]
            channel = self.bot.get_channel(channelID)
            await channel.edit(user_limit = limit)
            embed=discord.Embed(title=f':white_check_mark: {i18n(ctx.author.id, "voice", "채널 리미트를 {limit} 으로 설정했어요").format(limit=limit)}', color=color_code)
            embed.set_footer(text=BOT_NAME_TAG_VER)
            await ctx.respond(embed=embed)

            c.execute("SELECT channelName FROM userSettings WHERE userID = ?", (userId,))
            voice=c.fetchone()
            if voice is None:
                c.execute("INSERT INTO userSettings VALUES (?, ?, ?)", (userId, f'{ctx.author.name}',limit))
            else:
                c.execute("UPDATE userSettings SET channelLimit = ? WHERE userID = ?", (limit, userId))
        conn.close()


    @slash_command()
    async def name(self, ctx, *, name):
        """ 채널 이름 변경 """
        conn = sqlite3.connect(self.voice_db, isolation_level=None)
        c = conn.cursor()
        userId = ctx.author.id
        c.execute("SELECT voiceID FROM voiceChannel WHERE userID = ?", (userId,))
        voice=c.fetchone()
        if voice is None:
            embed=discord.Embed(title=f':warning: {i18n(ctx.author.id, "voice", "채널의 주인이 아닙니다!")}', color=color_code)
            embed.set_footer(text=BOT_NAME_TAG_VER)
            await ctx.respond(embed=embed)
        else:
            channelID = voice[0]
            channel = self.bot.get_channel(channelID)
            await channel.edit(name = name)
            embed=discord.Embed(title=f':white_check_mark: {i18n(ctx.author.id, "voice", "채널명을 {name} (으)로 변경했어요!").format(name=name)}', color=color_code)
            embed.set_footer(text=BOT_NAME_TAG_VER)
            await ctx.respond(embed=embed)

            c.execute("SELECT channelName FROM userSettings WHERE userID = ?", (userId,))
            voice=c.fetchone()
            if voice is None:
                c.execute("INSERT INTO userSettings VALUES (?, ?, ?)", (userId, name, 0))
            else:
                c.execute("UPDATE userSettings SET channelName = ? WHERE userID = ?", (name, userId))
        
        conn.close()

    @slash_command()
    async def claim(self, ctx):
        """ 채널 관리자가 나갔을 경우 관리자를 신청 """
        x = False
        conn = sqlite3.connect(self.voice_db, isolation_level=None)
        c = conn.cursor()
        channel = ctx.author.voice.channel
        if channel == None:
            embed=discord.Embed(title=f':warning: {i18n(ctx.author.id, "voice", "{you}님은 음성채널에 들어가 있지 않습니다!").format(you=ctx.author.name)}', color=color_code)
            embed.set_footer(text=BOT_NAME_TAG_VER)
            await ctx.respond(embed=embed)
        else:
            id = ctx.author.id
            c.execute("SELECT userID FROM voiceChannel WHERE voiceID = ?", (channel.id,))
            voice=c.fetchone()
            if voice is None:
                embed=discord.Embed(title=f':warning: {i18n(ctx.author.id, "voice", "이 음성채널을 소유하실 수 없습니다!")}', color=color_code)
                embed.set_footer(text=BOT_NAME_TAG_VER)
                await ctx.respond(embed=embed)
            else:
                for data in channel.members:
                    if data.id == voice[0]:
                        owner = ctx.guild.get_member(voice [0])
                        await ctx.channel.send(f"{ctx.author.mention} This channel is already owned by {owner.mention}!")
                        embed=discord.Embed(title=f':warning: {i18n(ctx.author.id, "voice", "이 음성채널은 이미 {owner}님의 소유입니다!").format(owner.name)}', color=color_code)
                        embed.set_footer(text=BOT_NAME_TAG_VER)
                        await ctx.respond(embed=embed)
                        x = True
                if x == False:
                    embed=discord.Embed(title=f':white_check_mark: {i18n(ctx.author.id, "voice", "이제 이 음성채널은 {name}님의 것입니다. {name}님 마음대로 관리할 수 있는 겁니다.").format(name=ctx.author.name)}', color=color_code)
                    embed.set_footer(text=BOT_NAME_TAG_VER)
                    await ctx.respond(embed=embed)
                    c.execute("UPDATE voiceChannel SET userID = ? WHERE voiceID = ?", (id, channel.id))
            conn.close()


def setup(bot):
    bot.add_cog(Voice(bot))
    LOGGER.info('Voice loaded!')