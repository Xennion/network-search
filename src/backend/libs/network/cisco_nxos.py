from ipaddress import IPv4Interface
from json import loads

from libs.common import ipv4_model


def get_vlans(connection, datacenter):
    vlan_data = []
    vlan_data_json = loads(connection.send_command("show vlan | json-pretty"))
    parsed_vlans = vlan_data_json["TABLE_vlanbrief"]["ROW_vlanbrief"]
    for vlan in parsed_vlans:
        vlan_data.append(
            {
                "vlan": vlan["vlanshowbr-vlanid"],
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
    for vlan in vlans:
        ip_data = loads(
            connection.send_command(f"show ip int vlan {vlan['vlan']} | json-pretty")
        )
        parsed_keys = {
            key.replace("-", "_"): value
            for key, value in ip_data["TABLE_intf"]["ROW_intf"].items()
        }
        if parsed_keys["ip_disabled"] == "TRUE":
            continue
        if not "prefix" in parsed_keys:
            final_network_data.append(vlan)
            continue
        ipv4_interface = IPv4Interface(
            f"{parsed_keys['prefix']}/{parsed_keys['masklen']}"
        )
        vlan.update(ipv4_model(ipv4_interface))
        final_network_data.append(vlan)
    return final_network_data
