import os
import json
import discord
import asyncio
import traceback
import urllib.request
from datetime import datetime
from colorthief import ColorThief

from bot.utils.database import *
from bot.utils.language import i18n
from bot import LOGGER, BOT_NAME_TAG_VER, color_code

async def broadcast(bot):
    latest_data = {}
    await asyncio.sleep(5)

    while True:
        try:
            table_list = scheduleDB.get_table_list()
            now_datetime = datetime.now().timestamp()

            for table in table_list:
                latest_data[table] = scheduleDB.get_database(table)

            # 테이블 체크
            for table in table_list:
                table_data = scheduleDB.get_database(table)

                if table_data is not None:
                    # 테이블 내부 데이터 시간 체크 후 알림 전송
                    for data in table_data:
                        # 이미 시간이 지났거나 지금이라면
                        if data[2] <= now_datetime:
                            LOGGER.info(f"Send msg : {data}")
                            await send_msg(bot, table, data)
                            status = scheduleDB.delete_db(table, data[0])
                            if status is True:
                                LOGGER.info(f"Data removal successful : {data}")
                            else:
                                LOGGER.info(f"Data removal failed, reset_db will delete it : {data}")

        except Exception:
            print(traceback.format_exc())
        await asyncio.sleep(30)

async def send_msg(bot, name, post):
    channel_id_list = channelDataDB.get_on_channel()
    _, _, unixtime, link, thumbnail, title, icon = post
    if channel_id_list != None:
        # 홀로 컬러데이터 가져오기
        with open(f"bot/data/holo.json") as f:
            data = f.read()
        holo_color = json.loads(data)
        try:
            role  = f"<@&{int(holo_color[name]['id'])}>"
        except:
            role = None

        # 아이콘 저장할 임시폴더 생성
        temp_folder = "temp"
        if not os.path.exists(temp_folder):
            os.mkdir(temp_folder)

        # 색상 추출
        try:
            urllib.request.urlretrieve(icon, f"{temp_folder}/{icon.split('/')[-1]}")
            dominant_color = ColorThief(f"{temp_folder}/{icon.split('/')[-1]}").get_color(quality=1)
            hex_color = hex(dominant_color[0]) + hex(dominant_color[1])[2:] + hex(dominant_color[2])[2:]
            color = int(hex_color, 16)
        except Exception:
            print(traceback.format_exc())
            color = color_code

        for channel_id in channel_id_list:
            target_channel = bot.get_channel(channel_id)
            try:
                if target_channel.guild.id == 866120502354116649 and role != None:
                    await target_channel.send(f"{role} {name} - {title}")
                embed=discord.Embed(title=title, description="", color=color)
                embed.add_field(name=i18n(channel_id, "broadcast", "버튜버"), value=name, inline=False)
                embed.add_field(name=i18n(channel_id, "broadcast", "방송 시간"), value=f"<t:{unixtime}>", inline=False)
                embed.add_field(name=i18n(channel_id, "broadcast", "링크"), value=link, inline=False)
                # 유튜버 프로필 설정
                embed.set_thumbnail(url=icon)
                # 썸네일 설정
                embed.set_image(url=thumbnail)
                embed.set_footer(text=BOT_NAME_TAG_VER)
                msg = await target_channel.send(embed=embed)
                if target_channel.type == discord.ChannelType.news:
                    await msg.publish()
            except Exception as e:
                print(f"Broadcast error : {e}")