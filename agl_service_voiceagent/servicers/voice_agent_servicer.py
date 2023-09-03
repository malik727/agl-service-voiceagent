import time
import threading
from generated import voice_agent_pb2
from generated import voice_agent_pb2_grpc
from utils.audio_recorder import AudioRecorder
from utils.wake_word import WakeWordDetector
from utils.stt_model import STTModel
from utils.config import get_config_value
from nlu.snips_interface import SnipsInterface
from nlu.rasa_interface import RASAInterface
from utils.common import generate_unique_uuid


class VoiceAgentServicer(voice_agent_pb2_grpc.VoiceAgentServiceServicer):
    def __init__(self):
        # Get the config values
        self.wake_word = get_config_value('WAKE_WORD')
        self.base_audio_dir = get_config_value('BASE_AUDIO_DIR')
        self.channels = int(get_config_value('CHANNELS'))
        self.sample_rate = int(get_config_value('SAMPLE_RATE'))
        self.bits_per_sample = int(get_config_value('BITS_PER_SAMPLE'))
        self.stt_model_path = get_config_value('STT_MODEL_PATH')
        self.snips_model_path = get_config_value('SNIPS_MODEL_PATH')
        self.rasa_model_path = get_config_value('RASA_MODEL_PATH')
        self.rasa_server_port = int(get_config_value('RASA_SERVER_PORT'))
        self.base_log_dir = get_config_value('BASE_LOG_DIR')

        # Initialize class methods
        self.detection_thread = None  # To hold the wake word detection thread
        self.stt_model = STTModel(self.stt_model_path, self.sample_rate)
        self.snips_interface = SnipsInterface(self.snips_model_path)
        self.rasa_interface = RASAInterface(self.rasa_server_port, self.rasa_model_path, self.base_log_dir)
        self.rasa_interface.start_server()
        self.rvc_stream_uuids = {}


    def DetectWakeWord(self, request, context):
        wake_word_detector = WakeWordDetector(self.wake_word, self.stt_model, self.channels, self.sample_rate, self.bits_per_sample)
        wake_word_detector.create_pipeline()
        detection_thread = threading.Thread(target=wake_word_detector.start_listening)
        detection_thread.start()

        while True:
            status = wake_word_detector.get_wake_word_status()
            time.sleep(1)
            yield voice_agent_pb2.WakeWordStatus(status=status)
            if status:
                break

        detection_thread.join()
    
    
    def RecognizeVoiceCommand(self, requests, context):
        intent = "INTENT_NOT_RECOGNIZED"
        intent_slots = []

        for request in requests:
            if request.record_mode == voice_agent_pb2.MANUAL:

                if request.action == voice_agent_pb2.START:
                    stream_uuid = generate_unique_uuid(8)
                    recorder = AudioRecorder(self.stt_model, self.base_audio_dir, self.channels, self.sample_rate, self.bits_per_sample)
                    recorder.set_pipeline_mode("manual")
                    audio_file = recorder.create_pipeline()

                    self.rvc_stream_uuids[stream_uuid] = {
                        "recorder": recorder,
                        "audio_file": audio_file
                    }
                    
                    stt = "PERFROMING_RECOGNITION"
                    recorder.start_recording()

                elif request.action == voice_agent_pb2.STOP:
                    stream_uuid = request.stream_id

                    recorder = self.rvc_stream_uuids[stream_uuid]["recorder"]
                    audio_file = self.rvc_stream_uuids[stream_uuid]["audio_file"]
                    del self.rvc_stream_uuids[stream_uuid]

                    stt = "NOT_RECOGNIZED"
                    recorder.stop_recording()
                    stt = self.stt_model.recognize_from_file(audio_file)
                    if stt not in ["FILE_NOT_FOUND", "FILE_FORMAT_INVALID", "NOT_RECOGNIZED"]:
                        if request.nlu_model == voice_agent_pb2.SNIPS:
                            extracted_intent = self.snips_interface.extract_intent(stt)
                            intent, intent_actions = self.snips_interface.process_intent(extracted_intent)
                            for action, value in intent_actions.items():
                                intent_slots.append(voice_agent_pb2.IntentSlot(name=action, value=value))
                        
                        elif request.nlu_model == voice_agent_pb2.RASA:
                            extracted_intent = self.rasa_interface.extract_intent(stt)
                            intent, intent_actions = self.rasa_interface.process_intent(extracted_intent)
                            for action, value in intent_actions.items():
                                intent_slots.append(voice_agent_pb2.IntentSlot(name=action, value=value))


        # Process the request and generate a RecognizeResult
        response = voice_agent_pb2.RecognizeResult(
            command=stt,
            intent=intent,
            intent_slots=intent_slots,
            stream_id=stream_uuid
        )
        return response
