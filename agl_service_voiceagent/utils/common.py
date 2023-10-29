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
import uuid
import json


def add_trailing_slash(path):
    """
    Adds a trailing slash to a path if it does not already have one.
    """
    if path and not path.endswith('/'):
        path += '/'
    return path


def generate_unique_uuid(length):
    """
    Generates a unique ID of specified length.
    """
    unique_id = str(uuid.uuid4().int)
    # Ensure the generated ID is exactly 'length' digits by taking the last 'length' characters
    unique_id = unique_id[-length:]
    return unique_id


def load_json_file(file_path):
    """
    Loads a JSON file and returns the data.
    """
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        raise ValueError(f"File '{file_path}' not found.")


def delete_file(file_path):
    """
    Deletes a file if it exists.
    """
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except Exception as e:
            print(f"Error deleting '{file_path}': {e}")
    else:
        print(f"File '{file_path}' does not exist.")


def words_to_number(words):
    """
    Converts a string of words to a number.
    """
    word_to_number = {
        'one': 1,
        'two': 2,
        'three': 3,
        'four': 4,
        'five': 5,
        'six': 6,
        'seven': 7,
        'eight': 8,
        'nine': 9,
        'ten': 10,
        'eleven': 11,
        'twelve': 12,
        'thirteen': 13,
        'fourteen': 14,
        'fifteen': 15,
        'sixteen': 16,
        'seventeen': 17,
        'eighteen': 18,
        'nineteen': 19,
        'twenty': 20,
        'thirty': 30,
        'forty': 40,
        'fourty': 40,
        'fifty': 50,
        'sixty': 60,
        'seventy': 70,
        'eighty': 80,
        'ninety': 90
    }

    # Split the input words and initialize total and current number
    words = words.split()

    if len(words) == 1:
        if words[0] in ["zero", "min", "minimum"]:
            return 0
        
        elif words[0] in ["half", "halfway"]:
            return 50
        
        elif words[0] in ["max", "maximum", "full", "fully", "completely", "hundred"]:
            return 100


    total = 0
    current_number = 0

    for word in words:
        if word in word_to_number:
            current_number += word_to_number[word]
        elif word == 'hundred':
            current_number *= 100
        else:
            total += current_number
            current_number = 0

    total += current_number

    # we return number in str format because kuksa expects str input
    return str(total) or None