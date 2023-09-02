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


class VoiceAgentServicer(voice_agent_pb2_grpc.VoiceAgentServiceServicer):
    def __init__(self):
        # Get the config values
        STT_MODEL_PATH = get_config_value('STT_MODEL_PATH')
        WAKE_WORD = get_config_value('WAKE_WORD')
        BASE_AUDIO_DIR = get_config_value('BASE_AUDIO_DIR')
        CHANNELS = int(get_config_value('CHANNELS'))
        SAMPLE_RATE = int(get_config_value('SAMPLE_RATE'))
        BITS_PER_SAMPLE = int(get_config_value('BITS_PER_SAMPLE'))
        SNIPS_MODEL_PATH = get_config_value('SNIPS_MODEL_PATH')
        RASA_MODEL_PATH = get_config_value('RASA_MODEL_PATH')
        RASA_SERVER_PORT = int(get_config_value('RASA_SERVER_PORT'))
        BASE_LOG_DIR = get_config_value('BASE_LOG_DIR')

        # Initialize class methods
        self.stt_model = STTModel(STT_MODEL_PATH, SAMPLE_RATE)
        self.wake_word_detector = WakeWordDetector(WAKE_WORD, self.stt_model, CHANNELS, SAMPLE_RATE, BITS_PER_SAMPLE)
        self.recorder = AudioRecorder(self.stt_model, BASE_AUDIO_DIR, CHANNELS, SAMPLE_RATE, BITS_PER_SAMPLE)
        self.detection_thread = None  # To hold the wake word detection thread
        self.snips_interface = SnipsInterface(SNIPS_MODEL_PATH)
        self.rasa_interface = RASAInterface(RASA_SERVER_PORT, RASA_MODEL_PATH, BASE_LOG_DIR)
        self.rasa_interface.start_server()

    def DetectWakeWord(self, request, context):
        self.wake_word_detector.cleanup_pipeline()
        self.wake_word_detector.create_pipeline()
        self.detection_thread = threading.Thread(target=self.wake_word_detector.start_listening)
        self.detection_thread.start()
        while True:
            status = self.wake_word_detector.get_wake_word_status()
            time.sleep(1)
            yield voice_agent_pb2.WakeWordStatus(status=status)
            if status:
                break
        
        self.detection_thread.join()
    
    def RecognizeVoiceCommand(self, request, context):

        if request.record_mode == voice_agent_pb2.AUTO:
            self.recorder.cleanup_pipeline()
            audio_file = self.recorder.create_pipeline("auto")
            self.recorder.start_recording()
        
        elif request.record_mode == voice_agent_pb2.MANUAL:
            self.recorder.cleanup_pipeline()
            audio_file = self.recorder.create_pipeline("manual")
            self.recorder.start_recording()
            time.sleep(7.5)
            self.recorder.stop_recording()
            stt = self.stt_model.recognize_from_file(audio_file)
            intent = "INTENT_NOT_RECOGNIZED"
            intent_slots = []
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
            intent_slots=intent_slots
        )
        return response
