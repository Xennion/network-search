from ipaddress import IPv4Interface
from json import loads
from loguru import logger

from libs.common import ipv4_model


def get_vlans(connection, datacenter):
    vlan_data = []
    vlan_command = "show vlan | json"
    logger.trace(f"Running command '{vlan_command}' on {connection.host}")
    vlan_data_json = loads(connection.send_command(vlan_command))
    parsed_vlans = vlan_data_json["TABLE_vlanbrief"]["ROW_vlanbrief"]
    for vlan in parsed_vlans:
        vlan_data.append(
            {
                "vlan": int(vlan["vlanshowbr-vlanid"]),
                "description": vlan["vlanshowbr-vlanname"],
                "datacenter": datacenter,
                "origin_device": connection.host,
                "network": "",
                "gateway": "",
                "network_address": "",
                "broadcast_address": "",
                "netmask": "",
                "bitmask": None,
                "first_usable_ip": "",
                "last_usable_ip": "",
            }
        )
    return vlan_data


def get_networks(connection, datacenter):
    final_network_data = []
    vlans = get_vlans(connection, datacenter)

    ip_data = loads(connection.send_command(f"show ip int vrf all | json"))
    ip_data = ip_data["TABLE_intf"]["ROW_intf"]
    import json

    ip_data = [net for net in ip_data if "Vlan" in net["intf-name"]]
    print(json.dumps(ip_data, indent=4))

    # for vlan in vlans:

    #     parsed_keys = {
    #         key.replace("-", "_"): value
    #         for key, value in ip_data["TABLE_intf"]["ROW_intf"].items()
    #     }

    #     if parsed_keys["ip_disabled"] == "TRUE":
    #         continue
    #     if not "prefix" in parsed_keys:
    #         final_network_data.append(vlan)
    #         continue
    #     ipv4_interface = IPv4Interface(
    #         f"{parsed_keys['prefix']}/{parsed_keys['masklen']}"
    #     )
    #     vlan.update(ipv4_model(ipv4_interface))
    #     final_network_data.append(vlan)
    # return final_network_data
