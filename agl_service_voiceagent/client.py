import time
import grpc
from agl_service_voiceagent.generated import voice_agent_pb2
from agl_service_voiceagent.generated import voice_agent_pb2_grpc
from agl_service_voiceagent.utils.config import get_config_value

# following code is only reqired for logging
import logging
logging.basicConfig()
logging.getLogger("grpc").setLevel(logging.DEBUG)

SERVER_URL = get_config_value('SERVER_ADDRESS') + ":" + str(get_config_value('SERVER_PORT'))

def run_client(mode, nlu_model):
    nlu_model = voice_agent_pb2.SNIPS if nlu_model == "snips" else voice_agent_pb2.RASA
    print("Starting Voice Agent Client...")
    print(f"Client connecting to URL: {SERVER_URL}")
    with grpc.insecure_channel(SERVER_URL) as channel:
        print("Press Ctrl+C to stop the client.")
        print("Voice Agent Client started!")
        if mode == 'wake-word':
            stub = voice_agent_pb2_grpc.VoiceAgentServiceStub(channel)
            print("Listening for wake word...")
            wake_request = voice_agent_pb2.Empty()
            wake_results = stub.DetectWakeWord(wake_request)
            wake_word_detected = False
            for wake_result in wake_results:
                print("Wake word status: ", wake_word_detected)
                if wake_result.status:
                    print("Wake word status: ", wake_result.status)
                    wake_word_detected = True
                    break

        elif mode == 'auto':
            raise ValueError("Auto mode is not implemented yet.")

        elif mode == 'manual':
            stub = voice_agent_pb2_grpc.VoiceAgentServiceStub(channel)
            print("Recording voice command...")
            record_start_request = voice_agent_pb2.RecognizeControl(action=voice_agent_pb2.START, nlu_model=nlu_model, record_mode=voice_agent_pb2.MANUAL)
            response = stub.RecognizeVoiceCommand(iter([record_start_request]))
            stream_id = response.stream_id
            time.sleep(5) # any arbitrary pause here
            record_stop_request = voice_agent_pb2.RecognizeControl(action=voice_agent_pb2.STOP, nlu_model=nlu_model, record_mode=voice_agent_pb2.MANUAL, stream_id=stream_id)
            record_result = stub.RecognizeVoiceCommand(iter([record_stop_request]))
            print("Voice command recorded!")
            
            status = "Uh oh! Status is unknown."
            if record_result.status == voice_agent_pb2.REC_SUCCESS:
                status = "Yay! Status is success."
            elif record_result.status == voice_agent_pb2.VOICE_NOT_RECOGNIZED:
                status = "Voice not recognized."
            elif record_result.status == voice_agent_pb2.INTENT_NOT_RECOGNIZED:
                status = "Intent not recognized."

            # Process the response
            print("Command:", record_result.command)
            print("Status:", status)
            print("Intent:", record_result.intent)
            for slot in record_result.intent_slots:
                print("Slot Name:", slot.name)
                print("Slot Value:", slot.value)