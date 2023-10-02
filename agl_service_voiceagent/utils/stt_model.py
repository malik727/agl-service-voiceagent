# SPDX-License-Identifier: Apache-2.0
#
# Copyright (c) 2023 Malik Talha
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import json
import vosk
import wave
from utils.common import generate_unique_uuid

class STTModel:
    def __init__(self, model_path, sample_rate=16000):
        self.sample_rate = sample_rate
        self.model = vosk.Model(model_path)
        self.recognizer = {}
        self.chunk_size = 1024
    
    def setup_recognizer(self):
        uuid = generate_unique_uuid(6)
        self.recognizer[uuid] = vosk.KaldiRecognizer(self.model, self.sample_rate)
        return uuid

    def init_recognition(self, uuid, audio_data):
        return self.recognizer[uuid].AcceptWaveform(audio_data)

    def recognize(self, uuid, partial=False):
        self.recognizer[uuid].SetWords(True)
        if partial:
            result = json.loads(self.recognizer[uuid].PartialResult())
        else:
            result = json.loads(self.recognizer[uuid].Result())
            self.recognizer[uuid].Reset()
        return result
    
    def recognize_from_file(self, uuid, filename):
        if not os.path.exists(filename):
            print(f"Audio file '{filename}' not found.")
            return "FILE_NOT_FOUND"
        
        wf = wave.open(filename, "rb")
        if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
            print("Audio file must be WAV format mono PCM.")
            return "FILE_FORMAT_INVALID"
        
        # audio_data = wf.readframes(wf.getnframes())
        # we need to perform chunking as target AGL system can't handle an entire audio file
        audio_data = b""
        while True:
            chunk = wf.readframes(self.chunk_size)
            if not chunk:
                break  # End of file reached
            audio_data += chunk

        if audio_data:
            if self.init_recognition(uuid, audio_data):
                result = self.recognize(uuid)
                return result['text']
            else:
                result = self.recognize(uuid, partial=True)
                return result['partial']

        else:
            print("Voice not recognized. Please speak again...")
            return "VOICE_NOT_RECOGNIZED"
    
    def cleanup_recognizer(self, uuid):
        del self.recognizer[uuid]
    