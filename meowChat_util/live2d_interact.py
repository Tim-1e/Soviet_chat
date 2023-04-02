import websocket
import asyncio
import json

def send(info , port = '10086'):
    ws = websocket.WebSocket()
    ws.connect("ws://127.0.0.1:" + port + "/api") 
    ws.send(info)   
    # 关闭 WebSocket 连接
    ws.close()

def set_text(text,duration = 10000):
    info = {
    "msg": 11000,
    "msgId": 1,
    "data": {
        "id": 0,
        "text": text,
        "textFrameColor": 0x000000,
        "textColor": 0xFFFFFF,
        "duration": duration
    }
    }
    send(info=str(info))
    
def set_expression(exp_id):
    info = {
    "msg": 13300,
    "msgId": 1,
    "data": {
        "id": 1,
        "expId": exp_id
        }
    }
    send(info = str(info)) 
       
def set_next_expression():
    info = {
    "msg": 13301,
    "msgId": 1,
    "data": 0
    }
    send(info = str(info))

def on_message(ws, message):
    # 在这里处理收到的消息
    print(message)
    print("ok get message")

def on_open(ws):
    # 在这里注册监听事件
    info = {
    "msg": 10000,
    "msgId": 1
    }
    ws.send(json.dumps(info))

def test():
    #注册监听事件
    ws = websocket.WebSocketApp("ws://127.0.0.1:10086/api", on_message=on_message)
    ws.run_forever()

    
if(__name__=='__main__'):
    test()
    