import discord
import asyncio
import traceback

from bot.utils.database import *
from bot import LOGGER, BOT_NAME_TAG_VER, color_code

async def broadcast_vroz(bot):
    latest_data = ""
    await asyncio.sleep(5)

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
    channel_id_list = channelDataDB().get_on_channel("VROZ")
    if channel_id_list != None:
        for channel_id in channel_id_list:
            target_channel = bot.get_channel(channel_id)
            try:
                embed=discord.Embed(title=title, description=description, color=color_code)
                embed.add_field(name="링크", value=f"https://vroz.cc/v/{article_id}", inline=False)
                # 썸네일 설정
                embed.set_image(url=thumbnail)
                embed.set_footer(text=BOT_NAME_TAG_VER)
                msg = await target_channel.send(embed=embed)
                if target_channel.type == discord.ChannelType.news:
                    await msg.publish()
            except Exception as e:
                print(f"Broadcast error : {e}")