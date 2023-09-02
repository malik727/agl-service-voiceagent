import sys
sys.path.append("generated/") # To access the generated grpc files

import os
import grpc
import argparse
from concurrent import futures
from generated import voice_agent_pb2
from generated import voice_agent_pb2_grpc
from servicers.voice_agent_servicer import VoiceAgentServicer
from utils.config import update_config_value, get_config_value
from utils.common import add_trailing_slash


SERVER_URL = get_config_value('SERVER_ADDRESS') + ":" + str(get_config_value('SERVER_PORT'))


def print_version():
    print("Automotive Grade Linux (AGL)")
    print(f"Voice Agent Service v{get_config_value('SERVICE_VERSION')}")


def run_server():
    print("Starting Voice Agent Service...")
    print(f"Server running at URL: {SERVER_URL}")
    print(f"STT Model Path: {get_config_value('STT_MODEL_PATH')}")
    print(f"Audio Store Directory: {get_config_value('BASE_AUDIO_DIR')}")
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    voice_agent_servicer = VoiceAgentServicer()
    voice_agent_pb2_grpc.add_VoiceAgentServiceServicer_to_server(voice_agent_servicer, server)
    server.add_insecure_port(SERVER_URL)
    print("Press Ctrl+C to stop the server.")
    print("Voice Agent Server started!")
    server.start()
    server.wait_for_termination()


def run_client(mode, nlu_model):
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


def main():
    parser = argparse.ArgumentParser(description="Automotive Grade Linux (AGL) - Voice Agent Service")
    parser.add_argument('--version', action='store_true', help='Show version')
    
    subparsers = parser.add_subparsers(dest='subcommand', title='Available Commands')
    subparsers.required = False
    
    # Create subparsers for "run server" and "run client"
    server_parser = subparsers.add_parser('run-server', help='Run the Voice Agent gRPC Server')
    client_parser = subparsers.add_parser('run-client', help='Run the Voice Agent gRPC Client')
    
    server_parser.add_argument('--stt-model-path', required=True, help='Path to the Speech To Text model. Currently only supports VOSK Kaldi.')
    server_parser.add_argument('--snips-model-path', required=True, help='Path to the Snips NLU model.')
    server_parser.add_argument('--rasa-model-path', required=True, help='Path to the RASA NLU model.')
    server_parser.add_argument('--audio-store-dir', required=False, help='Directory to store the generated audio files.')
    server_parser.add_argument('--log-store-dir', required=False, help='Directory to store the generated log files.')

    client_parser.add_argument('--mode', required=True, help='Mode to run the client in. Supported modes: "wake_word", "auto" and "manual".')
    client_parser.add_argument('--nlu', required=True, help='NLU engine to use. Supported NLU egnines: "snips" and "rasa".')

    args = parser.parse_args()
    
    if args.version:
        print_version()

    elif args.subcommand == 'run-server':
        stt_path = args.stt_model_path
        snips_model_path = args.snips_model_path
        rasa_model_path = args.rasa_model_path
        
        # Convert to an absolute path if it's a relative path
        stt_path = add_trailing_slash(os.path.abspath(stt_path)) if not os.path.isabs(stt_path) else stt_path
        snips_model_path = add_trailing_slash(os.path.abspath(snips_model_path)) if not os.path.isabs(snips_model_path) else snips_model_path
        rasa_model_path = add_trailing_slash(os.path.abspath(rasa_model_path)) if not os.path.isabs(rasa_model_path) else rasa_model_path
        
        # Also update the config.ini file
        update_config_value(stt_path, 'STT_MODEL_PATH')
        update_config_value(snips_model_path, 'SNIPS_MODEL_PATH')
        update_config_value(rasa_model_path, 'RASA_MODEL_PATH')

        # Update the audio store dir in config.ini if provided
        audio_dir = args.audio_store_dir or get_config_value('BASE_AUDIO_DIR')
        audio_dir = add_trailing_slash(os.path.abspath(audio_dir)) if not os.path.isabs(audio_dir) else audio_dir
        update_config_value(audio_dir, 'BASE_AUDIO_DIR')

        # create the base audio dir if not exists
        if not os.path.exists(get_config_value('BASE_AUDIO_DIR')):
            os.makedirs(get_config_value('BASE_AUDIO_DIR'))

        # Update the log store dir in config.ini if provided
        log_dir = args.log_store_dir or get_config_value('BASE_LOG_DIR')
        log_dir = add_trailing_slash(os.path.abspath(log_dir)) if not os.path.isabs(log_dir) else log_dir
        update_config_value(log_dir, 'BASE_LOG_DIR')

        # create the base log dir if not exists
        if not os.path.exists(get_config_value('BASE_LOG_DIR')):
            os.makedirs(get_config_value('BASE_LOG_DIR'))

        run_server()

    elif args.subcommand == 'run-client':
        mode = args.mode
        if mode not in ['wake-word', 'auto', 'manual']:
            print("Invalid mode. Supported modes: 'wake-word', 'auto' and 'manual'.")
            return
        
        model = args.nlu
        if model not in ['snips', 'rasa']:
            print("Invalid NLU engine. Supported NLU engines: 'snips' and 'rasa'.")
            return
        
        model = voice_agent_pb2.SNIPS if args.nlu == "snips" else voice_agent_pb2.RASA
        
        run_client(mode, model)

    else:
        print_version()
        print("Use --help to see available options.")


if __name__ == '__main__':
    main()