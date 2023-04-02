from pydub import AudioSegment
import pyaudio
import wave
import keyboard
import threading
from third.iat_ws import vocal_to_text

# 设置录音参数
chunk = 1024  # 每个数据块的大小
sample_format = pyaudio.paInt16  # 采样大小
channels = 1  # 声道数
fs = 16000  # 采样率
class Recorder:
    def __init__(self):
        self.p=pyaudio.PyAudio()
        self.recording = False
        self.record_thread = None
        self.frame = None
        self.result=""
        
    def start(self):
        self.recording = True
        self.record_thread=threading.Thread(target=self.record)
        self.record_thread.start()
        
    def stop(self):
        self.recording = False
        self.record_thread.join()
        self.save()
        
    def record(self):
        # 创建 WAV 文件
        self.frame = []
        stream = self.p.open(format=sample_format,
                        channels=channels,
                        rate=fs,
                        frames_per_buffer=chunk,
                        input=True)

        while self.recording:
            data = stream.read(chunk)
            self.frame.append(data)

        # 停止录音流
        stream.stop_stream()
        stream.close()


    def save(self):
        # 保存 WAV 文件列表
        wf = b"".join(self.frame)
        audio_data = AudioSegment(
            data=wf,
            sample_width=self.p.get_sample_size(sample_format),
            frame_rate=16000,
            channels=1
        )
        new_fs=16000
        audio_data.set_frame_rate(new_fs)
        output_file = f"./raw/audio_for_vtt.pcm"
        with wave.open(output_file, "wb") as f:
            f.setnchannels(1)
            f.setsampwidth(2)
            f.setframerate(new_fs)
            f.writeframes(audio_data._data)
        self.result=vocal_to_text(output_file)
        

