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
from typing import Text
from snips_inference_agl import SnipsNLUEngine

class SnipsInterface:
    """
    SnipsInterface is a class for interacting with the Snips Natural Language Understanding Engine (Snips NLU).
    """

    def __init__(self, model_path: Text):
        """
        Initialize the SnipsInterface instance with the provided Snips NLU model.

        Args:
            model_path (Text): The path to the Snips NLU model.
        """
        self.engine = SnipsNLUEngine.from_path(model_path)

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

    def extract_intent(self, text: Text):
        """
        Extract the intent from preprocessed text using the Snips NLU engine.

        Args:
            text (Text): The preprocessed input text.

        Returns:
            dict: The intent extraction result as a dictionary.
        """
        preprocessed_text = self.preprocess_text(text)
        result = self.engine.parse(preprocessed_text)
        return result
    
    def process_intent(self, intent_output):
        """
        Extract intent and slot values from Snips NLU output.

        Args:
            intent_output (dict): The intent extraction result from Snips NLU.

        Returns:
            tuple: A tuple containing the intent name (str) and a dictionary of intent actions (entity-value pairs).
        """
        intent_actions = {}
        intent = intent_output['intent']['intentName']
        slots = intent_output.get('slots', [])
        for slot in slots:
            action = slot['entity']
            value = slot['value']['value']
            intent_actions[action] = value

        return intent, intent_actions