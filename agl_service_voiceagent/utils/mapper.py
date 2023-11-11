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

import json
from agl_service_voiceagent.utils.config import get_config_value, get_logger
from agl_service_voiceagent.utils.common import load_json_file, words_to_number


class Intent2VSSMapper:
    """
    Intent2VSSMapper is a class that facilitates the mapping of natural language intent to
    corresponding vehicle signal specifications (VSS) for automated vehicle control systems.
    """

    def __init__(self):
        """
        Initializes the Intent2VSSMapper class by loading Intent-to-VSS signal mappings
        and VSS signal specifications from external configuration files.
        """
        intents_vss_map_file = get_config_value("intents_vss_map", "Mapper")
        vss_signals_spec_file = get_config_value("vss_signals_spec", "Mapper")
        self.intents_vss_map = load_json_file(intents_vss_map_file).get("intents", {})
        self.vss_signals_spec = load_json_file(vss_signals_spec_file).get("signals", {})
        self.logger = get_logger()

        if not self.validate_signal_spec_structure():
            raise ValueError("[-] Invalid VSS signal specification structure.")

    def validate_signal_spec_structure(self):
        """
        Validates the structure of the VSS signal specification data.
        """

        signals = self.vss_signals_spec

        # Iterate over each signal in the 'signals' dictionary
        for signal_name, signal_data in signals.items():
            # Check if the required keys are present in the signal data
            if not all(key in signal_data for key in ['default_value', 'default_change_factor', 'actions', 'values', 'default_fallback', 'value_set_intents']):
                print(f"[-] {signal_name}: Missing required keys in signal data.")
                self.logger.error(f"{signal_name}: Missing required keys in signal data.")
                return False

            actions = signal_data['actions']

            # Check if 'actions' is a dictionary with at least one action
            if not isinstance(actions, dict) or not actions:
                print(f"[-] {signal_name}: Invalid 'actions' key in signal data. Must be an object with at least one action.")
                self.logger.error(f"{signal_name}: Invalid 'actions' key in signal data. Must be an object with at least one action.")
                return False

            # Check if the actions match the allowed actions ["set", "increase", "decrease"]
            for action in actions.keys():
                if action not in ["set", "increase", "decrease"]:
                    print(f"[-] {signal_name}: Invalid action in signal data. Allowed actions: ['set', 'increase', 'decrease']")
                    self.logger.error(f"{signal_name}: Invalid action in signal data. Allowed actions: ['set', 'increase', 'decrease']")
                    return False

            # Check if the 'synonyms' list is present for each action and is either a list or None
            for action_data in actions.values():
                synonyms = action_data.get('synonyms')
                if synonyms is not None and (not isinstance(synonyms, list) or not all(isinstance(synonym, str) for synonym in synonyms)):
                    print(f"[-] {signal_name}: Invalid 'synonyms' value in signal data. Must be a list of strings.")
                    self.logger.error(f"{signal_name}: Invalid 'synonyms' value in signal data. Must be a list of strings.")
                    return False

            values = signal_data['values']

            # Check if 'values' is a dictionary with the required keys
            if not isinstance(values, dict) or not all(key in values for key in ['ranged', 'start', 'end', 'ignore', 'additional']):
                print(f"[-] {signal_name}: Invalid 'values' key in signal data. Required keys: ['ranged', 'start', 'end', 'ignore', 'additional']")
                self.logger.error(f"{signal_name}: Invalid 'values' key in signal data. Required keys: ['ranged', 'start', 'end', 'ignore', 'additional']")
                return False

            # Check if 'ranged' is a boolean
            if not isinstance(values['ranged'], bool):
                print(f"[-] {signal_name}: Invalid 'ranged' value in signal data. Allowed values: [true, false]")
                self.logger.error(f"{signal_name}: Invalid 'ranged' value in signal data. Allowed values: [true, false]")
                return False

            default_fallback = signal_data['default_fallback']

            # Check if 'default_fallback' is a boolean
            if not isinstance(default_fallback, bool):
                print(f"[-] {signal_name}: Invalid 'default_fallback' value in signal data. Allowed values: [true, false]")
                self.logger.error(f"{signal_name}: Invalid 'default_fallback' value in signal data. Allowed values: [true, false]")
                return False

        # If all checks pass, the self.vss_signals_spec structure is valid
        return True


    def map_intent_to_signal(self, intent_name):
        """
        Maps an intent name to the corresponding VSS signals and their specifications.

        Args:
            intent_name (str): The name of the intent to be mapped.

        Returns:
            dict: A dictionary containing VSS signals as keys and their specifications as values.
        """
    
        intent_data = self.intents_vss_map.get(intent_name, None)
        result = {}
        if intent_data:
            signals = intent_data.get("signals", [])

            for signal in signals:
                signal_info = self.vss_signals_spec.get(signal, {})
                if signal_info:
                    result.update({signal: signal_info})
        
        return result


    def parse_intent(self, intent_name, intent_slots = [], req_id = ""):
        """
        Parses an intent, extracting relevant VSS signals, actions, modifiers, and values
        based on the intent and its associated slots.

        Args:
            intent_name (str): The name of the intent to be parsed.
            intent_slots (list): A list of dictionaries representing intent slots.

        Returns:
            list: A list of dictionaries describing actions and signal-related details for execution.

        Note:
            - If no relevant VSS signals are found for the intent, an empty list is returned.
            - If no specific action or modifier is determined, default values are used.
        """
        vss_signal_data = self.map_intent_to_signal(intent_name)
        execution_list = []
        for signal_name, signal_data in vss_signal_data.items():
            action = self.determine_action(signal_data, intent_slots)
            modifier = self.determine_modifier(signal_data, intent_slots)
            value = self.determine_value(signal_data, intent_slots)
            original_value = value

            if value != None and not self.verify_value(signal_data, value):
                value = None

            change_factor = signal_data["default_change_factor"]
            log_change_factor = change_factor

            if action in ["increase", "decrease"]:
                if value and modifier == "to":
                    execution_list.append({"action": action, "signal": signal_name, "value": str(value)})
                
                elif value and modifier == "by":
                    execution_list.append({"action": action, "signal": signal_name, "factor": str(value)})
                    log_change_factor = value
                
                elif value:
                    execution_list.append({"action": action, "signal": signal_name, "value": str(value)})

                elif signal_data["default_fallback"]:
                    execution_list.append({"action": action, "signal": signal_name, "factor": str(change_factor)})

            # if no value found set the default value
            if value == None and signal_data["default_fallback"]:
                value = signal_data["default_value"]

            if action == "set" and value != None:
                execution_list.append({"action": action, "signal": signal_name, "value": str(value)})

            
            # log the mapping data
            mapping_log_data = {
                "Signal": signal_name,
                "Action": action,
                "Modifier": modifier,
                "OriginalValue": original_value,
                "ProcessedValue": value,
                "ChangeFactor": log_change_factor
            }
            mapping_log_data = json.dumps(mapping_log_data)
            print(f"[+] Mapper Log: {mapping_log_data}")
            self.logger.info(f"[ReqID#{req_id}] Mapper Log: {mapping_log_data}")
                    
        
        return execution_list
        

    def determine_action(self, signal_data, intent_slots):
        """
        Determines the action (e.g., set, increase, decrease) based on the intent slots
        and VSS signal data.

        Args:
            signal_data (dict): The specification data for a VSS signal.
            intent_slots (list): A list of dictionaries representing intent slots.

        Returns:
            str: The determined action or None if no action can be determined.
        """
        action_res = None
        for intent_slot in intent_slots:
           for action, action_data in signal_data["actions"].items():
                if intent_slot["name"] in action_data["intents"] and intent_slot["value"] in action_data["synonyms"]:
                    action_res = action
                    break
        
        return action_res
    

    def determine_modifier(self, signal_data, intent_slots):
        """
        Determines the modifier (e.g., 'to' or 'by') based on the intent slots
        and VSS signal data.

        Args:
            signal_data (dict): The specification data for a VSS signal.
            intent_slots (list): A list of dictionaries representing intent slots.

        Returns:
            str: The determined modifier or None if no modifier can be determined.
        """
        modifier_res = None
        for intent_slot in intent_slots:
           for _, action_data in signal_data["actions"].items():
                intent_val = intent_slot["value"]
                if "modifier_intents" in action_data and intent_slot["name"] in action_data["modifier_intents"] and ("to" in intent_val or "by" in intent_val):
                    modifier_res = "to" if "to" in intent_val else "by" if "by" in intent_val else None
                    break
        
        return modifier_res


    def determine_value(self, signal_data, intent_slots):
        """
        Determines the value associated with the intent slot, considering the data type
        and converting it to a numeric string representation if necessary.

        Args:
            signal_data (dict): The specification data for a VSS signal.
            intent_slots (list): A list of dictionaries representing intent slots.

        Returns:
            str: The determined value or None if no value can be determined.
        """
        result  = None
        for intent_slot in intent_slots:
           for value, value_data in signal_data["value_set_intents"].items():
                if intent_slot["name"] == value:
                    result = intent_slot["value"]

                    if value_data["datatype"] == "number":
                        result = words_to_number(result) # we assume our model will always return a number in words
        
        # the value should always returned as str because Kuksa expects str values
        return str(result) if result != None else None
    

    def verify_value(self, signal_data, value):
        """
        Verifies that the value is valid based on the VSS signal data.

        Args:
            signal_data (dict): The specification data for a VSS signal.
            value (str): The value to be verified.

        Returns:
            bool: True if the value is valid, False otherwise.
        """
        value = int(value) if value.isnumeric() else float(value) if value.replace('.', '', 1).isnumeric() else value

        if value in signal_data["values"]["ignore"]:
            return False
        
        elif signal_data["values"]["ranged"] and isinstance(value, (int, float)):
            return value >= signal_data["values"]["start"] and value <= signal_data["values"]["end"]
        
        else:
            return value in signal_data["values"]["additional"]
