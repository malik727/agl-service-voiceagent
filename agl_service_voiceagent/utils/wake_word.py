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

import gi
import vosk
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib

Gst.init(None)
GLib.threads_init()

class WakeWordDetector:
    def __init__(self, wake_word, stt_model, channels=1, sample_rate=16000, bits_per_sample=16):
        self.loop = GLib.MainLoop()
        self.pipeline = None
        self.bus = None
        self.wake_word = wake_word
        self.wake_word_detected = False
        self.sample_rate = sample_rate
        self.channels = channels
        self.bits_per_sample = bits_per_sample
        self.frame_size = int(self.sample_rate * 0.02)
        self.stt_model = stt_model # Speech to text model recognizer
        self.recognizer_uuid = stt_model.setup_recognizer() 
        self.buffer_duration = 1  # Buffer audio for atleast 1 second
        self.audio_buffer = bytearray()
    
    def get_wake_word_status(self):
        return self.wake_word_detected

    def create_pipeline(self):
        print("Creating pipeline for Wake Word Detection...")
        self.pipeline = Gst.Pipeline()
        autoaudiosrc = Gst.ElementFactory.make("autoaudiosrc", None)
        queue = Gst.ElementFactory.make("queue", None)
        audioconvert = Gst.ElementFactory.make("audioconvert", None)
        wavenc = Gst.ElementFactory.make("wavenc", None)

        capsfilter = Gst.ElementFactory.make("capsfilter", None)
        caps = Gst.Caps.new_empty_simple("audio/x-raw")
        caps.set_value("format", "S16LE")
        caps.set_value("rate", self.sample_rate)
        caps.set_value("channels", self.channels)
        capsfilter.set_property("caps", caps)

        appsink = Gst.ElementFactory.make("appsink", None)
        appsink.set_property("emit-signals", True)
        appsink.set_property("sync", False)  # Set sync property to False to enable async processing
        appsink.connect("new-sample", self.on_new_buffer, None)

        self.pipeline.add(autoaudiosrc)
        self.pipeline.add(queue)
        self.pipeline.add(audioconvert)
        self.pipeline.add(wavenc)
        self.pipeline.add(capsfilter)
        self.pipeline.add(appsink)
        
        autoaudiosrc.link(queue)
        queue.link(audioconvert)
        audioconvert.link(capsfilter)
        capsfilter.link(appsink)

        self.bus = self.pipeline.get_bus()
        self.bus.add_signal_watch()
        self.bus.connect("message", self.on_bus_message)

    def on_new_buffer(self, appsink, data) -> Gst.FlowReturn:
        sample = appsink.emit("pull-sample")
        buffer = sample.get_buffer()
        data = buffer.extract_dup(0, buffer.get_size())
        self.audio_buffer.extend(data)

        if len(self.audio_buffer) >= self.sample_rate * self.buffer_duration * self.channels * self.bits_per_sample // 8:
            self.process_audio_buffer()

        return Gst.FlowReturn.OK
    

    def process_audio_buffer(self):
        # Process the accumulated audio data using the audio model
        audio_data = bytes(self.audio_buffer)
        if self.stt_model.init_recognition(self.recognizer_uuid, audio_data):
            stt_result = self.stt_model.recognize(self.recognizer_uuid)
            print("STT Result: ", stt_result)
            if self.wake_word in stt_result["text"]:
                self.wake_word_detected = True
                print("Wake word detected!")
                self.pipeline.send_event(Gst.Event.new_eos())

        self.audio_buffer.clear()  # Clear the buffer
    

    def send_eos(self):
        self.pipeline.send_event(Gst.Event.new_eos())
        self.audio_buffer.clear()


    def start_listening(self):
        self.pipeline.set_state(Gst.State.PLAYING)
        print("Listening for Wake Word...")
        self.loop.run()


    def stop_listening(self):
        self.cleanup_pipeline()
        self.loop.quit()


    def on_bus_message(self, bus, message):
        if message.type == Gst.MessageType.EOS:
            print("End-of-stream message received")
            self.stop_listening()
        elif message.type == Gst.MessageType.ERROR:
            err, debug_info = message.parse_error()
            print(f"Error received from element {message.src.get_name()}: {err.message}")
            print(f"Debugging information: {debug_info}")
            self.stop_listening()
        elif message.type == Gst.MessageType.WARNING:
            err, debug_info = message.parse_warning()
            print(f"Warning received from element {message.src.get_name()}: {err.message}")
            print(f"Debugging information: {debug_info}")
        elif message.type == Gst.MessageType.STATE_CHANGED:
            if isinstance(message.src, Gst.Pipeline):
                old_state, new_state, pending_state = message.parse_state_changed()
                print(("Pipeline state changed from %s to %s." %
                       (old_state.value_nick, new_state.value_nick)))
    

    def cleanup_pipeline(self):
        if self.pipeline is not None:
            print("Cleaning up pipeline...")
            self.pipeline.set_state(Gst.State.NULL)
            self.bus.remove_signal_watch()
            print("Pipeline cleanup complete!")
            self.bus = None
            self.pipeline = None
            self.stt_model.cleanup_recognizer(self.recognizer_uuid)
