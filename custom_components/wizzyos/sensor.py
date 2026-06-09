"""Sensor platform for WizzyOS."""

from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    ATTR_ICON,
    ATTR_UNIT_OF_MEASUREMENT,
    STATE_UNAVAILABLE,
    STATE_UNKNOWN,
)
from homeassistant.core import Event, HomeAssistant, State, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_state_change_event

from .const import ATTR_SOURCE_ENTITY_ID, CONF_ENTITY_ID

ATTR_DEVICE_CLASS = "device_class"


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up WizzyOS sensors from a config entry."""
    async_add_entities([WizzyOSEntitySensor(hass, entry)])


class WizzyOSEntitySensor(SensorEntity):
    """Sensor that mirrors an existing Home Assistant entity."""

    _attr_has_entity_name = False


    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the sensor."""
        self.hass = hass
        self.entry = entry
        self.source_entity_id = entry.data[CONF_ENTITY_ID]
        self._attr_name = entry.title
        self._attr_unique_id = f"{entry.entry_id}_{self.source_entity_id}"
        self._source_state: State | None = hass.states.get(self.source_entity_id)

    @property
    def available(self) -> bool:
        """Return whether the source entity is available."""
        return self._source_state is not None and self._source_state.state not in {
            STATE_UNAVAILABLE,
            STATE_UNKNOWN,
        }

    @property
    def native_value(self) -> str | None:
        """Return the mirrored source state."""
        return self._source_state.state if self._source_state is not None else None

    @property
    def native_unit_of_measurement(self) -> str | None:
        """Return the source entity unit of measurement."""
        if self._source_state is None:
            return None
        return self._source_state.attributes.get(ATTR_UNIT_OF_MEASUREMENT)

    @property
    def icon(self) -> str | None:
        """Return the source entity icon."""
        if self._source_state is None:
            return None
        return self._source_state.attributes.get(ATTR_ICON)

    @property
    def device_class(self) -> str | None:
        """Return the source entity device class."""
        if self._source_state is None:
            return None
        return self._source_state.attributes.get(ATTR_DEVICE_CLASS)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra attributes for the mirrored entity."""
        return {
            ATTR_SOURCE_ENTITY_ID: self.source_entity_id,
        }

    async def async_added_to_hass(self) -> None:
        """Subscribe to source entity state changes."""
        self.async_on_remove(
            async_track_state_change_event(
                self.hass,
                [self.source_entity_id],
                self._async_source_state_changed,
            )
        )

    @callback
    def _async_source_state_changed(self, event: Event) -> None:
        """Handle source entity state changes."""
        self._source_state = event.data.get("new_state")
        self.async_write_ha_state()
