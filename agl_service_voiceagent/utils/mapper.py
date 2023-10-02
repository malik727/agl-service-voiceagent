from utils.config import get_config_value
from utils.common import load_json_file, words_to_number


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


    def parse_intent(self, intent_name, intent_slots = []):
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
            change_factor = signal_data["default_change_factor"]

            if action in ["increase", "decrease"]:
                if value and modifier == "to":
                    execution_list.append({"action": action, "signal": signal_name, "value": value})
                
                elif value and modifier == "by":
                    execution_list.append({"action": action, "signal": signal_name, "factor": value})
                
                elif value:
                    execution_list.append({"action": action, "signal": signal_name, "value": value})

                elif signal_data["default_fallback"]:
                    execution_list.append({"action": action, "signal": signal_name, "factor": change_factor})

            # if no value found set the default value
            if value == None and signal_data["default_fallback"]:
                value = signal_data["default_value"]

            if action == "set" and value != None:
                execution_list.append({"action": action, "signal": signal_name, "value": value})
                    
        
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
