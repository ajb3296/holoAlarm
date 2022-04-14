import asyncio
from datetime import datetime

from bot import LOGGER
from bot.utils.database import *

async def reset_db():
    await asyncio.sleep(120)
    while True:
        table_list = scheduleDB.get_table_list()
        # 알림 전송 오류를 해결하기 위한 1시간 지난 데이터 제거
        now_unix_time = int(datetime.now().timestamp())
        # 테이블 리스트
        for table in table_list:
            db_data = scheduleDB.get_database(table)
            if db_data is not None:
                for data in db_data:
                    # 테이블 데이터 체크
                    if int(data[2]) + 3600 < now_unix_time:
                        print(data[2])
                        # 과거의 알림일 경우 제거 시도
                        for a in range(3):
                            try:
                                LOGGER.info(f"Try delete {a}th : {table} - {data}")
                                status = scheduleDB.delete_db(table, data[0])
                                LOGGER.info(f"Deleted : {table} - {data}")
                                if status is True:
                                    break
                            except:
                                pass
        await asyncio.sleep(120)