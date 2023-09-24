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
    def __init__(self, model_path: Text):
        self.engine = SnipsNLUEngine.from_path(model_path)

    def preprocess_text(self, text):
        # text to lower case and remove trailing and leading spaces
        preprocessed_text = text.lower().strip()
        # remove special characters, punctuation, and extra whitespaces
        preprocessed_text = re.sub(r'[^\w\s]', '', preprocessed_text).strip()
        return preprocessed_text

    def extract_intent(self, text: Text):
        preprocessed_text = self.preprocess_text(text)
        result = self.engine.parse(preprocessed_text)
        return result
    
    def process_intent(self, intent_output):
        intent_actions = {}
        intent = intent_output['intent']['intentName']
        slots = intent_output.get('slots', [])
        for slot in slots:
            action = slot['entity']
            value = slot['value']['value']
            intent_actions[action] = value

        return intent, intent_actions