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
import sys

# Get the path to the directory containing this script
current_dir = os.path.dirname(os.path.abspath(__file__))
# Construct the path to the "generated" folder
generated_dir = os.path.join(current_dir, "generated")
# Add the "generated" folder to sys.path
sys.path.append(generated_dir)

import argparse
from agl_service_voiceagent.utils.config import update_config_value, get_config_value
from agl_service_voiceagent.utils.common import add_trailing_slash
from agl_service_voiceagent.server import run_server
from agl_service_voiceagent.client import run_client


def print_version():
    print("Automotive Grade Linux (AGL)")
    print(f"Voice Agent Service v{get_config_value('SERVICE_VERSION')}")


def main():
    parser = argparse.ArgumentParser(description="Automotive Grade Linux (AGL) - Voice Agent Service")
    parser.add_argument('--version', action='store_true', help='Show version')
    
    subparsers = parser.add_subparsers(dest='subcommand', title='Available Commands')
    subparsers.required = False
    
    # Create subparsers for "run server" and "run client"
    server_parser = subparsers.add_parser('run-server', help='Run the Voice Agent gRPC Server')
    client_parser = subparsers.add_parser('run-client', help='Run the Voice Agent gRPC Client')
    
    server_parser.add_argument('--config', action='store_true', help='Starts the server solely based on values provided in config file.')
    server_parser.add_argument('--stt-model-path', required=False, help='Path to the Speech To Text model. Currently only supports VOSK Kaldi.')
    server_parser.add_argument('--snips-model-path', required=False, help='Path to the Snips NLU model.')
    server_parser.add_argument('--rasa-model-path', required=False, help='Path to the RASA NLU model.')
    server_parser.add_argument('--audio-store-dir', required=False, help='Directory to store the generated audio files.')
    server_parser.add_argument('--log-store-dir', required=False, help='Directory to store the generated log files.')

    client_parser.add_argument('--mode', required=True, help='Mode to run the client in. Supported modes: "wake-word", "auto" and "manual".')
    client_parser.add_argument('--nlu', required=True, help='NLU engine to use. Supported NLU egnines: "snips" and "rasa".')

    args = parser.parse_args()
    
    if args.version:
        print_version()

    elif args.subcommand == 'run-server':
        if not args.config:
            if not args.stt_model_path:
                raise ValueError("The --stt-model-path is missing. Please provide a value. Use --help to see available options.")
            
            if not args.snips_model_path:
                raise ValueError("The --snips-model-path is missing. Please provide a value. Use --help to see available options.")
            
            if not args.rasa_model_path:
                raise ValueError("The --rasa-model-path is missing. Please provide a value. Use --help to see available options.")

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

            # Update the log store dir in config.ini if provided
            log_dir = args.log_store_dir or get_config_value('BASE_LOG_DIR')
            log_dir = add_trailing_slash(os.path.abspath(log_dir)) if not os.path.isabs(log_dir) else log_dir
            update_config_value(log_dir, 'BASE_LOG_DIR')


        # create the base audio dir if not exists
        if not os.path.exists(get_config_value('BASE_AUDIO_DIR')):
            os.makedirs(get_config_value('BASE_AUDIO_DIR'))
        
        # create the base log dir if not exists
        if not os.path.exists(get_config_value('BASE_LOG_DIR')):
            os.makedirs(get_config_value('BASE_LOG_DIR'))

        run_server()

    elif args.subcommand == 'run-client':
        mode = args.mode
        if mode not in ['wake-word', 'auto', 'manual']:
            raise ValueError("Invalid mode. Supported modes: 'wake-word', 'auto' and 'manual'. Use --help to see available options.")
        
        model = args.nlu
        if model not in ['snips', 'rasa']:
            raise ValueError("Invalid NLU engine. Supported NLU engines: 'snips' and 'rasa'. Use --help to see available options.")
        
        run_client(mode, model)

    else:
        print_version()
        print("Use --help to see available options.")


if __name__ == '__main__':
    main()