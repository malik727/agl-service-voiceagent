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
    if path and not path.endswith('/'):
        path += '/'
    return path


def generate_unique_uuid(length):
    unique_id = str(uuid.uuid4().int)
    # Ensure the generated ID is exactly 'length' digits by taking the last 'length' characters
    unique_id = unique_id[-length:]
    return unique_id


def load_json_file(file_path):
        try:
            with open(file_path, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            raise ValueError(f"File '{file_path}' not found.")


def delete_file(file_path):
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except Exception as e:
            print(f"Error deleting '{file_path}': {e}")
    else:
        print(f"File '{file_path}' does not exist.")