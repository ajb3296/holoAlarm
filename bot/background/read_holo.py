#
# (name, (datetime, unixdatetime, isLive, url, thumbnail, title, talent.iconImageUrl))
#

import re
import json
import asyncio
from datetime import datetime
from turtle import goto

from bot.utils.crawler import getText
from bot.utils.database import *
from bot import schedule_link, LOGGER

def read_holo():
    while True:
        header = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Trident/7.0; rv:11.0) like Gecko'}
        #result = await getJSON(schedule_link, header)
        result = requests.get(schedule_link)
        json_data = json.loads(result.text)
        datetime.today().strftime('%m%d')
        today_videos_list = json_data["dateGroupList"][0]["videoList"]
        print(today_videos_list)
        # Table name : Vtuber name
        # info : datetime, unixdatetime, isLive, url, thumbnail, title, name, talent.iconImageUrl
        goto_DB = []
        for temp in today_videos_list:
            unixtime = int(datetime.strptime(temp['datetime'], '%Y/%m/%d %H:%M:%S').timestamp())
            now_unix_time = int(datetime.now().timestamp())
            # 과거일 경우 추가하지 않음
            if unixtime > now_unix_time:
                goto_DB.append((temp['name'], (temp['datetime'], unixtime, temp['isLive'], temp['url'], temp['thumbnail'], temp['talent']['iconImageUrl'])))
            else:
                # 데이터베이스에서 제거
                status = scheduleDB.delete_db(temp['name'], temp[0])

        break

        #scheduleDB.set_database(goto_DB)
        #await asyncio.sleep(1800)

if __name__ == "__main__":
    import requests
    schedule_link = "https://schedule.hololive.tv/api/list"
    read_holo()