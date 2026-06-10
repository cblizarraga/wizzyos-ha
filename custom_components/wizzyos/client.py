"""HTTP client for the WizzyOS SaaS bridge."""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime
import logging
from typing import Any
from uuid import uuid4

from aiohttp import ClientError, ClientResponseError, ClientSession, ClientTimeout

from homeassistant.core import HomeAssistant, State

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

EVENTS_PATH = "/v1/home-assistant/events"
SCHEMA_VERSION = "1.0"


class WizzyOSClient:
    """Client that sends Home Assistant entity events to WizzyOS SaaS."""

    def __init__(
        self,
        hass: HomeAssistant,
        session: ClientSession,
        backend_url: str,
        api_token: str,
        version: str,
    ) -> None:
        """Initialize the client."""
        self.hass = hass
        self.session = session
        self.backend_url = backend_url.rstrip("/")
        self.api_token = api_token
        self.version = version

    async def async_send_state(self, entry_id: str, state: State) -> bool:
        """Send a state payload to WizzyOS SaaS."""
        payload = self._build_payload(entry_id, state)
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
            "User-Agent": f"WizzyOS-HA/{self.version}",
            "X-WizzyOS-Schema-Version": SCHEMA_VERSION,
            "X-WizzyOS-Event-Id": payload["event_id"],
        }

        try:
            async with self.session.post(
                f"{self.backend_url}{EVENTS_PATH}",
                json=payload,
                headers=headers,
                timeout=ClientTimeout(total=10),
            ) as response:
                response.raise_for_status()
        except ClientResponseError as err:
            _LOGGER.warning(
                "WizzyOS backend rejected state for %s with HTTP %s",
                state.entity_id,
                err.status,
            )
            return False
        except asyncio.TimeoutError:
            _LOGGER.warning("Timed out sending WizzyOS state for %s", state.entity_id)
            return False
        except ClientError as err:
            _LOGGER.warning(
                "Failed sending WizzyOS state for %s: %s",
                state.entity_id,
                err.__class__.__name__,
            )
            return False

        return True

    def _build_payload(self, entry_id: str, state: State) -> dict[str, Any]:
        """Build the WizzyOS event payload."""
        return {
            "schema_version": SCHEMA_VERSION,
            "source": "home_assistant",
            "integration": DOMAIN,
            "instance_id": entry_id,
            "event_id": str(uuid4()),
            "sent_at": datetime.now(UTC).isoformat(),
            "entity": {
                "entity_id": state.entity_id,
                "state": state.state,
                "attributes": dict(state.attributes),
                "last_changed": state.last_changed.isoformat(),
                "last_updated": state.last_updated.isoformat(),
            },
            "home_assistant": {
                "time_zone": str(self.hass.config.time_zone),
            },
        }
