from __future__ import annotations

import logging
from datetime import timedelta
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_URL, Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import aiohttp_client, config_validation as cv
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.typing import ConfigType
from homeassistant.util import slugify

from .const import (
    BACKGROUND_DIR,
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
    UNSPLASH_RANDOM_PHOTO_URL,
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = []
CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)

SERVICE_SET_STATIC = "set_static"
SERVICE_REFRESH = "refresh"

SET_STATIC_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_DASHBOARD, default=DEFAULT_DASHBOARD): cv.string,
        vol.Required(CONF_STATIC_PATH): cv.string,
    }
)

REFRESH_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_DASHBOARD, default=DEFAULT_DASHBOARD): cv.string,
        vol.Optional(CONF_URL): cv.url,
    }
)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    hass.data.setdefault(DOMAIN, {})
    await _async_register_services(hass)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    hass.data.setdefault(DOMAIN, {})
    dashboard = entry.data.get(CONF_DASHBOARD, DEFAULT_DASHBOARD)
    hass.data[DOMAIN][entry.entry_id] = entry

    source = entry.data.get(CONF_SOURCE)
    if source == SOURCE_STATIC and entry.data.get(CONF_STATIC_PATH):
        await async_set_static_background(hass, dashboard, entry.data[CONF_STATIC_PATH])

    if source in (SOURCE_API, SOURCE_UNSPLASH):
        minutes = entry.data.get(CONF_REFRESH_MINUTES, DEFAULT_REFRESH_MINUTES)

        async def _refresh_interval(now) -> None:  # noqa: ANN001
            await async_refresh_entry_background(hass, entry)

        remove_listener = async_track_time_interval(
            hass,
            _refresh_interval,
            timedelta(minutes=minutes),
        )
        entry.async_on_unload(remove_listener)
        await async_refresh_entry_background(hass, entry)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    hass.data[DOMAIN].pop(entry.entry_id, None)
    return True


async def _async_register_services(hass: HomeAssistant) -> None:
    if hass.services.has_service(DOMAIN, SERVICE_SET_STATIC):
        return

    async def _set_static(call: ServiceCall) -> None:
        dashboard = call.data[CONF_DASHBOARD]
        static_path = call.data[CONF_STATIC_PATH]
        await async_set_static_background(hass, dashboard, static_path)

    async def _refresh(call: ServiceCall) -> None:
        dashboard = call.data[CONF_DASHBOARD]
        if call.data.get(CONF_URL):
            await async_refresh_background(hass, dashboard, call.data[CONF_URL])
            return

        entry = _find_entry(hass, dashboard)
        if entry is None:
            raise ValueError(f"Dashboard is not configured: {dashboard}")
        await async_refresh_entry_background(hass, entry)

    hass.services.async_register(DOMAIN, SERVICE_SET_STATIC, _set_static, schema=SET_STATIC_SCHEMA)
    hass.services.async_register(DOMAIN, SERVICE_REFRESH, _refresh, schema=REFRESH_SCHEMA)


def _background_path(hass: HomeAssistant, dashboard: str) -> Path:
    safe_dashboard = _safe_dashboard(dashboard)

    directory = Path(hass.config.path("www", BACKGROUND_DIR))
    directory.mkdir(parents=True, exist_ok=True)
    return directory / f"{safe_dashboard}.jpg"


def _public_url(dashboard: str) -> str:
    safe_dashboard = _safe_dashboard(dashboard)
    return f"/local/{BACKGROUND_DIR}/{safe_dashboard}.jpg"


def _entity_id(dashboard: str) -> str:
    return f"{DOMAIN}.{_safe_dashboard(dashboard)}"


def _safe_dashboard(dashboard: str) -> str:
    return slugify(dashboard) or DEFAULT_DASHBOARD


def _find_entry(hass: HomeAssistant, dashboard: str) -> ConfigEntry | None:
    for entry in hass.config_entries.async_entries(DOMAIN):
        if entry.data.get(CONF_DASHBOARD) == dashboard:
            return entry
    return None


def _set_background_state(
    hass: HomeAssistant,
    dashboard: str,
    url: str,
    source: str,
    extra_attributes: dict[str, str | int | None] | None = None,
) -> None:
    attributes = {"dashboard": dashboard, "source": source}
    if extra_attributes:
        attributes.update({key: value for key, value in extra_attributes.items() if value is not None})
    hass.states.async_set(_entity_id(dashboard), url, attributes)


async def async_refresh_entry_background(hass: HomeAssistant, entry: ConfigEntry) -> str:
    dashboard = entry.data.get(CONF_DASHBOARD, DEFAULT_DASHBOARD)
    source = entry.data.get(CONF_SOURCE)

    if source == SOURCE_API:
        return await async_refresh_background(hass, dashboard, entry.data.get(CONF_API_URL))
    if source == SOURCE_UNSPLASH:
        return await async_refresh_unsplash_background(hass, dashboard, entry.data)
    if source == SOURCE_STATIC:
        return await async_set_static_background(hass, dashboard, entry.data[CONF_STATIC_PATH])

    raise ValueError(f"Unsupported background source: {source}")


async def async_set_static_background(
    hass: HomeAssistant,
    dashboard: str,
    static_path: str,
) -> str:
    source = Path(static_path)
    if not source.is_absolute():
        source = Path(hass.config.path(static_path))
    target = _background_path(hass, dashboard)

    if not source.exists() or not source.is_file():
        raise FileNotFoundError(f"Static background file does not exist: {source}")

    def _copy_file() -> None:
        target.write_bytes(source.read_bytes())

    await hass.async_add_executor_job(_copy_file)
    _set_background_state(hass, dashboard, _public_url(dashboard), SOURCE_STATIC)
    return _public_url(dashboard)


async def async_refresh_background(
    hass: HomeAssistant,
    dashboard: str,
    api_url: str | None,
) -> str:
    if not api_url:
        raise ValueError("API URL is required to refresh dashboard background")

    session = aiohttp_client.async_get_clientsession(hass)
    async with session.get(api_url) as response:
        response.raise_for_status()
        content = await response.read()

    target = _background_path(hass, dashboard)
    await hass.async_add_executor_job(target.write_bytes, content)
    _set_background_state(hass, dashboard, _public_url(dashboard), SOURCE_API)
    return _public_url(dashboard)


async def async_refresh_unsplash_background(
    hass: HomeAssistant,
    dashboard: str,
    config: dict,
) -> str:
    access_key = config.get(CONF_UNSPLASH_ACCESS_KEY)
    if not access_key:
        raise ValueError("Unsplash access key is required")

    params = {
        "orientation": config.get(CONF_UNSPLASH_ORIENTATION, DEFAULT_UNSPLASH_ORIENTATION),
        "content_filter": config.get(
            CONF_UNSPLASH_CONTENT_FILTER,
            DEFAULT_UNSPLASH_CONTENT_FILTER,
        ),
    }
    if config.get(CONF_UNSPLASH_QUERY):
        params["query"] = config[CONF_UNSPLASH_QUERY]

    headers = {
        "Accept-Version": "v1",
        "Authorization": f"Client-ID {access_key}",
    }

    session = aiohttp_client.async_get_clientsession(hass)
    async with session.get(UNSPLASH_RANDOM_PHOTO_URL, headers=headers, params=params) as response:
        response.raise_for_status()
        photo = await response.json()

    urls = photo.get("urls", {})
    raw_url = urls.get("raw")
    if not raw_url:
        raise ValueError("Unsplash response does not contain urls.raw")

    image_url = _with_image_params(
        raw_url,
        {
            "w": config.get(CONF_UNSPLASH_WIDTH, DEFAULT_UNSPLASH_WIDTH),
            "h": config.get(CONF_UNSPLASH_HEIGHT, DEFAULT_UNSPLASH_HEIGHT),
            "fit": "crop",
            "crop": "entropy",
            "auto": "format",
            "q": config.get(CONF_UNSPLASH_QUALITY, DEFAULT_UNSPLASH_QUALITY),
        },
    )

    async with session.get(image_url) as response:
        response.raise_for_status()
        content = await response.read()

    target = _background_path(hass, dashboard)
    await hass.async_add_executor_job(target.write_bytes, content)

    user = photo.get("user") or {}
    links = photo.get("links") or {}
    _set_background_state(
        hass,
        dashboard,
        _public_url(dashboard),
        SOURCE_UNSPLASH,
        {
            "photo_id": photo.get("id"),
            "photographer": user.get("name"),
            "photographer_url": (user.get("links") or {}).get("html"),
            "unsplash_url": links.get("html"),
            "image_url": image_url,
        },
    )
    return _public_url(dashboard)


def _with_image_params(url: str, params: dict[str, str | int]) -> str:
    parsed = urlparse(url)
    query = dict(parse_qsl(parsed.query, keep_blank_values=True))
    query.update({key: str(value) for key, value in params.items()})
    return urlunparse(parsed._replace(query=urlencode(query)))
