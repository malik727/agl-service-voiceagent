import grpc
from generated import voice_agent_pb2
from generated import voice_agent_pb2_grpc
from utils.config import get_config_value

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
            print("Auto mode not supported yet.")

        elif mode == 'manual':
            stub = voice_agent_pb2_grpc.VoiceAgentServiceStub(channel)
            print("Recording voice command...")
            record_request = voice_agent_pb2.RecognizeControl(action=voice_agent_pb2.START, nlu_model=nlu_model, record_mode=voice_agent_pb2.MANUAL)
            record_result = stub.RecognizeVoiceCommand(record_request)
            print("Voice command recorded!")
            # Process the response
            print("Command:", record_result.command)
            print("Intent:", record_result.intent)
            for slot in record_result.intent_slots:
                print("Slot Name:", slot.name)
                print("Slot Value:", slot.value)