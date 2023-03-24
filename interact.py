import threading
from threading import Lock
import inference_main 
import re
from meowChat_util.third_part import *

mutex = Lock()
#
# generate voice from wav file
#
def generate_song(parser, wav_path):
    mutex.acquire()
    generator = stream_voice_generator()
    inference_main.generate(parser=parser, clean_names=[wav_path], output_path="results", stream=True,
                            generator=generator)
    mutex.release()


#
# generate voice from info
#
def generate_voice(parser, info, language='en', stream=False):
    mutex.acquire()
    tts_output_path = "tts_output"
    get_tts(info, language, tts_output_path)
    parser.auto_predict_f0=True
    if not stream:
        audiopath = inference_main.generate(parser=parser, clean_names=[tts_output_path], output_path="results",stream=False)
        playsound(audiopath)
    else:
        generator = stream_voice_generator()
        inference_main.generate(parser=parser, clean_names=[tts_output_path], output_path="results", stream=True,
                                generator=generator)
    mutex.release()

def generate_voice_by_chat(parser, info, language='en', stream=False):
    reply = get_chatgpt_reply(info, language)
    #reply=info+"this is my fake reply!but enough long for you to generate some answer and say something great for me!Please say it loudly!"
    print("\nEvilia> "+reply+"\nuser> ",end="")
    generate_voice(parser, reply, language,stream)
    get_instructions(reply)

#
# stream generator
#
def stream_voice_generator():
    r = ''
    not_used = yield r
    while (True):
        audiopath = yield r
        if (not audiopath):
            return
        # playsound(audiopath)
        p = threading.Thread(target=playsound, args=(audiopath,))
        p.start()
        not_used = yield r
        p.join()


#
# get instructions within ai output
#
def get_instructions(info):
    instruction = re.search('-draw', info)
    if (instruction):
        prompt = get_prompt(info, instruction.span()[1])
        instruction_draw(prompt)

    instruction = re.search('-sing', info)
    if (instruction):
        prompt = get_prompt(info, instruction.span()[1])
        instruction_draw(prompt)


def get_prompt(info, index):
    prompt = ''
    while (index < len(info) and not info[index] in split_symbol):
        prompt = prompt + info[index]
        index += 1
    return prompt


#
# gpt instruction to draw
#
def instruction_draw(prompt):
    pass
    # rst = wenxin.get_painting(prompt=prompt)
    # print(rst)
    # for url in rst['imgUrls']:
    #     print(url)


#
# gpt instruction to sing
#
def instruction_sing(prompt):
    pass
