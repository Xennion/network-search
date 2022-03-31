from ipaddress import IPv4Address, IPv4Interface
from copy import deepcopy


def merge_networks(current_networks, new_networks):
    merged_networks = deepcopy(current_networks)

    # search and update existing networks
    for new_network in new_networks:
        existing = [
            network
            for network in merged_networks
            if network["vlan"] == new_network["vlan"]
        ]
        if existing:
            existing = existing[0]
            if not existing["network"]:
                existing["network"] = new_network["network"]
                existing["gateway"] = new_network["gateway"]
                existing["network_address"] = new_network["network_address"]
                existing["broadcast_address"] = new_network["broadcast_address"]
                existing["netmask"] = new_network["netmask"]
                existing["bitmask"] = new_network["bitmask"]
                existing["first_usable_ip"] = new_network["first_usable_ip"]
                existing["last_usable_ip"] = new_network["last_usable_ip"]
                existing["origin_device"] = new_network["origin_device"]
        else:
            merged_networks.append(new_network)

    # create a unique id for each network
    for network in merged_networks:
        network["id"] = f"{network['datacenter']}:{network['vlan']}"

    return merged_networks


def ipv4_model(ipv4_interface: IPv4Interface):
    return {
        "network": str(ipv4_interface.network),
        "network_address": str(ipv4_interface.network).split("/")[0],
        "broadcast_address": str(ipv4_interface.network.broadcast_address),
        "netmask": str(ipv4_interface.network.netmask),
        "bitmask": int(ipv4_interface.network._prefixlen),
        "first_usable_ip": str(
            IPv4Address(int(ipv4_interface.network.network_address) + 1)
        ),
        "last_usable_ip": str(
            IPv4Address(int(ipv4_interface.network.broadcast_address) - 1)
        ),
    }
