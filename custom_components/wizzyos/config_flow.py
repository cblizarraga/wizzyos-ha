"""Config flow for WizzyOS."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import valid_entity_id
from homeassistant.helpers import selector

from .const import CONF_ENTITIES, CONF_ENTITY_ID, CONF_NAME, DOMAIN


class WizzyOSConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for WizzyOS."""

    VERSION = 1

    @staticmethod
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

            if not valid_entity_id(entity_id):
                errors[CONF_ENTITY_ID] = "invalid_entity_id"
            elif self.hass.states.get(entity_id) is None:
                errors[CONF_ENTITY_ID] = "entity_not_found"
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
                }
            ),
            errors=errors,
        )


class WizzyOSOptionsFlow(config_entries.OptionsFlow):
    """Handle WizzyOS options."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Manage the configured entities."""
        errors: dict[str, str] = {}

        configured_entities = _configured_entities(self.config_entry)

        if user_input is not None:
            entities = user_input[CONF_ENTITIES]
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
            else:
                return self.async_create_entry(
                    title="",
                    data={CONF_ENTITIES: entities},
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
                }
            ),
            errors=errors,
        )


def _configured_entities(config_entry: config_entries.ConfigEntry) -> list[str]:
    """Return all configured source entities without duplicates."""
    entities = [config_entry.data[CONF_ENTITY_ID]]
    entities.extend(config_entry.options.get(CONF_ENTITIES, []))
    return list(dict.fromkeys(entities))
