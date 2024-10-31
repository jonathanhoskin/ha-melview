"""The MelView integration."""

DOMAIN = 'melview'
REQUIREMENTS = ['requests']
DEPENDENCIES = []

def setup(hass, config):

    def handle_hello(call):
        """Handle the service call."""
        name = call.data.get(ATTR_NAME, DEFAULT_NAME)

        hass.states.set("hello_service.hello", name)

    hass.services.register(DOMAIN, "hello", handle_hello)

    # Return boolean to indicate that initialization was successfully.
    return True

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
