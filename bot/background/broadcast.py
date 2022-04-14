import json
import discord
import asyncio
from datetime import datetime

from bot.utils.database import *
from bot import LOGGER, BOT_NAME_TAG_VER, color_code

async def broadcast(bot):
    latest_data = {}
    await asyncio.sleep(5)

    while True:
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

        await asyncio.sleep(30)

async def send_msg(bot, name, post):
    channel_id_list = channelDataDB.get_on_channel()
    if channel_id_list != None:
        # 홀로 컬러데이터 가져오기
        with open(f"bot/data/holo.json") as f:
            data = f.read()
        holo_color = json.loads(data)
        try:
            holo_color = holo_color[name]
        except:
            holo_color = None

        try:
            color = int(str(holo_color['color']).replace("#", ""), 16)
        except:
            color = color_code
        try:
            role  = f"<@${int(holo_color['id'])}>"
        except:
            role = None

        for channel_id in channel_id_list:
            target_channel = bot.get_channel(channel_id)
            try:
                embed=discord.Embed(title=post[5], description=f"", color=color)
                embed.add_field(name="링크", value=post[3], inline=False)
                embed.add_field(name="버튜버", value=name, inline=False)
                embed.add_field(name="방송시간", value=f"<t:{post[2]}>", inline=False)
                if target_channel.guild.id == 866120502354116649:
                    embed.add_field(name="알림", value=role, inline=False)
                # 유튜버 프로필 설정
                embed.set_thumbnail(url=post[6])
                # 썸네일 설정
                embed.set_image(url=post[4])
                embed.set_footer(text=BOT_NAME_TAG_VER)
                await target_channel.send(embed=embed)
            except:
                pass