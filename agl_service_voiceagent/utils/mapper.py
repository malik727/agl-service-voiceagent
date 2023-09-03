from utils.config import get_config_value
from utils.common import load_json_file

class Intent2VSSMapper:
    def __init__(self):
        self.intent_map = load_json_file(get_config_value("intent_map_file", "Mapper")).get("intents", {})
        self.vss_signals = load_json_file(get_config_value("vss_signals_file", "Mapper")).get("signals", {})


    def map_intent_to_signal(self, intent_name):
        intent_data = self.intent_map.get(intent_name, None)
        if intent_data:
            signal_name = intent_data.get("signal", None)
            if signal_name:
                return self.vss_signals.get(signal_name, None)
        return None


    def perform_action(self, intent_name, action=None, value=None):
        vss_signal_data = self.map_intent_to_signal(intent_name)
        if vss_signal_data:
            if not action or action in vss_signal_data.get("actions", []):
                self.execute_action(vss_signal_data, action, value)
            else:
                print(f"Action '{action}' is not supported for this signal.")

        else:
            print(f"No mapping found for intent '{intent_name}'.")


    def execute_action(self, vss_signal_data, action, value=None):
        signal_name = vss_signal_data["signal"]
        default_action = vss_signal_data.get("default_action", None)
        default_value = vss_signal_data.get("default_value", None)

        # verify stuff and perform actions here

