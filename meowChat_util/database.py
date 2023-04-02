import sqlite3
import keyboard
import json
class Database:
    def __init__(self, database_name):
        self.conn = sqlite3.connect(database_name)
        self.c = self.conn.cursor()

    def use_the_database(self, query):
        # 执行SQLite语句
        print("SQlite you use is: "+query)
        try:
            self.c.execute(query)
            result=self.c.fetchall()
            self.conn.commit()
            return(json.dumps(result))
        except Exception as e:
            return str(e)

    # 提交更改并关闭连接
    def close(self):
        self.conn.commit()
        self.conn.close()
