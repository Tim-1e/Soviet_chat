import io
import logging
import os
import time
import warnings

from pathlib import Path

import librosa
import matplotlib.pyplot as plt
import numpy as np
import soundfile

from inference import infer_tool
from inference import slicer
from inference.infer_tool import Svc

logging.getLogger('').setLevel(logging.WARNING)
warnings.filterwarnings("ignore", category=UserWarning)
chunks_dict = infer_tool.read_temp("chunks_temp.json")


def main():
    import argparse

    parser = argparse.ArgumentParser(description='sovits4 inference')

    # 一定要设置的部分
    parser.add_argument('-m', '--model_path', type=str, default="logs/44k/G_12800.pth", help='模型路径')
    parser.add_argument('-c', '--config_path', type=str, default="configs/config.json", help='配置文件路径')
    parser.add_argument('-n', '--clean_names', type=str, nargs='+', default=["test"],
                        help='wav文件名列表，放在raw文件夹下')
    parser.add_argument('-t', '--trans', type=int, nargs='+', default=[0], help='音高调整，支持正负（半音）')
    parser.add_argument('-s', '--spk_list', type=str, nargs='+', default=['Dorothy'], help='合成目标说话人名称')
    parser.add_argument('-o', '--output_path', type=str, default="results")
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
    parser.add_argument('-wf', '--wav_format', type=str, default='flac', help='音频输出格式')

    args = parser.parse_args()
    generate(parser, args.clean_names, "results")


def generate(parser, clean_names, output_path, stream=False, generator=None):
    if (stream):
        generator.send(None)
    import argparse
    args = parser.parse_args()

    configsBind = os.path.dirname(args.model_path) + "/config.json"
    svc_model = Svc(args.model_path, configsBind, args.device, args.cluster_model_path)
    infer_tool.mkdir(["raw", "results"])
    trans = args.trans
    spk_list = svc_model.spk2id
    spk_list = list(spk_list.keys())
    slice_db = args.slice_db
    wav_format = args.wav_format
    auto_predict_f0 = args.auto_predict_f0
    cluster_infer_ratio = args.cluster_infer_ratio
    noice_scale = args.noice_scale
    pad_seconds = args.pad_seconds

    infer_tool.fill_a_to_b(trans, clean_names)
    for clean_name, tran in zip(clean_names, trans):
        raw_audio_path = f"raw/{clean_name}"
        if "." not in raw_audio_path:
            raw_audio_path += ".mp3"
        infer_tool.format_wav(raw_audio_path)
        wav_path = Path(raw_audio_path)
        # wav_path = wav_path.with_suffix('.mp3')
        chunks = slicer.cut(wav_path, db_thresh=slice_db)
        audio_data, audio_sr = slicer.chunks2audio(wav_path, chunks)

        for spk in spk_list:
            audio = []
            #print(f"use voice lab:{spk}")
            for index, (slice_tag, data) in enumerate(audio_data):
                #print(f'#=====segment start, {round(len(data) / audio_sr, 3)}s======!')

                length = int(np.ceil(len(data) / audio_sr * svc_model.target_sample))
                if slice_tag:
                    #print('jump empty segment')
                    _audio = np.zeros(length)
                else:
                    # padd
                    pad_len = int(audio_sr * pad_seconds)
                    data = np.concatenate([np.zeros([pad_len]), data, np.zeros([pad_len])])
                    raw_path = io.BytesIO()
                    soundfile.write(raw_path, data, audio_sr, format="wav")
                    raw_path.seek(0)
                    out_audio, out_sr = svc_model.infer(spk, tran, raw_path,
                                                        cluster_infer_ratio=cluster_infer_ratio,
                                                        auto_predict_f0=auto_predict_f0,
                                                        noice_scale=noice_scale
                                                        )
                    _audio = out_audio.cpu().numpy()
                    pad_len = int(svc_model.target_sample * pad_seconds)
                    _audio = _audio[pad_len:-pad_len]

                audio.extend(list(infer_tool.pad_array(_audio, length)))
                if (stream and not slice_tag):  # output in stream format
                    res_path = output_path + f'/{str(index)}_{clean_name}_{spk}.{wav_format}'
                    soundfile.write(res_path, audio, svc_model.target_sample, format=wav_format)
                    generator.send('nothing')
                    generator.send(res_path)
                    audio = []

            key = "auto" if auto_predict_f0 else f"{tran}key"
            cluster_name = "" if cluster_infer_ratio == 0 else f"_{cluster_infer_ratio}"
            res_path = output_path + f'/{clean_name}_{key}_{spk}{cluster_name}.{wav_format}'
            if not stream:
                soundfile.write(res_path, audio, svc_model.target_sample, format=wav_format)
            return res_path


if __name__ == '__main__':
    main()
