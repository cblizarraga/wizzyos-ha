"""The WizzyOS integration."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import Platform

from .const import CONF_ENTITY_ID, DATA_ENTITY_ID, DATA_ENTITY_STATE, DOMAIN

PLATFORMS = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up WizzyOS from a config entry."""
    entity_id = entry.data[CONF_ENTITY_ID]
    state = hass.states.get(entity_id)

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        DATA_ENTITY_ID: entity_id,
        DATA_ENTITY_STATE: {
            "available": state is not None,
            "state": state.state if state is not None else None,
            "attributes": dict(state.attributes) if state is not None else {},
        },
    }
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if not unload_ok:
        return False

    hass.data[DOMAIN].pop(entry.entry_id, None)
    return True
