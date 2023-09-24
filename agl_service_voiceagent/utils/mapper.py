from agl_service_voiceagent.utils.config import get_config_value
from agl_service_voiceagent.utils.common import load_json_file


class Intent2VSSMapper:
    def __init__(self):
        intents_vss_map_file = get_config_value("intents_vss_map", "Mapper")
        vss_signals_spec_file = get_config_value("vss_signals_spec", "Mapper")
        self.intents_vss_map = load_json_file(intents_vss_map_file).get("intents", {})
        self.vss_signals_spec = load_json_file(vss_signals_spec_file).get("signals", {})


    def map_intent_to_signal(self, intent_name):
        intent_data = self.intents_vss_map.get(intent_name, None)
        if intent_data:
            result = []
            signals = intent_data.get("signals", [])

            for signal in signals:
                signal_info = self.vss_signals_spec.get(signal, {})
                if signal_info:
                    result.append(signal_info)

                return result
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

