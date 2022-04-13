#
# (name, (datetime, unixdatetime, isLive, url, thumbnail, title, talent.iconImageUrl))
#

import asyncio
from datetime import datetime

from bot.utils.crawler import getJSON
from bot.utils.database import *
from bot import schedule_link

async def read_holo():
    while True:
        header = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Trident/7.0; rv:11.0) like Gecko'}
        result = await getJSON(schedule_link, header)
        datetime.today().strftime('%m%d')
        today_videos_list = result["dateGroupList"][0]["videoList"]
        # Table name : Vtuber name
        # info : datetime, unixdatetime, isLive, url, thumbnail, title, name, talent.iconImageUrl
        goto_DB = []
        for temp in today_videos_list:
            unixtime = int(datetime.strptime(temp['datetime'], '%Y/%m/%d %H:%M:%S').timestamp())
            now_unix_time = int(datetime.now().timestamp())
            # 과거일 경우 추가하지 않음
            if unixtime > now_unix_time:
                goto_DB.append((temp['name'], (temp['datetime'], unixtime, temp['url'], temp['thumbnail'], temp['title'], temp['talent']['iconImageUrl'])))

        scheduleDB.set_database(goto_DB)
        await asyncio.sleep(1800)

if __name__ == "__main__":
    import requests
    schedule_link = "https://schedule.hololive.tv/api/list"
    read_holo()