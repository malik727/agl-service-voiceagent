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

import re
import time
import requests
import subprocess
from concurrent.futures import ThreadPoolExecutor

class RASAInterface:
    """
    RASAInterface is a class for interfacing with a Rasa NLU server to extract intents and entities from text input.
    """

    def __init__(self, port, model_path, log_dir, max_threads=5):
        """
        Initialize the RASAInterface instance with the provided parameters.

        Args:
            port (int): The port number on which the Rasa NLU server will run.
            model_path (str): The path to the Rasa NLU model.
            log_dir (str): The directory where server logs will be saved.
            max_threads (int, optional): The maximum number of concurrent threads (default is 5).
        """
        self.port = port
        self.model_path = model_path
        self.max_threads = max_threads
        self.server_process = None
        self.thread_pool = ThreadPoolExecutor(max_workers=max_threads)
        self.log_file = log_dir+"rasa_server.log"


    def _start_server(self):
        """
        Start the Rasa NLU server in a subprocess and redirect its output to the log file.
        """
        command = (
            f"rasa run --enable-api -m \"{self.model_path}\" -p {self.port}"
        )
        # Redirect stdout and stderr to capture the output
        with open(self.log_file, "w") as output_file:
            self.server_process = subprocess.Popen(command, shell=True, stdout=output_file, stderr=subprocess.STDOUT)
            self.server_process.wait()  # Wait for the server process to finish


    def start_server(self):
        """
        Start the Rasa NLU server in a separate thread and wait for it to initialize.
        """
        self.thread_pool.submit(self._start_server)

        # Wait for a brief moment to allow the server to start
        time.sleep(25)


    def stop_server(self):
        """
        Stop the Rasa NLU server and shut down the thread pool.
        """
        if self.server_process:
            self.server_process.terminate()
            self.server_process.wait()
            self.server_process = None
            self.thread_pool.shutdown(wait=True)
    

    def preprocess_text(self, text):
        """
        Preprocess the input text by converting it to lowercase, removing leading/trailing spaces,
        and removing special characters and punctuation.

        Args:
            text (str): The input text to preprocess.

        Returns:
            str: The preprocessed text.
        """
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
        """
        Extract intents and entities from preprocessed text using the Rasa NLU server.

        Args:
            text (str): The preprocessed input text.

        Returns:
            dict: Intent and entity extraction result as a dictionary.
        """
        intent = intent_output["intent"]["name"]
        entities = {}
        for entity in intent_output["entities"]:
            entity_name = entity["entity"]
            entity_value = entity["value"]
            entities[entity_name] = entity_value
        
        return intent, entities