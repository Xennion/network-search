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
    logger.trace(f"Collected {len(vlans)} vlans from {connection.host}")
    network_command = "show ip int vrf all | json"
    logger.trace(f"Running command '{network_command}' on {connection.host}")

    ip_data = loads(connection.send_command(network_command))
    ip_data = ip_data["TABLE_intf"]["ROW_intf"]

    ip_data = [net for net in ip_data if "Vlan" in net["intf-name"]]
    for vlan in vlans:
        vlan_match = [
            net for net in ip_data if f"Vlan{vlan['vlan']}" == net["intf-name"]
        ]
        if not len(vlan_match) or not "prefix" in vlan_match[0]:
            final_network_data.append(vlan)
            continue
        vlan_match = vlan_match[0]
        ipv4_interface = IPv4Interface(
            f"{vlan_match['prefix']}/{vlan_match['masklen']}"
        )
        vlan.update(ipv4_model(ipv4_interface))
        final_network_data.append(vlan)
    logger.trace(f"Collected {len(final_network_data)} networks from {connection.host}")
    return final_network_data
