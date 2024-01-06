#
# (name, (datetime, unixdatetime, isLive, url, thumbnail, title, talent.iconImageUrl))
#

import asyncio
import traceback
import feedparser

from bot.utils.database import VrozDB
from bot import LOGGER, VROZ_LINK

async def read_vroz():
    LOGGER.info("Read_vroz start")
    while True:
        try:
            vroz_all = feedparser.parse(VROZ_LINK)
            goto_DB = []
            for temp in vroz_all.entries:
                title = temp.title
                description = temp.description
                article_id = int(temp.link.split("/")[-1])
                thumbnail = temp.media_content[0]["url"]

                if thumbnail[0:4] != "http":
                    thumbnail = "https://vroznews.com" + thumbnail

                goto_DB.append((title.replace("'", "''"),
                                description.replace("'", "''"),
                                article_id,
                                thumbnail))

            VrozDB().set_database(goto_DB)

        except Exception:
            print(traceback.format_exc())
        await asyncio.sleep(60)