"""
Support for reading SmartMeter data through Eneco's Toon thermostats.
Only works for rooted Toon.

configuration.yaml

sensor:
  - platform: toon_smartswitch
    host: IP_ADDRESS
    port: 10080
    scan_interval: 10
    resources:
      - elecusageflowfib
      - elecusagecntfib
"""
import logging
from datetime import timedelta
import requests
import voluptuous as vol

from homeassistant.components.sensor import PLATFORM_SCHEMA
import homeassistant.helpers.config_validation as cv
from homeassistant.const import (
    CONF_HOST, CONF_PORT, CONF_SCAN_INTERVAL, CONF_RESOURCES)
from homeassistant.util import Throttle
from homeassistant.helpers.entity import Entity

_LOGGER = logging.getLogger(__name__)

BASE_URL = 'http://{0}:{1}{2}'
MIN_TIME_BETWEEN_UPDATES = timedelta(seconds=10)

SENSOR_PREFIX = 'Toon '

SENSOR_TYPES = {
    'elecusageflowfib': ['Fibaro Plug Power', 'W', 'mdi:flash'],
    'elecusagecntfib': ['Fibaro Power Use Cnt', 'kWh', 'mdi:flash'],
}

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_HOST): cv.string,
    vol.Optional(CONF_PORT, default=10800): cv.positive_int,
    vol.Required(CONF_RESOURCES, default=[]):
        vol.All(cv.ensure_list, [vol.In(SENSOR_TYPES)]),
})


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Setup the Toon smartmeter sensors."""
    scan_interval = config.get(CONF_SCAN_INTERVAL)
    host = config.get(CONF_HOST)
    port = config.get(CONF_PORT)

    try:
        data = ToonData(host, port)
    except requests.exceptions.HTTPError as error:
        _LOGGER.error(error)
        return False

    entities = []

    for resource in config[CONF_RESOURCES]:
        sensor_type = resource.lower()

        if sensor_type not in SENSOR_TYPES:
            SENSOR_TYPES[sensor_type] = [
                sensor_type.title(), '', 'mdi:flash']

        entities.append(ToonSmartMeterSensor(data, sensor_type))

    add_entities(entities)


# pylint: disable=abstract-method
class ToonData(object):
    """Representation of a Toon thermostat."""

    def __init__(self, host, port):
        """Initialize the thermostat."""
        self._host = host
        self._port = port
        self.data = None

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self):
        """Update the data from the thermostat."""
        try:
            self.data = requests.get(BASE_URL.format(self._host, self._port, '/hdrv_zwave?action=getDevices.json'), timeout=5).json()
            _LOGGER.debug("Data = %s", self.data)
        except requests.exceptions.RequestException:
            _LOGGER.error("Error occurred while fetching data.")
            self.data = None
            return False

 
class ToonSmartMeterSensor(Entity):
    """Representation of a SmartMeter connected to Toon."""

    def __init__(self, data, sensor_type):
        """Initialize the sensor."""
        self.data = data
        self.type = sensor_type
        self._name = SENSOR_PREFIX + SENSOR_TYPES[self.type][0]
        self._unit = SENSOR_TYPES[self.type][1]
        self._icon = SENSOR_TYPES[self.type][2]
        self._state = None

        self._discovery = False
        self._dev_id = {}

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        return self._icon

    @property
    def state(self):
        """Return the state of the sensor. (total/current power consumption/production or total gas used)"""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of this entity, if any."""
        return self._unit

    def update(self):
        """Get the latest data and use it to update our sensor state."""
        self.data.update()
        energy = self.data.data

        if self._discovery == False:

            for key in energy:
                dev = energy[key]

                if dev['type'] in ['FGWP011']:
                    self._dev_id['elecusageflowfib'] = key
                    self._dev_id['elecusagecntfib'] = key

            self._discovery = True

        """Go to http://toon.ip:port/hdrv_zwave?action=getDevices.json and search for dev_"""
        if self.type == 'elecusageflowfib':
								   
            if self.type in self._dev_id:
									 
                self._state = energy[self._dev_id[self.type]]["CurrentElectricityFlow"]

        elif self.type == 'elecusagecntfib':
								   
            if self.type in self._dev_id:
									 
                self._state = float(energy[self._dev_id[self.type]]["CurrentElectricityQuantity"])/1000