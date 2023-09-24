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
import time
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib

Gst.init(None)
GLib.threads_init()

class AudioRecorder:
    def __init__(self, stt_model, audio_files_basedir, channels=1, sample_rate=16000, bits_per_sample=16):
        self.loop = GLib.MainLoop()
        self.mode = None
        self.pipeline = None
        self.bus = None
        self.audio_files_basedir = audio_files_basedir
        self.sample_rate = sample_rate
        self.channels = channels
        self.bits_per_sample = bits_per_sample
        self.frame_size = int(self.sample_rate * 0.02)
        self.audio_model = stt_model
        self.buffer_duration = 1  # Buffer audio for atleast 1 second
        self.audio_buffer = bytearray()
        self.energy_threshold = 50000  # Adjust this threshold as needed
        self.silence_frames_threshold = 10
        self.frames_above_threshold = 0
    

    def create_pipeline(self):
        print("Creating pipeline for audio recording in {} mode...".format(self.mode))
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

        self.pipeline.add(autoaudiosrc)
        self.pipeline.add(queue)
        self.pipeline.add(audioconvert)
        self.pipeline.add(wavenc)
        self.pipeline.add(capsfilter)
        
        autoaudiosrc.link(queue)
        queue.link(audioconvert)
        audioconvert.link(capsfilter)

        audio_file_name = f"{self.audio_files_basedir}{int(time.time())}.wav"

        filesink = Gst.ElementFactory.make("filesink", None)
        filesink.set_property("location", audio_file_name)
        self.pipeline.add(filesink)
        capsfilter.link(wavenc)
        wavenc.link(filesink)

        self.bus = self.pipeline.get_bus()
        self.bus.add_signal_watch()
        self.bus.connect("message", self.on_bus_message)

        return audio_file_name


    def start_recording(self):
        self.pipeline.set_state(Gst.State.PLAYING)
        print("Recording Voice Input...")


    def stop_recording(self):
        print("Stopping recording...")
        self.frames_above_threshold = 0
        self.cleanup_pipeline()
        print("Recording finished!")

    
    def set_pipeline_mode(self, mode):
        self.mode = mode

    
    # this method helps with error handling
    def on_bus_message(self, bus, message):
        if message.type == Gst.MessageType.EOS:
            print("End-of-stream message received")
            self.stop_recording()

        elif message.type == Gst.MessageType.ERROR:
            err, debug_info = message.parse_error()
            print(f"Error received from element {message.src.get_name()}: {err.message}")
            print(f"Debugging information: {debug_info}")
            self.stop_recording()

        elif message.type == Gst.MessageType.WARNING:
            err, debug_info = message.parse_warning()
            print(f"Warning received from element {message.src.get_name()}: {err.message}")
            print(f"Debugging information: {debug_info}")

        elif message.type == Gst.MessageType.STATE_CHANGED:
            if isinstance(message.src, Gst.Pipeline):
                old_state, new_state, pending_state = message.parse_state_changed()
                print(("Pipeline state changed from %s to %s." %
                       (old_state.value_nick, new_state.value_nick)))
                
        elif self.mode == "auto" and message.type == Gst.MessageType.ELEMENT:
            if message.get_structure().get_name() == "level":
                rms = message.get_structure()["rms"][0]
                if rms > self.energy_threshold:
                    self.frames_above_threshold += 1
                    # if self.frames_above_threshold >= self.silence_frames_threshold:
                    #     self.start_recording()
                else:
                    if self.frames_above_threshold > 0:
                        self.frames_above_threshold -= 1
                        if self.frames_above_threshold == 0:
                            self.stop_recording()
    

    def cleanup_pipeline(self):
        if self.pipeline is not None:
            print("Cleaning up pipeline...")
            self.pipeline.set_state(Gst.State.NULL)
            self.bus.remove_signal_watch()
            print("Pipeline cleanup complete!")
            self.bus = None
            self.pipeline = None
