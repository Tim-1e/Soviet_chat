import random
import sys
import os
import re
import queue
from time import sleep
import threading
from threading import Lock
import keyboard

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
sys.path.append("meowChat_util")
import third_part
import render
import voice_to_text as vtt
import database as DB
import interact

message_queue = queue.Queue()
stop_event=None
message_handler_thread=None
parser = None
is_recording=False
micro_record=vtt.Recorder()
evilia_db=DB.Database("evilia_private_db.db")

class chat_message:
    def __init__(self, info):
        self.content=""
        self.type=""
        self.from_string(info)

    
    def from_string(self,info):
        """
        parse the message from string
        """
        if (info[0:5] == '-sing'):
            self.content=info[6:]
            self.type="sing"
        elif (info[0:5] == '-echo'):
            self.content=info[6:]
            self.type="echo"
        else:
            self.content=info
            self.type="chat"
    
    def create_thread(self):
        '''
        convert message to thread
        '''
        thread=None
        if self.type=="sing":
            thread=threading.Thread(target=interact.generate_song, args=(parser, self.content))
        elif self.type=="echo":
            thread=threading.Thread(target=interact.generate_voice, args=(parser, self.content,'en',True))
        else:
            thread=threading.Thread(target=interact.generate_voice_by_chat, args=(parser, self.content,'en',True))
        return  thread


def message_handler(stop_event):
    task_list=[]
    # 初始化计时器和上一次用户回复的时间戳
    while not stop_event.is_set():
        try:
            message = message_queue.get()
            task = message.create_thread()
            task_list.append(task)
        except queue.Empty:
            info=random.choice(third_part.default_greets)
            meassage=chat_message(info)
            task = meassage.create_thread()
            task_list.append(task)
            task.start()
            continue
        task.start()
        message_queue.task_done()

    for task in task_list:
        task.join()

def get_arguments():
    '''
    get global arguments
    '''
    import argparse
    parser = argparse.ArgumentParser(description='sovits4 inference')

    # 一定要设置的部分
    parser.add_argument('-m', '--model_path', type=str, default="logs/onimal/mahiro/G_52000.pth", help='模型路径')
    parser.add_argument('-c', '--config_path', type=str, default="configs/config.json", help='配置文件路径')
    parser.add_argument('-t', '--trans', type=int, nargs='+', default=[5], help='音高调整，支持正负（半音）')
    parser.add_argument('-s', '--spk_list', type=str, nargs='+', default=[''], help='合成目标说话人名称')
    # 可选项部分
    parser.add_argument('-a', '--auto_predict_f0', action='store_true', default=False,
                        help='语音转换自动预测音高，转换歌声时不要打开这个会严重跑调')
    parser.add_argument('-cm', '--cluster_model_path', type=str, default="logs/44k/kmeans_10000.pt",
                        help='聚类模型路径，如果没有训练聚类则随便填')
    parser.add_argument('-cr', '--cluster_infer_ratio', type=float, default=0,
                        help='聚类方案占比，范围0-1，若没有训练聚类模型则填0即可')

    # 不用动的部分
    parser.add_argument('-sd', '--slice_db', type=int, default=-40,
                        help='默认-40，嘈杂的音频可以-30，干声保留呼吸可以-50')
    parser.add_argument('-d', '--device', type=str, default=None, help='推理设备，None则为自动选择cpu和gpu')
    parser.add_argument('-ns', '--noice_scale', type=float, default=0.4, help='噪音级别，会影响咬字和音质，较为玄学')
    parser.add_argument('-p', '--pad_seconds', type=float, default=0.5,
                        help='推理音频pad秒数，由于未知原因开头结尾会有异响，pad一小段静音段后就不会出现')
    parser.add_argument('-wf', '--wav_format', type=str, default='wav', help='音频输出格式')

    return parser

def init_handler():
    global stop_event, message_handler_thread
    stop_event = threading.Event()
    message_handler_thread = threading.Thread(target=message_handler, args=(stop_event,))
    message_handler_thread.start()
    

def keyborad_input():
    '''
    get keyborad input and set exception
    '''
    keyboard.add_hotkey("ctrl+e", voice_input)
    try:
        while True:
            sys.stdout.write("user> ")
            sys.stdout.flush()
            user_input = input().strip()
            if user_input.lower() == "exit":
                break
            message_queue.put(chat_message(user_input))
    except KeyboardInterrupt:
        print("\nExiting due to KeyboardInterrupt...")
    
    stop_event.set()
    message_handler_thread.join()

def voice_input():
    '''
    press ctrl+e to get input and press ctrl+e again to stop
    '''
    global is_recording
    is_recording = not is_recording
    if is_recording:
        print("开始录音")
        micro_record.start()
    else:
        print("录音结束")
        micro_record.stop()
        message_queue.put(chat_message(micro_record.result))
        print("user> "+micro_record.result)

def main():
    global parser
    parser=get_arguments()
    third_part.init_openai()
    init_handler()
    keyborad_input()
    
# Note: you need to be using OpenAI Python v0.27.0 for the code below to work
if __name__ == '__main__':
    main()
