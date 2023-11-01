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

import grpc
from concurrent import futures
from agl_service_voiceagent.generated import voice_agent_pb2_grpc
from agl_service_voiceagent.servicers.voice_agent_servicer import VoiceAgentServicer
from agl_service_voiceagent.utils.config import get_config_value, get_logger

def run_server():
    logger = get_logger()
    SERVER_URL = get_config_value('SERVER_ADDRESS') + ":" + str(get_config_value('SERVER_PORT'))
    print("Starting Voice Agent Service...")
    print(f"STT Model Path: {get_config_value('STT_MODEL_PATH')}")
    print(f"Audio Store Directory: {get_config_value('BASE_AUDIO_DIR')}")
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    voice_agent_pb2_grpc.add_VoiceAgentServiceServicer_to_server(VoiceAgentServicer(), server)
    server.add_insecure_port(SERVER_URL)
    print("Press Ctrl+C to stop the server.")
    print("Voice Agent Server started!")
    print(f"Server running at URL: {SERVER_URL}")
    logger.info(f"Voice Agent Service started in server mode! Server running at URL: {SERVER_URL}")
    server.start()
    server.wait_for_termination()