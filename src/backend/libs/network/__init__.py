from netmiko import ConnectHandler
from loguru import logger
import sys
import os

from . import juniper, paloalto_panos, cisco_nxos

logger.remove(0)
logger.add(
    sys.stderr,
    level=os.environ.get("LOGLEVEL").upper() if os.environ.get("LOGLEVEL") else "DEBUG",
)


class NetworkDevice:
    def __init__(
        self,
        host: str,
        device_type: str,
        username: str,
        password: str,
        datacenter: str,
    ) -> None:
        self.__host = host
        self.__device_type = device_type
        self.__username = username
        self.__password = password
        self.__datacenter = datacenter

    def get_data(self):
        device = {
            "host": self.__host,
            "device_type": self.__device_type,
            "username": self.__username,
            "password": self.__password,
        }
        logger.trace(f"Connecting to {self.__host} device type '{self.__device_type}'")
        connection = ConnectHandler(**device)
        logger.trace(f"Successfully connected to {self.__host}")

        if self.__device_type == "juniper":
            result = juniper.get_networks(connection, self.__datacenter)
        elif self.__device_type == "paloalto_panos":
            result = paloalto_panos.get_networks(connection, self.__datacenter)
        elif self.__device_type == "cisco_nxos":
            result = cisco_nxos.get_networks(connection, self.__datacenter)
        else:
            result = []

        connection.disconnect()

        return result
