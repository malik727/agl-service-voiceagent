import os
import json
import vosk
import wave

class STTModel:
    def __init__(self, model_path, sample_rate=16000):
        self.sample_rate = sample_rate
        self.model = vosk.Model(model_path)
        self.recognizer = vosk.KaldiRecognizer(self.model, self.sample_rate)
    
    def init_rec(self, audio_data):
        return self.recognizer.AcceptWaveform(audio_data)

    def recognize(self):
        self.recognizer.SetWords(True)
        result = json.loads(self.recognizer.Result())
        self.recognizer.Reset()
        return result
    
    def recognize_from_file(self, filename):
        if not os.path.exists(filename):
            print(f"Audio file '{filename}' not found.")
            return "FILE_NOT_FOUND"
        
        wf = wave.open(filename, "rb")
        if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
            print("Audio file must be WAV format mono PCM.")
            return "FILE_FORMAT_INVALID"
        
        audio_data = wf.readframes(wf.getnframes())
        
        if self.init_rec(audio_data):
            result = self.recognize()
            self.recognizer.Reset()
            return result['text']
        else:
            self.recognizer.Reset()
            print("Voice not recognized. Please speak again...")
            return "NOT_RECOGNIZED"