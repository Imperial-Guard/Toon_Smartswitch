# Toon Smartswitch Component
This is a Custom Component for Home-Assistant (https://home-assistant.io).
The code is based on the TOON Smart Meter Sensor Component from Cyberjunky (https://github.com/cyberjunky/home-assistant-toon_smartmeter/blob/master/info.md)
You can read and control a Z-Wave Fibaro Wall Plug (https://www.fibaro.com/en/products/wall-plug/) from the meteradapter connected to a rooted TOON thermostat, the Fibaro Wall Plug must be paired to a TOON thermostat.

## Installation

### Manual
- Copy directory `toon_smartswitch` to your `<config dir>/custom_components` directory.
- Configure with config below.
- Restart Home-Assistant.

## Usage
To use this component in your installation, add the following to your `configuration.yaml` file:

```yaml
# Example configuration.yaml entry

sensor:
  - platform: toon_smartswitch
    host: IP_ADDRESS
    port: 10080
    scan_interval: 10
    resources:
    - elecusageflowfib
    - elecusagecntfib
```

Configuration variables:

- **host** (*Required*): The IP address on which the TOON can be reached.
- **port** (*Optional*): Port used by your TOON. (default = 10080)
- **scan_interval** (*Optional*): Number of seconds between polls. (default = 10)
- **resources** (*Required*): This section tells the component which values to display.
