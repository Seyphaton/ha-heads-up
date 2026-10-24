"""Config flow for Heads Up. One entry, no input (D-026)."""

from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult

from .const import DOMAIN


class HeadsUpConfigFlow(ConfigFlow, domain=DOMAIN):
    """Create the single Heads Up entry."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Confirm and create the entry."""
        # Duplicate entries are prevented by "single_config_entry" in manifest.json.
        if user_input is not None:
            return self.async_create_entry(title="Heads Up", data={})
        return self.async_show_form(step_id="user")
