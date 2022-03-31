import click
import json

from libs.network import NetworkDevice


@click.command()
@click.argument("device")
@click.argument("device_type")
@click.option("-u", "--username", prompt=True, help="device username")
@click.option("-p", "--password", prompt=True, hide_input=True, help="device password")
def main(device, device_type, username, password):
    """Connect to device and gather network information"""
    dev = NetworkDevice(device, device_type, username, password, datacenter="NA")
    data = dev.get_data()
    click.echo(json.dumps(data, indent=4))


if __name__ == "__main__":
    main()
