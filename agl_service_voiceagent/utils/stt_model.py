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
from agl_service_voiceagent.utils.common import generate_unique_uuid

class STTModel:
    """
    STTModel is a class for speech-to-text (STT) recognition using the Vosk speech recognition library.
    """

    def __init__(self, model_path, sample_rate=16000):
        """
        Initialize the STTModel instance with the provided model and sample rate.

        Args:
            model_path (str): The path to the Vosk speech recognition model.
            sample_rate (int, optional): The audio sample rate in Hz (default is 16000).
        """
        self.sample_rate = sample_rate
        self.model = vosk.Model(model_path)
        self.recognizer = {}
        self.chunk_size = 1024
    

    def setup_recognizer(self):
        """
        Set up a Vosk recognizer for a new session and return a unique identifier (UUID) for the session.

        Returns:
            str: A unique identifier (UUID) for the session.
        """
        uuid = generate_unique_uuid(6)
        self.recognizer[uuid] = vosk.KaldiRecognizer(self.model, self.sample_rate)
        return uuid


    def init_recognition(self, uuid, audio_data):
        """
        Initialize the Vosk recognizer for a session with audio data.

        Args:
            uuid (str): The unique identifier (UUID) for the session.
            audio_data (bytes): Audio data to process.

        Returns:
            bool: True if initialization was successful, False otherwise.
        """
        return self.recognizer[uuid].AcceptWaveform(audio_data)


    def recognize(self, uuid, partial=False):
        """
        Recognize speech and return the result as a JSON object.

        Args:
            uuid (str): The unique identifier (UUID) for the session.
            partial (bool, optional): If True, return partial recognition results (default is False).

        Returns:
            dict: A JSON object containing recognition results.
        """
        self.recognizer[uuid].SetWords(True)
        if partial:
            result = json.loads(self.recognizer[uuid].PartialResult())
        else:
            result = json.loads(self.recognizer[uuid].Result())
            self.recognizer[uuid].Reset()
        return result
    

    def recognize_from_file(self, uuid, filename):
        """
        Recognize speech from an audio file and return the recognized text.

        Args:
            uuid (str): The unique identifier (UUID) for the session.
            filename (str): The path to the audio file.

        Returns:
            str: The recognized text or error messages.
        """
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
        """
        Clean up and remove the Vosk recognizer for a session.

        Args:
            uuid (str): The unique identifier (UUID) for the session.
        """
        del self.recognizer[uuid]
    