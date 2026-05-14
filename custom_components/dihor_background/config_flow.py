from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries

from .const import (
    CONF_API_URL,
    CONF_DASHBOARD,
    CONF_REFRESH_MINUTES,
    CONF_SOURCE,
    CONF_STATIC_PATH,
    CONF_UNSPLASH_ACCESS_KEY,
    CONF_UNSPLASH_CONTENT_FILTER,
    CONF_UNSPLASH_HEIGHT,
    CONF_UNSPLASH_ORIENTATION,
    CONF_UNSPLASH_QUERY,
    CONF_UNSPLASH_QUALITY,
    CONF_UNSPLASH_WIDTH,
    DEFAULT_DASHBOARD,
    DEFAULT_REFRESH_MINUTES,
    DEFAULT_UNSPLASH_CONTENT_FILTER,
    DEFAULT_UNSPLASH_HEIGHT,
    DEFAULT_UNSPLASH_ORIENTATION,
    DEFAULT_UNSPLASH_QUALITY,
    DEFAULT_UNSPLASH_WIDTH,
    DOMAIN,
    SOURCE_API,
    SOURCE_STATIC,
    SOURCE_UNSPLASH,
)


class DihorBackgroundConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            dashboard = user_input[CONF_DASHBOARD]
            await self.async_set_unique_id(dashboard)
            self._abort_if_unique_id_configured()

            if user_input[CONF_SOURCE] == SOURCE_API and not user_input.get(CONF_API_URL):
                errors[CONF_API_URL] = "required"
            elif user_input[CONF_SOURCE] == SOURCE_STATIC and not user_input.get(CONF_STATIC_PATH):
                errors[CONF_STATIC_PATH] = "required"
            elif user_input[CONF_SOURCE] == SOURCE_UNSPLASH and not user_input.get(
                CONF_UNSPLASH_ACCESS_KEY
            ):
                errors[CONF_UNSPLASH_ACCESS_KEY] = "required"
            else:
                return self.async_create_entry(
                    title=f"Dihor Background: {dashboard}",
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_DASHBOARD, default=DEFAULT_DASHBOARD): str,
                    vol.Required(CONF_SOURCE, default=SOURCE_STATIC): vol.In(
                        [SOURCE_STATIC, SOURCE_API, SOURCE_UNSPLASH]
                    ),
                    vol.Optional(CONF_STATIC_PATH): str,
                    vol.Optional(CONF_API_URL): str,
                    vol.Optional(CONF_UNSPLASH_ACCESS_KEY): str,
                    vol.Optional(CONF_UNSPLASH_QUERY): str,
                    vol.Optional(
                        CONF_UNSPLASH_ORIENTATION,
                        default=DEFAULT_UNSPLASH_ORIENTATION,
                    ): vol.In(["landscape", "portrait", "squarish"]),
                    vol.Optional(
                        CONF_UNSPLASH_CONTENT_FILTER,
                        default=DEFAULT_UNSPLASH_CONTENT_FILTER,
                    ): vol.In(["low", "high"]),
                    vol.Optional(
                        CONF_UNSPLASH_WIDTH,
                        default=DEFAULT_UNSPLASH_WIDTH,
                    ): vol.All(vol.Coerce(int), vol.Range(min=320, max=7680)),
                    vol.Optional(
                        CONF_UNSPLASH_HEIGHT,
                        default=DEFAULT_UNSPLASH_HEIGHT,
                    ): vol.All(vol.Coerce(int), vol.Range(min=320, max=4320)),
                    vol.Optional(
                        CONF_UNSPLASH_QUALITY,
                        default=DEFAULT_UNSPLASH_QUALITY,
                    ): vol.All(vol.Coerce(int), vol.Range(min=1, max=100)),
                    vol.Optional(
                        CONF_REFRESH_MINUTES,
                        default=DEFAULT_REFRESH_MINUTES,
                    ): vol.All(vol.Coerce(int), vol.Range(min=1, max=1440)),
                }
            ),
            errors=errors,
        )
