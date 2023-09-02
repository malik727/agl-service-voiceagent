import re
import time
import requests
import subprocess
from concurrent.futures import ThreadPoolExecutor

class RASAInterface:
    def __init__(self, port, model_path, log_dir, max_threads=5):
        self.port = port
        self.model_path = model_path
        self.max_threads = max_threads
        self.server_process = None
        self.thread_pool = ThreadPoolExecutor(max_workers=max_threads)
        self.log_file = log_dir+"rasa_server_logs.txt"


    def _start_server(self):
        command = (
            f"rasa run --enable-api -m \"{self.model_path}\" -p {self.port}"
        )
        # Redirect stdout and stderr to capture the output
        with open(self.log_file, "w") as output_file:
            self.server_process = subprocess.Popen(command, shell=True, stdout=output_file, stderr=subprocess.STDOUT)
            self.server_process.wait()  # Wait for the server process to finish


    def start_server(self):
        self.thread_pool.submit(self._start_server)

        # Wait for a brief moment to allow the server to start
        time.sleep(25)


    def stop_server(self):
        if self.server_process:
            self.server_process.terminate()
            self.server_process.wait()
            self.server_process = None
            self.thread_pool.shutdown(wait=True)
    

    def preprocess_text(self, text):
        # text to lower case and remove trailing and leading spaces
        preprocessed_text = text.lower().strip()
        # remove special characters, punctuation, and extra whitespaces
        preprocessed_text = re.sub(r'[^\w\s]', '', preprocessed_text).strip()
        return preprocessed_text


    def extract_intent(self, text):
        preprocessed_text = self.preprocess_text(text)
        url = f"http://localhost:{self.port}/model/parse"
        data = {
            "text": preprocessed_text
        }
        response = requests.post(url, json=data)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    

    def process_intent(self, intent_output):
        intent = intent_output["intent"]["name"]
        entities = {}
        for entity in intent_output["entities"]:
            entity_name = entity["entity"]
            entity_value = entity["value"]
            entities[entity_name] = entity_value
        
        return intent, entities