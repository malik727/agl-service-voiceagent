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
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib

Gst.init(None)
GLib.threads_init()

class WakeWordDetector:
    """
    WakeWordDetector is a class for detecting a wake word in an audio stream using GStreamer and Vosk.
    """

    def __init__(self, wake_word, stt_model, channels=1, sample_rate=16000, bits_per_sample=16):
        """
        Initialize the WakeWordDetector instance with the provided parameters.

        Args:
            wake_word (str): The wake word to detect in the audio stream.
            stt_model (STTModel): An instance of the STTModel for speech-to-text recognition.
            channels (int, optional): The number of audio channels (default is 1).
            sample_rate (int, optional): The audio sample rate in Hz (default is 16000).
            bits_per_sample (int, optional): The number of bits per sample (default is 16).
        """
        self.loop = GLib.MainLoop()
        self.pipeline = None
        self.bus = None
        self.wake_word = wake_word
        self.wake_word_detected = False
        self.sample_rate = sample_rate
        self.channels = channels
        self.bits_per_sample = bits_per_sample
        self.wake_word_model = stt_model # Speech to text model recognizer
        self.recognizer_uuid = stt_model.setup_recognizer() 
        self.audio_buffer = bytearray()
        self.segment_size = int(self.sample_rate * 1.0)  # Adjust the segment size (e.g., 1 second)
     
    
    def get_wake_word_status(self):
        """
        Get the status of wake word detection.

        Returns:
            bool: True if the wake word has been detected, False otherwise.
        """
        return self.wake_word_detected

    def create_pipeline(self):
        """
        Create and configure the GStreamer audio processing pipeline for wake word detection.
        """
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
        """
        Callback function to handle new audio buffers from GStreamer appsink.

        Args:
            appsink (Gst.AppSink): The GStreamer appsink.
            data (object): User data (not used).

        Returns:
            Gst.FlowReturn: Indicates the status of buffer processing.
        """
        sample = appsink.emit("pull-sample")
        buffer = sample.get_buffer()
        data = buffer.extract_dup(0, buffer.get_size())

        # Add the new data to the buffer
        self.audio_buffer.extend(data)

        # Process audio in segments
        while len(self.audio_buffer) >= self.segment_size:
            segment = self.audio_buffer[:self.segment_size]
            self.process_audio_segment(segment)

            # Advance the buffer by the segment size
            self.audio_buffer = self.audio_buffer[self.segment_size:]

        return Gst.FlowReturn.OK

    def process_audio_segment(self, segment):
        """
        Process an audio segment for wake word detection.

        Args:
            segment (bytes): The audio segment to process.
        """
        # Process the audio data segment
        audio_data = bytes(segment)

        # Perform wake word detection on the audio_data
        if self.wake_word_model.init_recognition(self.recognizer_uuid, audio_data):
            stt_result = self.wake_word_model.recognize(self.recognizer_uuid)
            print("STT Result: ", stt_result)
            if self.wake_word in stt_result["text"]:
                self.wake_word_detected = True
                print("Wake word detected!")
                self.pipeline.send_event(Gst.Event.new_eos())

    def send_eos(self):
        """
        Send an End-of-Stream (EOS) event to the pipeline.
        """
        self.pipeline.send_event(Gst.Event.new_eos())
        self.audio_buffer.clear()


    def start_listening(self):
        """
        Start listening for the wake word and enter the event loop.
        """
        self.pipeline.set_state(Gst.State.PLAYING)
        print("Listening for Wake Word...")
        self.loop.run()


    def stop_listening(self):
        """
        Stop listening for the wake word and clean up the pipeline.
        """
        self.cleanup_pipeline()
        self.loop.quit()


    def on_bus_message(self, bus, message):
        """
        Handle GStreamer bus messages and perform actions based on the message type.

        Args:
            bus (Gst.Bus): The GStreamer bus.
            message (Gst.Message): The GStreamer message to process.
        """
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
        """
        Clean up the GStreamer pipeline and release associated resources.
        """
        if self.pipeline is not None:
            print("Cleaning up pipeline...")
            self.pipeline.set_state(Gst.State.NULL)
            self.bus.remove_signal_watch()
            print("Pipeline cleanup complete!")
            self.bus = None
            self.pipeline = None
            self.wake_word_model.cleanup_recognizer(self.recognizer_uuid)
