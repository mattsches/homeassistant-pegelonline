"""Support for getting current PEGELONLINE data from the PEGELONLINE REST-API."""

from homeassistant.helpers.entity import Entity
from . import get_coordinator
from .const import ATTR_PEGEL


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Defer sensor setup to the shared sensor module."""
    coordinator = await get_coordinator(hass, config_entry.unique_id)
    async_add_entities([PegelOnlineSensor(coordinator, config_entry.data)])


class PegelOnlineSensor(Entity):
    """Representation of a PEGELONLINE station."""

    def __init__(self, coordinator, data):
        """Initialize sensor."""
        self.coordinator = coordinator
        self._uuid = data["uuid"]
        self._name = f"Pegel {data['desc']}"
        self._state = None

    @property
    def available(self):
        if self.coordinator.data is None:
            return False

        return (
            self.coordinator.last_update_success and self._uuid in self.coordinator.data
        )

    @property
    def name(self):
        return self._name

    @property
    def unique_id(self):
        return self._uuid

    @property
    def icon(self):
        return "mdi:waves"

    @property
    def unit_of_measurement(self):
        return "cm"

    @property
    def state(self):
        data = self.coordinator.data
        if data is not None and self._uuid in data:
            return data[self._uuid]["value"]

        return False

    @property
    def device_state_attributes(self):
        return {ATTR_PEGEL: self.coordinator.data[self._uuid]["value"]}

    async def async_added_to_hass(self):
        """When entity is added to hass."""
        self.coordinator.async_add_listener(self.async_write_ha_state)

    async def async_will_remove_from_hass(self):
        """When entity will be removed from hass."""
        self.coordinator.async_remove_listener(self.async_write_ha_state)
