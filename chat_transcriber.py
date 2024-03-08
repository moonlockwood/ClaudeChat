from openai import OpenAI

import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write

from PyQt5.QtCore import QThread

class OpenAIThread(QThread):
    def __init__(self):
        QThread.__init__(self)
        self.init_openai()
        self.recorder = audio_recorder()
    
    def init_openai(self):
        with open('settings/key.txt', 'r') as key_file:
            api_key = key_file.readline().strip()
            self.client = OpenAI()
            self.client.api_key = api_key   
            self.client.organization = None
            self.recorder = audio_recorder()
        
    def transcribe_audio(self, audio_filename):
        audio_file= open(audio_filename, "rb")
        transcript = self.client.audio.transcriptions.create(
            model="whisper-1", 
            file=audio_file,
            response_format="text"
            )
        return transcript

class audio_recorder():
    def __init__(self):
        self.init_recorder()

    def init_recorder(self):     
        self.sample_rate = 16000  # in Hz
        recording = []
        stream = None

    def callback(self, indata, frames, time, status):
        global recording
        recording.append(indata.copy())

    def start_recording(self):
        global stream
        global recording
        recording = []
        stream = sd.InputStream(samplerate=self.sample_rate, channels=1, callback=self.callback)
        stream.start()

    def stop_recording(self, filename):
        global stream
        global recording

        if stream is not None:
            stream.stop()
            stream.close()

        if recording:
            audio_data = np.concatenate(recording, axis=0)
            write(filename, self.sample_rate, audio_data)
