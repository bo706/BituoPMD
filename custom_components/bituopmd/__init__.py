import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import Platform
from homeassistant.exceptions import ConfigEntryNotReady
from .const import DOMAIN, CONF_HOST_IP, CONF_KIND, CONF_DIAL_SN
from .device_api import KIND_DIAL, DeviceProbeError, probe_device
from .frontend import setup_frontend
_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.SENSOR, Platform.BUTTON, Platform.SWITCH]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up BituoPMD integration from a config entry."""
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}

    host_ip = entry.data[CONF_HOST_IP]
    _LOGGER.info("Setting up BituoPMD integration for %s", host_ip)
    
    # Initialize the data dictionary for this entry
    hass.data[DOMAIN][entry.entry_id] = {}

    try:
        probed = await hass.async_add_executor_job(probe_device, host_ip)
    except DeviceProbeError as e:
        _LOGGER.error("Error fetching device data from %s: %s", host_ip, e)
        raise ConfigEntryNotReady from e

    new_data = dict(entry.data)
    new_data[CONF_KIND] = probed["kind"]
    if probed["kind"] == KIND_DIAL:
        new_data[CONF_DIAL_SN] = probed["dial_sn"]
    hass.config_entries.async_update_entry(
        entry, data=new_data, title=probed["title"]
    )

    # Forward the setup to the sensor platforms
    try:
        await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    except ConfigEntryNotReady as e:
        _LOGGER.error("Error setting up platforms for BituoPMD: %s", e)
        raise ConfigEntryNotReady from e

    # Set up the frontend
    await setup_frontend(hass)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a BituoPMD config entry."""
    _LOGGER.info("Unloading BituoPMD integration for %s", entry.data[CONF_HOST_IP])

    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        _LOGGER.info("Successfully unloaded BituoPMD integration for %s", entry.data[CONF_HOST_IP])
        if DOMAIN in hass.data:
            hass.data[DOMAIN].pop(entry.entry_id, None)

    return unload_ok

async def async_remove_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle removal of an entry."""
    _LOGGER.info("Removing BituoPMD integration for %s", entry.data[CONF_HOST_IP])
    if DOMAIN in hass.data:
        hass.data[DOMAIN].pop(entry.entry_id, None)
