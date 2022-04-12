import re
from ipaddress import IPv4Interface
from loguru import logger
from schemas.network import NetworkSchema

from libs.common import ipv4_model


def get_vlans(connection, datacenter) -> list[NetworkSchema]:
    vlan_command = 'show vlan brief'
    logger.trace(f"Running command '{vlan_command}' on {connection.host}")
    vlan_data_raw = connection.send_command(vlan_command)
    vlan_lines = vlan_data_raw.split('\n')
    vlan_data = []

    for line in vlan_lines:
        vlan = re.search("^(\d{1,4})\s+(\S+)", line)
        if not vlan: continue
        vlan_data.append(
            {
                "vlan": int(vlan.group(1)),
                "description": vlan.group(2),
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

def get_networks(connection, datacenter) -> list[NetworkSchema]:
    vlans = get_vlans(connection, datacenter)
    logger.trace(f"Collected {len(vlans)} vlans from {connection.host}")
    network_command = 'show ip int vrf all'
    logger.trace(f"Running command '{network_command}' on {connection.host}")
    ip_data_raw = connection.send_command(network_command)
    final_network_data = []
    for vlan in vlans:
        vlan_match = re.search(rf'(^Vlan{vlan["vlan"]}\b).+\n.+?subnet: (?=\d)(.+?(?= route))', ip_data_raw, re.MULTILINE)
        if not vlan_match: continue
        ipv4_interface = IPv4Interface(vlan_match.group(2))
        vlan.update(ipv4_model(ipv4_interface))
        final_network_data.append(vlan)
    logger.trace(f"Collected {len(final_network_data)} networks from {connection.host}")
    return final_network_data