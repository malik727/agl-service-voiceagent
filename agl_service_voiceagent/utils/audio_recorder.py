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
import time
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib

Gst.init(None)
GLib.threads_init()

class AudioRecorder:
    """
    AudioRecorder is a class for recording audio using GStreamer in various modes.
    """

    def __init__(self, stt_model, audio_files_basedir, channels=1, sample_rate=16000, bits_per_sample=16):
        """
        Initialize the AudioRecorder instance with the provided parameters.

        Args:
            stt_model (str): The speech-to-text model to use for voice input recognition.
            audio_files_basedir (str): The base directory for saving audio files.
            channels (int, optional): The number of audio channels (default is 1).
            sample_rate (int, optional): The audio sample rate in Hz (default is 16000).
            bits_per_sample (int, optional): The number of bits per sample (default is 16).
        """
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
        """
        Create and configure the GStreamer audio recording pipeline.

        Returns:
            str: The name of the audio file being recorded.
        """
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
        """
        Start recording audio using the GStreamer pipeline.
        """
        self.pipeline.set_state(Gst.State.PLAYING)
        print("Recording Voice Input...")


    def stop_recording(self):
        """
        Stop audio recording and clean up the GStreamer pipeline.
        """
        print("Stopping recording...")
        # self.cleanup_pipeline()
        self.pipeline.send_event(Gst.Event.new_eos())
        print("Recording finished!")

    
    def set_pipeline_mode(self, mode):
        """
        Set the recording mode to 'auto' or 'manual'.

        Args:
            mode (str): The recording mode ('auto' or 'manual').
        """
        self.mode = mode

    
    def on_bus_message(self, bus, message):
        """
        Handle GStreamer bus messages and perform actions based on the message type.

        Args:
            bus (Gst.Bus): The GStreamer bus.
            message (Gst.Message): The GStreamer message to process.
        """
        if message.type == Gst.MessageType.EOS:
            print("End-of-stream message received")
            self.cleanup_pipeline()

        elif message.type == Gst.MessageType.ERROR:
            err, debug_info = message.parse_error()
            print(f"Error received from element {message.src.get_name()}: {err.message}")
            print(f"Debugging information: {debug_info}")
            self.cleanup_pipeline()

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
        """
        Clean up the GStreamer pipeline, set it to NULL state, and remove the signal watch.
        """
        if self.pipeline is not None:
            print("Cleaning up pipeline...")
            self.pipeline.set_state(Gst.State.NULL)
            self.bus.remove_signal_watch()
            print("Pipeline cleanup complete!")
            self.bus = None
            self.pipeline = None
