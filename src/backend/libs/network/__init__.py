from netmiko import ConnectHandler

from . import juniper, paloalto_panos, cisco_nxos


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
        connection = ConnectHandler(**device)

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
