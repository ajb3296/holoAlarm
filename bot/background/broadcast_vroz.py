import os
import discord
import asyncio
import traceback
import urllib.request
from colorthief import ColorThief

from bot.utils.database import *
from bot import LOGGER, BOT_NAME_TAG_VER, COLOR_CODE

async def broadcast_vroz(bot):
    LOGGER.info("Broadcast_vroz start")
    await asyncio.sleep(5)
    table_list = VrozDB().get_database()
    latest_data = table_list[-1][1]

    while True:
        try:
            # 테이블 리스트 가져오기
            table_list = VrozDB().get_database()

            data_add = False
            for data in table_list:
                _, article_id, title, description, thumbnail = data
                if (data_add != True) and (article_id == latest_data):
                    data_add = True
                else:
                    if data_add:
                        await send_msg(bot, article_id, title, description, thumbnail)
                        # 최신 데이터 아이디 갱신
                        latest_data = article_id

        except Exception:
            print(traceback.format_exc())
        await asyncio.sleep(30)

async def send_msg(bot, article_id, title, description, thumbnail):
    LOGGER.info(f"Send msg : {title}")
    # 채널 리스트 가져오기
    channel_id_list = channelDataDB().get_on_channel("VROZ")

    # 썸네일 저장할 임시폴더 생성
    temp_folder = "temp_vroz"
    if not os.path.exists(temp_folder):
        os.mkdir(temp_folder)

    # 색상 추출
    try:
        urllib.request.urlretrieve(thumbnail, f"{temp_folder}/temp.jpg")
        dominant_color = ColorThief(f"{temp_folder}/temp.jpg").get_color(quality=1)
        hex_color = hex(dominant_color[0]) + hex(dominant_color[1])[2:] + hex(dominant_color[2])[2:]
        color = int(hex_color, 16)
    except Exception:
        print(traceback.format_exc())
        color = COLOR_CODE

    if channel_id_list != None:

        # 채널 아이디 별로 메시지 보냄
        for channel_id in channel_id_list:
            target_channel = bot.get_channel(channel_id)
            try:
                embed=discord.Embed(title=title, description=description, color=color)
                embed.add_field(name="링크", value=f"https://vroznews.com/v/{article_id}", inline=False)
                # 썸네일 설정
                embed.set_image(url=thumbnail)
                embed.set_footer(text=BOT_NAME_TAG_VER)
                msg = await target_channel.send(embed=embed)
                if target_channel.type == discord.ChannelType.news:
                    await msg.publish()
            except Exception as e:
                print(f"Broadcast error : {e}")