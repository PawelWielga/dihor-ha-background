from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import slugify

from . import async_refresh_entry_background
from .const import CONF_DASHBOARD, DEFAULT_DASHBOARD, DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    async_add_entities([DihorBackgroundRefreshButton(hass, entry)])


class DihorBackgroundRefreshButton(ButtonEntity):
    _attr_has_entity_name = True
    _attr_name = "Refresh background"

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self._hass = hass
        self._entry = entry
        self._dashboard = entry.data.get(CONF_DASHBOARD, DEFAULT_DASHBOARD)
        self._attr_unique_id = f"{entry.entry_id}_refresh_background"
        self.entity_id = f"button.{DOMAIN}_{slugify(self._dashboard)}_refresh_background"

    async def async_press(self) -> None:
        await async_refresh_entry_background(self._hass, self._entry)
