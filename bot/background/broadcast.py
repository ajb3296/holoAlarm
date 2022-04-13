import json
import discord
import asyncio

from bot.utils.database import *
from bot import LOGGER, BOT_NAME_TAG_VER, se_board_link

async def broadcast(bot):
    await asyncio.sleep(5)
    latest_data_id = scheduleDB.get_latest_data_id()
    while True:
        now_latest_data = scheduleDB.get_latest_data()
        if latest_data_id != now_latest_data:
            # get post
            post = scheduleDB.get_database_from_id(now_latest_data[0])
            if post is not None:
                LOGGER.info(f"Send msg : {post}")
                await send_msg(bot, post)

            latest_data_id = now_latest_data
        await asyncio.sleep(30)

async def send_msg(bot, post):
    channel_id_list = channelDataDB.get_on_channel()
    if channel_id_list != None:
        # Get holo color data
        with open(f"bot/data/holo.json") as f:
            holo_color = json.load(f)
        for channel_id in channel_id_list:
            target_channel = bot.get_channel(channel_id)
            try:
                embed=discord.Embed(title=post[2], description=f"", color=color)
                embed.add_field(name="글쓴이", value=post[3], inline=True)
                embed.add_field(name="중요도", value=important, inline=True)
                embed.add_field(name="링크", value=f"{se_board_link}freeboard/{post[1]}", inline=False)
                embed.set_footer(text=BOT_NAME_TAG_VER)
                await target_channel.send(embed=embed)
            except:
                pass