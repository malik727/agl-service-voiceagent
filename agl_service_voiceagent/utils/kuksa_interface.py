from kuksa_client import KuksaClientThread
from utils.config import get_config_value

class KuksaInterface:
    def __init__(self):
        # get config values
        self.ip = get_config_value("ip", "Kuksa")
        self.port = get_config_value("port", "Kuksa")
        self.insecure = get_config_value("insecure", "Kuksa")
        self.protocol = get_config_value("protocol", "Kuksa")
        self.token = get_config_value("token", "Kuksa")

        # define class methods
        self.kuksa_client = None


    def get_kuksa_client(self):
        return self.kuksa_client
    

    def get_kuksa_status(self):
        if self.kuksa_client:
            return self.kuksa_client.checkConnection()

        return False


    def connect_kuksa_client(self):
        try:
            self.kuksa_client = KuksaClientThread({
                "ip": self.ip,
                "port": self.port,
                "insecure": self.insecure,
                "protocol": self.protocol,
            })
            self.kuksa_client.authorize(self.token)

        except Exception as e:
            print("Error: ", e)
    

    def send_values(self, Path=None, Value=None):
        if self.kuksa_client is None:
            print("Error: Kuksa client is not initialized.")

        if self.get_kuksa_status():
            self.kuksa_client.setValue(Path, Value)

        else:
            print("Error: Connection to Kuksa failed.")
