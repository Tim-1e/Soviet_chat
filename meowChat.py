import sys
import os
import io
import queue
from time import sleep
import _thread
import threading
from threading import Lock

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
from meowChat_util.third_part import *
from meowChat_util.render import *
from interact import *


def worker(task_queue, stop_event):
    while not stop_event.is_set():
        try:
            task = task_queue.get(timeout=1)
        except queue.Empty:
            continue
        print("A thread begin")
        task.start()
        task.join()
        task_queue.task_done()


#
# get global arguments
#
def get_arguments():
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

#
# get user input. ignore empty input
#
def user_input(parser):
    task_queue = queue.Queue()
    stop_event = threading.Event()
    worker_thread = threading.Thread(target=worker, args=(task_queue, stop_event))
    worker_thread.start()
    try:
        while True:
            sys.stdout.write("user> ")
            sys.stdout.flush()
            user_input = input().strip()

            if user_input.lower() == "exit":
                break

            main_chat(parser,user_input,task_queue)
    except KeyboardInterrupt:
        print("\nExiting due to KeyboardInterrupt...")
    stop_event.set()
    worker_thread.join()

#
# Your main chat loop is here
#
def main_chat(parser,info,task_queue):
    global REPLY_LANGUAGE
    language = REPLY_LANGUAGE
    if (info[0:5] == '-sing'):
        wavefile = str.strip(info[5:])
        sing=threading.Thread(target=generate_song, args=(parser, wavefile))
        task_queue.put(sing)
    elif (info[0:5] == '-echo'):
        reply = str.strip(info[5:])
        echo=threading.Thread(target=generate_voice, args=(parser, reply, language, True))
        task_queue.put(echo)
    elif (info[0:5] == '-exit'):
        bye=threading.Thread(target=generate_voice, args=(parser, 'good bye!', language, True))
        task_queue.put(bye)
        sys.exit(0)
    else:
        chat=threading.Thread(target=generate_voice_by_chat, args=(parser, info, language, True))
        task_queue.put(chat)



def main():
    parser = get_arguments()
    init_openai()
    user_input(parser)

# Note: you need to be using OpenAI Python v0.27.0 for the code below to work
if __name__ == '__main__':
    main()
