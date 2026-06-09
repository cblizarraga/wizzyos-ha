"""Config flow for WizzyOS."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import valid_entity_id
from homeassistant.helpers import selector

from .const import CONF_ENTITY_ID, CONF_NAME, DOMAIN


class WizzyOSConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for WizzyOS."""

    VERSION = 1


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
