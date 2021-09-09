import logging

from homeassistant.components.sensor import SensorEntity

from homeassistant.const import (
    TEMP_CELSIUS,
    DEVICE_CLASS_TEMPERATURE
)

from .melview import MelViewAuthentication, MelView, MODE, FAN

_LOGGER = logging.getLogger(__name__)

DOMAIN = 'melview'
REQUIREMENTS = ['requests']
DEPENDENCIES = []

class MelViewOutdoorTemperatureSensor(SensorEntity):

    def __init__(self, device):
        self._device = device

        self._name = 'MelView {} Outdoor Temperature'.format(device.get_friendly_name())
        self._unique_id = device.get_id()

        self._outside_temp = self._device.get_room_temperature()
        self._state = self._outside_temp

    def update(self):
        """ Update device properties
        """
        _LOGGER.debug('updating state')
        self._device.force_update()

        self._outside_temp = self._device.get_outside_temperature()
        self._state = self._outside_temp

    @property
    def device_class(self):
        return DEVICE_CLASS_TEMPERATURE

    @property
    def name(self):
        return self._name

    @property
    def unique_id(self):
        return self._unique_id

    @property
    def state(self):
        return self._state

    @property
    def unit_of_measurement(self):
        return TEMP_CELSIUS

# ---------------------------------------------------------------

def setup_platform(hass, config, add_devices, discovery_info=None):
    """ Set up the HASS component
    """
    _LOGGER.debug('adding component')

    email = config.get('email')
    password = config.get('password')
    local = config.get('local')

    if email is None:
        _LOGGER.error('no email provided')
        return False

    if password is None:
        _LOGGER.error('no password provided')
        return False

    if local is None:
        _LOGGER.warning('local unspecified, defaulting to false')
        local = False

    mv_auth = MelViewAuthentication(email, password)
    if not mv_auth.login():
        _LOGGER.error('login combination')
        return False

    melview = MelView(mv_auth, localcontrol=local)

    device_list = []

    devices = melview.get_devices_list()
    for device in devices:
        _LOGGER.debug('new device: %s', device.get_friendly_name())
        device_list.append(MelViewClimate(device))

    add_devices(device_list)

    _LOGGER.debug('component successfully added')
    return True

# ---------------------------------------------------------------
