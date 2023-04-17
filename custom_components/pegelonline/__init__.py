"""The PEGELONLINE integration."""
from __future__ import annotations
import async_timeout
import logging
from datetime import timedelta
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import aiohttp_client
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from .const import DOMAIN, ENDPOINT

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[str] = ["sensor"]


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the PEGELONLINE component."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up PEGELONLINE from a config entry."""
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry"""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def get_coordinator(hass: HomeAssistant, uuid=""):
    """Get the data update coordinator."""
    if uuid == "":
        return

    if DOMAIN in hass.data:
        return hass.data[DOMAIN]

    async def async_get_data():
        with async_timeout.timeout(30):
            response = await aiohttp_client.async_get_clientsession(hass).get(
                ENDPOINT
                + "/stations.json?includeTimeseries=true&includeCurrentMeasurement=true"
            )
        data = await response.json()
        result = {}
        for row in data:
            result[row["uuid"]] = dict(
                uuid=row["uuid"],
                value=f"{row['timeseries'][0]['currentMeasurement']['value']:.0f}",
            )
        return result

    hass.data[DOMAIN] = DataUpdateCoordinator(
        hass,
        logging.getLogger(__name__),
        name=DOMAIN,
        update_method=async_get_data,
        update_interval=timedelta(seconds=900),
    )
    await hass.data[DOMAIN].async_refresh()
    return hass.data[DOMAIN]
