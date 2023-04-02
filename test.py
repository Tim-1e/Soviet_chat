import sqlite3
import keyboard

conn = sqlite3.connect('evilia_private_db.db')
c = conn.cursor()
is_loop=True
def Exit():
    global is_loop
    is_loop=False
keyboard.add_hotkey('esc',Exit)

# 循环读取用户输入的SQLite语句，并执行
while is_loop:
    # 读取用户输入
    query = input("请输入SQLite语句：")

    # 按下Esc键退出循环
    if keyboard.is_pressed('q'):
        break

    # 执行SQLite语句
    try:
        c.execute(query)
        print(c.fetchall())
    except Exception as e:  
        print(e)

# 提交更改并关闭连接
conn.commit()
conn.close()
