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
import configparser

# Get the absolute path to the directory of the current script
current_dir = os.path.dirname(os.path.abspath(__file__))
# Construct the path to the config.ini file located in the base directory
config_path = os.path.join(current_dir, '..', 'config.ini')

config = configparser.ConfigParser()
config.read(config_path)

def update_config_value(value, key, group="General"):
    config.set(group, key, value)
    with open(config_path, 'w') as configfile:
        config.write(configfile)

def get_config_value(key, group="General"):
    return config.get(group, key)
