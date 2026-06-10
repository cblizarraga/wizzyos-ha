"""The WizzyOS integration."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import Event, HomeAssistant, callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.event import async_track_state_change_event

from .client import WizzyOSClient
from .const import (
    CONF_API_TOKEN,
    CONF_BACKEND_URL,
    CONF_ENABLED,
    CONF_ENTITIES,
    CONF_ENTITY_ID,
    DATA_CLIENT,
    DATA_ENTITY_ID,
    DATA_ENTITY_STATE,
    DATA_STATS,
    DATA_UNSUB_STATE,
    DEFAULT_ENABLED,
    DOMAIN,
    VERSION,
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up WizzyOS from a config entry."""
    entity_id = entry.data[CONF_ENTITY_ID]
    state = hass.states.get(entity_id)
    entities = _configured_entities(entry)
    enabled = bool(_option(entry, CONF_ENABLED, DEFAULT_ENABLED))
    backend_url = str(_option(entry, CONF_BACKEND_URL, ""))
    api_token = str(_option(entry, CONF_API_TOKEN, ""))
    client = None

    if enabled and backend_url and api_token:
        client = WizzyOSClient(
            hass,
            async_get_clientsession(hass),
            backend_url,
            api_token,
            VERSION,
        )

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        DATA_ENTITY_ID: entity_id,
        CONF_ENTITIES: entities,
        DATA_CLIENT: client,
        DATA_STATS: {
            "events_sent": 0,
            "send_errors": 0,
            "last_success": None,
            "last_error": None,
        },
        DATA_ENTITY_STATE: {
            "available": state is not None,
            "state": state.state if state is not None else None,
            "attributes": dict(state.attributes) if state is not None else {},
        },
    }

    if client is not None:
        hass.data[DOMAIN][entry.entry_id][DATA_UNSUB_STATE] = async_track_state_change_event(
            hass,
            entities,
            _async_state_changed_factory(hass, entry),
        )

    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if not unload_ok:
        return False

    if unsub := hass.data[DOMAIN][entry.entry_id].get(DATA_UNSUB_STATE):
        unsub()

    hass.data[DOMAIN].pop(entry.entry_id, None)
    return True


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload WizzyOS when options change."""
    await hass.config_entries.async_reload(entry.entry_id)


def _configured_entities(entry: ConfigEntry) -> list[str]:
    """Return all configured source entities without duplicates."""
    entities = [entry.data[CONF_ENTITY_ID]]
    entities.extend(entry.options.get(CONF_ENTITIES, []))
    return list(dict.fromkeys(entities))


def _option(entry: ConfigEntry, key: str, default: object) -> object:
    """Return an option value with config entry data fallback."""
    return entry.options.get(key, entry.data.get(key, default))


def _async_state_changed_factory(hass: HomeAssistant, entry: ConfigEntry):
    """Create a state change callback for a config entry."""

    @callback
    def _async_state_changed(event: Event) -> None:
        new_state = event.data.get("new_state")
        if new_state is None:
            return
        hass.async_create_task(_async_send_state(hass, entry, new_state))

    return _async_state_changed


async def _async_send_state(hass: HomeAssistant, entry: ConfigEntry, state) -> None:
    """Send a state change to WizzyOS SaaS."""
    data = hass.data[DOMAIN][entry.entry_id]
    client = data.get(DATA_CLIENT)
    if client is None:
        return

    stats = data[DATA_STATS]
    if await client.async_send_state(entry.entry_id, state):
        stats["events_sent"] += 1
        stats["last_success"] = state.last_updated.isoformat()
        return

    stats["send_errors"] += 1
    stats["last_error"] = state.last_updated.isoformat()
    _LOGGER.debug("Failed to send WizzyOS event for %s", state.entity_id)
