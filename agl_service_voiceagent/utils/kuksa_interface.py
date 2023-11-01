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

import time
import json
import threading
from kuksa_client import KuksaClientThread
from agl_service_voiceagent.utils.config import get_config_value, get_logger

class KuksaInterface:
    """
    Kuksa Interface

    This class provides methods to initialize, authorize, connect, send values,
    check the status, and close the Kuksa client.
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        """
        Get the unique instance of the class.

        Returns:
            KuksaInterface: The instance of the class.
        """
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(KuksaInterface, cls).__new__(cls)
                cls._instance.init_client()
        return cls._instance
    

    def init_client(self):
        """
        Initialize the Kuksa client configuration.
        """
        # get config values
        self.ip = str(get_config_value("ip", "Kuksa"))
        self.port = str(get_config_value("port", "Kuksa"))
        self.insecure = get_config_value("insecure", "Kuksa")
        self.protocol = get_config_value("protocol", "Kuksa")
        self.token = get_config_value("token", "Kuksa")
        self.logger = get_logger()

        print(self.ip, self.port, self.insecure, self.protocol, self.token)

        # define class methods
        self.kuksa_client = None


    def get_kuksa_client(self):
        """
        Get the Kuksa client instance.

        Returns:
            KuksaClientThread: The Kuksa client instance.
        """
        return self.kuksa_client


    def get_kuksa_status(self):
        """
        Check the status of the Kuksa client connection.

        Returns:
            bool: True if the client is connected, False otherwise.
        """
        if self.kuksa_client:
            return self.kuksa_client.checkConnection()
        return False


    def connect_kuksa_client(self):
        """
        Connect and start the Kuksa client.
        """
        try:
            with self._lock:
                if self.kuksa_client is None:
                    self.kuksa_client = KuksaClientThread({
                        "ip": self.ip,
                        "port": self.port,
                        "insecure": self.insecure,
                        "protocol": self.protocol,
                    })
                    self.kuksa_client.start()
                    time.sleep(2)  # Give the thread time to start

                if not self.get_kuksa_status():
                    print("[-] Error: Connection to Kuksa server failed.")
                    self.logger.error("Connection to Kuksa server failed.")
                else:
                    print("[+] Connection to Kuksa established.")
                    self.logger.info("Connection to Kuksa established.")

        except Exception as e:
            print("[-] Error: Connection to Kuksa server failed. ", str(e))
            self.logger.error(f"Connection to Kuksa server failed. {str(e)}")

    
    def authorize_kuksa_client(self):
        """
        Authorize the Kuksa client with the provided token.
        """
        if self.kuksa_client:
            response = self.kuksa_client.authorize(self.token)
            response = json.loads(response)
            if "error" in response:
                error_message = response.get("error", "Unknown error")
                print(f"[-] Error: Authorization failed. {error_message}")
                self.logger.error(f"Authorization failed. {error_message}")
            else:
                print("[+] Kuksa client authorized successfully.")
                self.logger.info("Kuksa client authorized successfully.")
        else:
            print("[-] Error: Kuksa client is not initialized. Call `connect_kuksa_client` first.")
            self.logger.error("Kuksa client is not initialized. Call `connect_kuksa_client` first.")


    def send_values(self, path=None, value=None):
        """
        Send values to the Kuksa server.

        Args:
            path (str): The path to the value.
            value (str): The value to be sent.
        Returns:
            bool: True if the value was set, False otherwise.
        """
        result = False
        if self.kuksa_client is None:
            print(f"[-] Error: Failed to send value '{value}' to Kuksa. Kuksa client is not initialized.")
            self.logger.error(f"Failed to send value '{value}' to Kuksa. Kuksa client is not initialized.")
            return

        if self.get_kuksa_status():
            try:
                response = self.kuksa_client.setValue(path, value)
                response = json.loads(response)
                if not "error" in response:
                    print(f"[+] Value '{value}' sent to Kuksa successfully.")
                    result = True
                else:
                    error_message = response.get("error", "Unknown error")
                    print(f"[-] Error: Failed to send value '{value}' to Kuksa. {error_message}")
                    self.logger.error(f"Failed to send value '{value}' to Kuksa. {error_message}")
            
            except Exception as e:
                print(f"[-] Error: Failed to send value '{value}' to Kuksa. ", str(e))
                self.logger.error(f"Failed to send value '{value}' to Kuksa. {str(e)}")

        else:
            print(f"[-] Error: Failed to send value '{value}' to Kuksa. Connection to Kuksa failed.")
            self.logger.error(f"Failed to send value '{value}' to Kuksa. Connection to Kuksa failed.")

        return result
    

    def get_value(self, path=None):
        """
        Get values from the Kuksa server.

        Args:
            path (str): The path to the value.
        Returns:
            str: The value if the path is valid, None otherwise.
        """
        result = None
        if self.kuksa_client is None:
            print(f"[-] Error: Failed to get value at path '{path}' from Kuksa. Kuksa client is not initialized.")
            self.logger.error(f"Failed to get value at path '{path}' from Kuksa. Kuksa client is not initialized.")
            return

        if self.get_kuksa_status():
            try:
                response = self.kuksa_client.getValue(path)
                response = json.loads(response)
                if not "error" in response:
                    result = response.get("data", None)
                    result = result.get("dp", None)
                    result = result.get("value", None)
                    
                else:
                    error_message = response.get("error", "Unknown error")
                    print(f"[-] Error: Failed to get value at path '{path}' from Kuksa. {error_message}")
                    self.logger.error(f"Failed to get value at path '{path}' from Kuksa. {error_message}")
            
            except Exception as e:
                print(f"[-] Error: Failed to get value at path '{path}' from Kuksa. ", str(e))
                self.logger.error(f"Failed to get value at path '{path}' from Kuksa. {str(e)}")

        else:
            print(f"[-] Error: Failed to get value at path '{path}' from Kuksa. Connection to Kuksa failed.")
            self.logger.error(f"Failed to get value at path '{path}' from Kuksa. Connection to Kuksa failed.")

        return result
    

    def close_kuksa_client(self):
        """
        Close and stop the Kuksa client.
        """
        try:
            with self._lock:
                if self.kuksa_client:
                    self.kuksa_client.stop()
                    self.kuksa_client = None
                    print("[+] Kuksa client stopped.")
                    self.logger.info("Kuksa client stopped.")
        except Exception as e:
            print("[-] Error: Failed to close Kuksa client. ", str(e))
            self.logger.error(f"Failed to close Kuksa client. {str(e)}")