import json
import websocket
import threading

# 定义当接收到消息时的处理函数
def on_message(ws, message):
    print("Received message: {}".format(message))

# 定义当WebSocket连接成功时的处理函数
def on_open(ws):
    message = {
        "msg": 13100,
        "msgId": 1,
        "data": 1
    }
    ws.send(json.dumps(message))

# 创建一个WebSocket连接
ws = websocket.WebSocketApp(
    "ws://127.0.0.1:10086/api",
    on_message=on_message,
    on_open=on_open
)

# 启动一个新线程运行WebSocket客户端
thread = threading.Thread(target=ws.run_forever)
thread.start()
thread.join()
