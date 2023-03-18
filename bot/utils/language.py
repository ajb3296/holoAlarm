import os
import json
import sqlite3

from bot.utils.database import channelDataDB

def i18n(id, table, text):
    default_language = "ko"
    userdata_db_path = "userdata.db"

    if table == "broadcast":
        data = channelDataDB().get_database_from_id("broadcastChannel", id)
        language = data[2]

        with open(f"bot/language/{language}.json") as f:
            language_data = json.load(f)
        return language_data[table][text]

    # if the userdata file exists
    if os.path.exists(userdata_db_path):
        conn = sqlite3.connect(userdata_db_path, isolation_level=None)
        c = conn.cursor()
        c.execute("SELECT * FROM userdata WHERE id=:Id", {"Id": id})
        temp = c.fetchone()
        if temp is None:
            language = default_language
        else:
            language = temp[1]
            if not os.path.exists(f"bot/language/{language}.json"):
                language = default_language
        conn.close()
        # read language file
        with open(f"bot/language/{language}.json") as f:
            language_data = json.load(f)
        return language_data[table][text]

    else:
        with open(f"bot/language/{default_language}.json") as f:
            language_data = json.load(f)
        return language_data[table][text]