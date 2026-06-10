"""Config flow for WizzyOS."""

from __future__ import annotations

from typing import Any
from urllib.parse import urlparse

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback, valid_entity_id
from homeassistant.helpers import selector

from .const import (
    CONF_API_TOKEN,
    CONF_BACKEND_URL,
    CONF_ENABLED,
    CONF_ENTITIES,
    CONF_ENTITY_ID,
    CONF_NAME,
    DEFAULT_ENABLED,
    DOMAIN,
)


class WizzyOSConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for WizzyOS."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Create the options flow."""
        return WizzyOSOptionsFlow(config_entry)


    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            entity_id = user_input[CONF_ENTITY_ID]
            backend_url = user_input.get(CONF_BACKEND_URL, "")
            api_token = user_input.get(CONF_API_TOKEN, "")
            enabled = user_input.get(CONF_ENABLED, DEFAULT_ENABLED)

            if not valid_entity_id(entity_id):
                errors[CONF_ENTITY_ID] = "invalid_entity_id"
            elif self.hass.states.get(entity_id) is None:
                errors[CONF_ENTITY_ID] = "entity_not_found"
            elif backend_url and not _valid_https_url(backend_url):
                errors[CONF_BACKEND_URL] = "invalid_url"
            elif enabled and (not backend_url or not api_token):
                errors[CONF_ENABLED] = "missing_backend_config"
            else:
                await self.async_set_unique_id(entity_id)
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=user_input[CONF_NAME],
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_NAME): str,
                    vol.Required(CONF_ENTITY_ID): selector.EntitySelector(),
                    vol.Optional(CONF_BACKEND_URL, default=""): str,
                    vol.Optional(CONF_API_TOKEN, default=""): str,
                    vol.Optional(CONF_ENABLED, default=DEFAULT_ENABLED): bool,
                }
            ),
            errors=errors,
        )


class WizzyOSOptionsFlow(config_entries.OptionsFlow):
    """Handle WizzyOS options."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self._config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Manage the configured entities."""
        errors: dict[str, str] = {}

        configured_entities = _configured_entities(self._config_entry)
        backend_url = self._config_entry.options.get(
            CONF_BACKEND_URL, self._config_entry.data.get(CONF_BACKEND_URL, "")
        )
        api_token = self._config_entry.options.get(
            CONF_API_TOKEN, self._config_entry.data.get(CONF_API_TOKEN, "")
        )
        enabled = self._config_entry.options.get(
            CONF_ENABLED, self._config_entry.data.get(CONF_ENABLED, DEFAULT_ENABLED)
        )

        if user_input is not None:
            entities = user_input[CONF_ENTITIES]
            backend_url = user_input.get(CONF_BACKEND_URL, "")
            api_token = user_input.get(CONF_API_TOKEN, "")
            enabled = user_input.get(CONF_ENABLED, DEFAULT_ENABLED)
            invalid_entities = [
                entity_id for entity_id in entities if not valid_entity_id(entity_id)
            ]
            missing_entities = [
                entity_id for entity_id in entities if self.hass.states.get(entity_id) is None
            ]

            if invalid_entities:
                errors[CONF_ENTITIES] = "invalid_entity_id"
            elif missing_entities:
                errors[CONF_ENTITIES] = "entity_not_found"
            elif backend_url and not _valid_https_url(backend_url):
                errors[CONF_BACKEND_URL] = "invalid_url"
            elif enabled and (not backend_url or not api_token):
                errors[CONF_ENABLED] = "missing_backend_config"
            else:
                return self.async_create_entry(
                    title="",
                    data={
                        CONF_ENTITIES: entities,
                        CONF_BACKEND_URL: backend_url,
                        CONF_API_TOKEN: api_token,
                        CONF_ENABLED: enabled,
                    },
                )

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_ENTITIES,
                        default=configured_entities,
                    ): selector.EntitySelector(
                        selector.EntitySelectorConfig(multiple=True)
                    ),
                    vol.Optional(CONF_BACKEND_URL, default=backend_url): str,
                    vol.Optional(CONF_API_TOKEN, default=api_token): str,
                    vol.Optional(CONF_ENABLED, default=enabled): bool,
                }
            ),
            errors=errors,
        )


def _configured_entities(config_entry: config_entries.ConfigEntry) -> list[str]:
    """Return all configured source entities without duplicates."""
    entities = [config_entry.data[CONF_ENTITY_ID]]
    entities.extend(config_entry.options.get(CONF_ENTITIES, []))
    return list(dict.fromkeys(entities))


def _valid_https_url(value: str) -> bool:
    """Return whether a backend URL is a valid HTTPS URL."""
    parsed = urlparse(value)
    return parsed.scheme == "https" and bool(parsed.netloc)
