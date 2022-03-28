import re
from ipaddress import IPv4Interface

from schemas.network import NetworkSchema
from libs.common import ipv4_model


def get_networks(connection, datacenter) -> list[NetworkSchema]:
    final_network_data = []
    data_raw = connection.send_command("show interface logical")
    lines = data_raw.split("\n")

    for line in lines:
        filter = re.search(
            "([1-9][0-9]{0,3})\s+([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}/[0-9]{1,2})",
            line,
        )
        if not filter:
            continue

        vlan = int(filter[1])
        ip = IPv4Interface(filter[2])

        final_network_data.append(
            {
                "vlan": vlan,
                "description": "",  # todo - get description maybe?
                "datacenter": datacenter,
                "origin_device": connection.host,
                "gateway": filter[2].split("/")[0],
                **ipv4_model(ip),
            },
        )

    return final_network_data
