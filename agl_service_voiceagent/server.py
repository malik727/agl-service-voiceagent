import grpc
from concurrent import futures
from agl_service_voiceagent.generated import voice_agent_pb2_grpc
from agl_service_voiceagent.servicers.voice_agent_servicer import VoiceAgentServicer
from agl_service_voiceagent.utils.config import get_config_value

SERVER_URL = get_config_value('SERVER_ADDRESS') + ":" + str(get_config_value('SERVER_PORT'))

def run_server():
    print("Starting Voice Agent Service...")
    print(f"Server running at URL: {SERVER_URL}")
    print(f"STT Model Path: {get_config_value('STT_MODEL_PATH')}")
    print(f"Audio Store Directory: {get_config_value('BASE_AUDIO_DIR')}")
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    voice_agent_pb2_grpc.add_VoiceAgentServiceServicer_to_server(VoiceAgentServicer(), server)
    server.add_insecure_port(SERVER_URL)
    print("Press Ctrl+C to stop the server.")
    print("Voice Agent Server started!")
    server.start()
    server.wait_for_termination()