"""Config flow for PEGELONLINE integration."""

from __future__ import annotations
import async_timeout
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import aiohttp_client
from .const import DOMAIN, ENDPOINT


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for PEGELONLINE."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    def __init__(self):
        self._uuid = None
        self._options = None
        self._data = {}

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        if self._options is None:
            self._options = {}
            for row in await self.get_station_data():
                self._options[
                    row["longname"]
                ] = f"{row['water']['longname'].title()}: {row['longname'].title()}"

        if user_input is not None:
            for row in await self.get_station_data():
                if row["longname"] == user_input["longname"]:
                    self._uuid = row["uuid"]
                    self._data["uuid"] = row["uuid"]
                    self._data[
                        "desc"
                    ] = f"{row['water']['longname'].title()}: {row['longname'].title()}"
            await self.async_set_unique_id(self._data["uuid"])
            self._abort_if_unique_id_configured()
            return self.async_create_entry(
                title=self._options[user_input["longname"]], data=self._data
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({vol.Required("longname"): vol.In(self._options)}),
        )

    async def get_station_data(self):
        """Get available PEGELONLINE stations from REST API"""
        with async_timeout.timeout(30):
            response = await aiohttp_client.async_get_clientsession(self.hass).get(
                ENDPOINT + "/stations.json"
            )
        return await response.json()


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""
