"""

id, datetime, unixdatetime, url, thumbnail, title, iconImage

"""

import sqlite3

from bot import SCHEDULE_DB_PATH, CHANNEL_DB_PATH

class scheduleDB:
    def __init__(self):
        self.db_path = SCHEDULE_DB_PATH

    def set_database(self, holo_list: list[tuple[str, tuple[str, int, str, str, str, str]]]) -> None:
        """ 홀로라이브 스케줄 데이터베이스에 추가 """
        # Create table if it doesn't exist
        # (name, (datetime, unixdatetime, url, thumbnail, title, talent.iconImageUrl))
        con = sqlite3.connect(self.db_path, isolation_level=None)
        cur = con.cursor()

        # add broadcast data
        for holo in holo_list:
            name, holotemp = holo
            datetime_text, unixdatetime, url, thumbnail, title, icon_url = holotemp

            cur.execute(f"CREATE TABLE IF NOT EXISTS {name} (id integer PRIMARY KEY AUTOINCREMENT, datetime text, unixdatetime int, url text, thumbnail text, title text, iconImage text)")
            try:
                cur.execute(f"SELECT * FROM {name} WHERE datetime=:datetime", {"datetime": datetime_text})
                temp = cur.fetchone()
            except:
                temp = None
            if temp is None:
                # 없으면 추가
                cur.execute(f"INSERT INTO {name} (datetime, unixdatetime, url, thumbnail, title, iconImage) VALUES(?, ?, ?, ?, ?, ?)", (datetime_text, int(unixdatetime), url, thumbnail, title, icon_url))
            elif temp[5] != title:
                cur.execute(f"UPDATE {name} SET thumbnail=:thumbnail, url=:url, title=:title WHERE datetime=:datetime", {"url": url, "thumbnail": thumbnail, "title": title, 'datetime': datetime_text})
        con.close()

    def get_database(self, table_name: str) -> list[tuple] | None:
        """ 테이블의 모든 데이터 가져오기 """
        con = sqlite3.connect(self.db_path, isolation_level=None)
        cur = con.cursor()
        try:
            cur.execute(f"SELECT * FROM {table_name} ORDER BY id")
        except:
            con.close()
            return None
        temp = cur.fetchall()
        con.close()
        return temp

    def get_database_from_id(self, table_name: str, id: int) -> tuple | None:
        """ id로 데이터 가져오기 """
        con = sqlite3.connect(self.db_path, isolation_level=None)
        cur = con.cursor()
        try:
            cur.execute(f"SELECT * FROM {table_name} WHERE id=:Id", {"Id": id})
        except sqlite3.OperationalError:
            con.close()
            return None
        temp = cur.fetchone()
        con.close()
        return temp

    def get_table_list(self) -> list:
        """ 테이블 리스트 가져오기 """
        con = sqlite3.connect(self.db_path)
        cur = con.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
        table_list = cur.fetchall()
        cur.close()
        tables = []
        for table in table_list:
            tables.append(table[0])
        return tables

    def delete_db(self, table_name: str, id: int):
        """ id 값으로 데이터 제거 """
        con = sqlite3.connect(self.db_path, isolation_level=None)
        cur = con.cursor()
        try:
            cur.execute(f"DELETE FROM {table_name} WHERE id = :ID",{"ID":id})
        except:
            cur.close()
            return False
        con.close()
        return True

    def get_latest_data(self, table_name: str) -> list | None:
        """ 마지막 행 리턴 """
        all_db = scheduleDB().get_database(table_name)
        if all_db is None:
            return None
        else:
            return all_db[-1]

class VrozDB:
    def __init__(self):
        self.db_path = "vroz.db"
        self.table_name = "vroz"

    def set_database(self, vroz_list: list[tuple[str, str, int, str]]) -> None:
        """ vroz 데이터베이스에 추가 """
        con = sqlite3.connect(self.db_path, isolation_level=None)
        cur = con.cursor()

        # add vroz data
        for vroz in vroz_list:
            title, description, article_id, thumbnail = vroz
            cur.execute(f"CREATE TABLE IF NOT EXISTS {self.table_name} (id integer PRIMARY KEY AUTOINCREMENT, article_id integer, title text, description text, thumbnail text)")
            try:
                cur.execute(f"SELECT * FROM {self.table_name} WHERE article_id=:article_id", {"article_id": article_id})
                temp = cur.fetchone()
            except:
                temp = None
            if temp is None:
                # 없으면 추가
                cur.execute(f"INSERT INTO {self.table_name} (article_id, title, description, thumbnail) VALUES(?, ?, ?, ?)", (article_id, title, description, thumbnail))
        con.close()
    
    def get_database(self) -> list[tuple[int, int, str, str, str]] | None:
        """ 모든 데이터베이스 가져오기 """
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
        self.db_path = CHANNEL_DB_PATH

    def channel_status_set(self, table: str, id: int, status: str, language: str):
        """ 채널 상태 설정 """
        # Create table if it doesn't exist
        con = sqlite3.connect(self.db_path, isolation_level=None)
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
        con = sqlite3.connect(self.db_path, isolation_level=None)
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
        """ id로 데이터 가져오기 """
        con = sqlite3.connect(self.db_path, isolation_level=None)
        cur = con.cursor()
        try:
            cur.execute(f"SELECT * FROM {table} WHERE id=:Id", {"Id": id})
        except sqlite3.OperationalError:
            con.close()
            return None
        temp = cur.fetchone()
        con.close()
        return temp

class Muted():
    """
        데이터베이스 구조
        data:
            guild_id: int
            user_id: int
            delete_check: bool
        guild:
            guild_id: int
            channel_id: int
            role_id: int
    """
    def __init__(self):
        self.db_path = "muted.db"

        con = None
        cur = None
    
    def open(self):
        """ DB 연결 """
        self.con = sqlite3.connect(self.db_path, isolation_level=None)
        self.cur = self.con.cursor()
    
    def close(self):
        """ DB 연결 해제 """
        self.con.close()
    
    def enroll_guild(self, guild_id: int, channel_id: int, role_id: int):
        """ 서버 알림 등록 """
        try:
            self.cur.execute(f"SELECT * FROM guild WHERE guild_id=:guild_id", {"guild_id": guild_id})
            temp = self.cur.fetchone()
        except:
            temp = None
        if temp is None:
            # 없으면 추가
            self.cur.execute(f"INSERT INTO guild (guild_id, channel_id, role_id) VALUES(?, ?, ?)", (guild_id, channel_id, role_id))
        else:
            self.cur.execute(f"UPDATE guild SET channel_id=:channel_id, role_id=:role_id WHERE guild_id=:guild_id", {"channel_id": channel_id, "role_id": role_id, "guild_id": guild_id})
    
    def delete_guild(self, guild_id: int):
        """ 서버 알림 삭제 """
        try:
            self.cur.execute(f"DELETE FROM guild WHERE guild_id=:guild_id", {"guild_id": guild_id})
            self.cur.execute(f"DELETE FROM data WHERE guild_id=:guild_id", {"guild_id": guild_id})
        except:
            return False
        return True

    def get_all_guild_id(self) -> list[tuple[int, int, int]]:
        """ 알림이 켜진 서버 목록 가져오기 """
        try:
            self.cur.execute(f"SELECT * FROM guild ORDER BY guild_id")
        except:
            self.con.close()
            return None
        temp = self.cur.fetchall()
        return temp

    def get_alarm_channel(self, guild_id: int) -> int | None:
        """ 알림 채널 가져오기 """
        try:
            self.cur.execute(f"SELECT * FROM guild WHERE guild_id=:guild_id", {"guild_id": guild_id})
            temp = self.cur.fetchone()
        except:
            temp = None
        if temp is None:
            return None
        else:
            return temp[1]

    def get_all_db(self, guild_id: int) -> list[tuple[int, int, bool]]:
        """ 모든 데이터베이스 가져오기 """
        try:
            self.cur.execute(f"SELECT * FROM data WHERE guild_id=:guild_id ORDER BY user_id", {"guild_id": guild_id})
        except:
            self.con.close()
            return None
        temp = self.cur.fetchall()
        return temp

    def update_user_status(self, guild_id: int, user_id: int, delete: bool):
        """ 유저 추가 혹은 업데이트 """
        try:
            self.cur.execute(f"SELECT * FROM data WHERE guild_id=:guild_id AND user_id=:user_id", {"guild_id": guild_id, "user_id": user_id})
            temp = self.cur.fetchone()
        except:
            temp = None
        if temp is None:
            # 없으면 추가
            self.cur.execute(f"INSERT INTO data (guild_id, user_id, delete_check) VALUES(?, ?, ?)", (guild_id, user_id, delete))
        else:
            # 다음에 삭제할지 말지 업데이트
            self.cur.execute(f"UPDATE data SET delete_check=:delete_check WHERE guild_id=:guild_id AND user_id=:user_id", {"delete_check": delete, "guild_id": guild_id, "user_id": user_id})
    
    def delete_user(self, guild_id: int, user_id: int):
        """ 유저 삭제 """
        try:
            self.cur.execute(f"DELETE FROM data WHERE guild_id=:guild_id AND user_id=:user_id", {"guild_id": guild_id, "user_id": user_id})
        except:
            return False
        return True

    def check_user(self, guild_id: int, user_id: int) -> bool:
        """ 유저가 존재하는지 확인, 존재하면 True, 존재하지 않으면 False """
        try:
            self.cur.execute(f"SELECT * FROM data WHERE guild_id=:guild_id AND user_id=:user_id", {"guild_id": guild_id, "user_id": user_id})
            temp = self.cur.fetchone()
        except:
            temp = None
        if temp is None:
            return False
        else:
            return True

    def set_database(self, muted_list: dict[int, list[int]]):
        for guild_id in muted_list.keys(): # 들어온 값에서 서버 하나씩 확인
            db = self.get_all_db(guild_id) # 데이터베이스에서 서버의 뮤트된 유저 목록 가져오기
            if db != []: # 데이터베이스에 유저가 있으면
                for db_user in db: # 데이터베이스 유저를 하나씩 확인
                    user_id = db_user[1]
                    delete = db_user[2]

                    if user_id not in muted_list[guild_id]: # 만약 데이터베이스엔 존재하지만 들어온 값에는 없으면
                        # 이전 사이클에 제거된 유저가 있으면 이번 사이클에 제거
                        if delete:
                            self.delete_user(guild_id, user_id)
                        else:
                            self.update_user_status(guild_id, user_id, True)
                    
                    else: # 데이터베이스에도 존재하고 들어온 값에도 존재하면
                        if delete:
                            self.update_user_status(guild_id, user_id, False)
                    try:
                        muted_list[guild_id].remove(user_id)
                    except ValueError:
                        pass
            
            # 데이터베이스에 없는 유저 추가
            for user_id in muted_list[guild_id]:
                self.update_user_status(guild_id, user_id, False)