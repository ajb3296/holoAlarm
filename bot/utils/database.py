"""

id, datetime, unixdatetime, url, thumbnail, title, iconImage

"""

import sqlite3

from bot import schedule_db_path, channel_db_path

class scheduleDB:
    def set_database(holo_list):
        # Create table if it doesn't exist
        # (name, (datetime, unixdatetime, url, thumbnail, title, talent.iconImageUrl))
        con = sqlite3.connect(schedule_db_path, isolation_level=None)
        cur = con.cursor()

        # add broadcast data
        for holo in holo_list:
            cur.execute(f"CREATE TABLE IF NOT EXISTS {holo[0]} (id integer PRIMARY KEY AUTOINCREMENT, datetime text, unixdatetime int, url text, thumbnail text, title text, iconImage text)")
            try:
                cur.execute(f"SELECT * FROM {holo[0]} WHERE datetime=:datetime", {"datetime": holo[1][0]})
                temp = cur.fetchone()
            except:
                temp = None
            if temp is None:
                # 없으면 추가
                cur.execute(f"INSERT INTO {holo[0]} (datetime, unixdatetime, url, thumbnail, title, iconImage) VALUES(?, ?, ?, ?, ?, ?)", (holo[1][0], int(holo[1][1]), holo[1][2], holo[1][3], holo[1][4], holo[1][5]))
            elif temp[5] != holo[1][4]:
                cur.execute(f"UPDATE {holo[0]} SET thumbnail=:thumbnail, url=:url, title=:title WHERE datetime=:datetime LIMIT 1", {"url": holo[1][2], "thumbnail": holo[1][3], "title": holo[1][4], 'datetime': holo[1][0]})
        con.close()

    def get_database(table_name):
        # 모든 데이터베이스 가져오기
        con = sqlite3.connect(schedule_db_path, isolation_level=None)
        cur = con.cursor()
        try:
            cur.execute(f"SELECT * FROM {table_name} ORDER BY id")
        except:
            con.close()
            return None
        temp = cur.fetchall()
        con.close()
        return temp

    def get_database_from_id(table_name, id):
        # id로 데이터베이스 가져오기
        con = sqlite3.connect(schedule_db_path, isolation_level=None)
        cur = con.cursor()
        try:
            cur.execute(f"SELECT * FROM {table_name} WHERE id=:Id", {"Id": id})
        except sqlite3.OperationalError:
            con.close()
            return None
        temp = cur.fetchone()
        con.close()
        return temp

    def get_table_list():
        # 테이블 리스트 가져오기
        con = sqlite3.connect(schedule_db_path)
        cur = con.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
        table_list = cur.fetchall()
        cur.close()
        tables = []
        for table in table_list:
            tables.append(table[0])
        return tables

    def delete_db(table_name, id):
        # 데이터 제거
        con = sqlite3.connect(schedule_db_path, isolation_level=None)
        cur = con.cursor()
        try:
            cur.execute(f"DELETE FROM {table_name} WHERE id = :ID",{"ID":id})
        except:
            cur.close()
            return False
        con.close()
        return True

    def get_latest_data(table_name):
        # 마지막 행 리턴
        all_db = scheduleDB.get_database(table_name)
        if all_db is None:
            return None
        else:
            return all_db[-1]

class VrozDB:
    def __init__(self):
        self.db_path = "vroz.db"
        self.table_name = "vroz"

    def set_database(self, vroz_list: list[tuple[str, str, int, str]]) -> None:
        con = sqlite3.connect(self.db_path, isolation_level=None)
        cur = con.cursor()

        # add vroz data
        for vroz in vroz_list:
            title, description, article_id, thumbnail = vroz
            cur.execute(f"CREATE TABLE IF NOT EXISTS {self.table_name} (id integer PRIMARY KEY AUTOINCREMENT, article_id integer, title text, description text, thumbnail text)")
            try:
                cur.execute(f"SELECT * FROM {self.table_name} WHERE article_id=:article_id", {"id": article_id})
                temp = cur.fetchone()
            except:
                temp = None
            if temp is None:
                # 없으면 추가
                cur.execute(f"INSERT INTO {self.table_name} (article_id, title, description, thumbnail) VALUES(?, ?, ?, ?)", (article_id, title, description, thumbnail))
        con.close()
    
    def get_database(self):
        # 모든 데이터베이스 가져오기
        con = sqlite3.connect(self.db_path, isolation_level=None)
        cur = con.cursor()
        try:
            cur.execute(f"SELECT * FROM {self.table_name} ORDER BY id")
        except:
            con.close()
            return None
        temp = cur.fetchall()
        con.close()
        return temp

class channelDataDB:
    def __init__(self):
        pass

    def channel_status_set(self, table: str, id: int, status: str, language: str):
        """ 채널 상태 설정 """
        # Create table if it doesn't exist
        con = sqlite3.connect(channel_db_path, isolation_level=None)
        cur = con.cursor()
        cur.execute(f"CREATE TABLE IF NOT EXISTS {table} (id integer PRIMARY KEY, onoff text, language text)")
        try:
            cur.execute(f"SELECT * FROM {table} WHERE id=:id", {"id": id})
            a = cur.fetchone()
        except:
            a = None
        if a is None:
            # add channel set
            cur.execute(f"INSERT INTO {table} VALUES('{id}', '{status}', '{language}')")
        else:
            # modify channel set
            cur.execute(f"UPDATE {table} SET onoff=:onoff, language=:language WHERE id=:id", {"onoff": status, "language": language, 'id': id})
        con.close()

    def get_on_channel(self, table: str):
        """ 모든 알람설정 되어있는 채널 가져오기 """
        con = sqlite3.connect(channel_db_path, isolation_level=None)
        cur = con.cursor()
        try:
            cur.execute(f"SELECT * FROM {table} ORDER BY id")
        except sqlite3.OperationalError:
            return None
        temp = cur.fetchall()
        con.close()

        on_channel = []
        for channel in temp:
            if channel[1] == "on":
                on_channel.append(channel[0])
        return on_channel

    def get_database_from_id(self, table: str, id: int):
        con = sqlite3.connect(channel_db_path, isolation_level=None)
        cur = con.cursor()
        try:
            cur.execute(f"SELECT * FROM {table} WHERE id=:Id", {"Id": id})
        except sqlite3.OperationalError:
            con.close()
            return None
        temp = cur.fetchone()
        con.close()
        return temp

if __name__ == "__main__":
    schedule_db_path = "holo.db"
    channel_db_path = "channel.db"
    post_list = [(80000, '제목1', '글쓴이1'), (80001, '제목2', '글쓴이2')]
    scheduleDB.set_database(post_list)