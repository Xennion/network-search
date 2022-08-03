# NetworkSearch
A (work in progress) simple app to catalog and allow you to search your networks based on collecting and normalizing network data from the vendor devices directly.

## Basic Setup

Make copy of config-example.yml from root of project and put in your devices.

## Supported Network Devices

- paloalto_panos
- cisco_nxos
- juniper

## To run with docker in dev

```bash
docker build -t network-discovery .

docker run --rm -p 8000:80 -v /<YOUR_LOCAL_DB_LOCATION>/db:/db -v /<YOUR_CONFIG_FILE_LOCATION>/config.yml:/config.yml network-discovery
```

Then connect to web interface via http://localhost:8000
