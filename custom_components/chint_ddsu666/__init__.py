"""CHINT DDSU666 Modbus Emulator - Home Assistant Custom Component.

Emuleert een CHINT DDSU666 single-phase energy meter via Modbus TCP.
Registerdefinities en gedrag gebaseerd op de Node-RED flow.
Slave ID-filtering gebaseerd op Modbus-proxy.
"""

import asyncio
import logging
import threading
from datetime import timedelta

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.event import async_track_time_interval
import homeassistant.helpers.config_validation as cv

from .const import (
    DOMAIN,
    DEFAULT_HOST,
    DEFAULT_PORT,
    DEFAULT_SLAVE_ID,
    DEFAULT_TIMEOUT,
    DEFAULT_FREQUENCY,
    DEFAULT_VALUES,
    REGISTERS,
    CONVERSION_FACTORS,
    POLLING_INTERVALS,
    VALIDATION_RULES,
    FLOAT_REGISTER_NAMES,
    STATIC_REGISTERS,
)
from .modbus_server import ModbusServer
from .data_converter import float_to_modbus

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[str] = []

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Optional("modbus"): vol.Schema(
                    {
                        vol.Optional("host", default="0.0.0.0"): str,
                        vol.Optional("port", default=502): int,
                        vol.Optional("slave_id", default=3): int,
                        vol.Optional("timeout", default=30): int,
                        vol.Optional("debug", default=False): bool,
                    }
                ),
                vol.Optional("home_assistant"): vol.Schema(
                    {
                        vol.Optional("voltage_entity"): str,
                        vol.Optional("current_entity"): str,
                        vol.Optional("active_power_entity"): str,
                        vol.Optional("reactive_power_entity"): str,
                        vol.Optional("apparent_power_entity"): str,
                        vol.Optional("power_factor_entity"): str,
                        vol.Optional("frequency_entity"): str,
                        vol.Optional("total_energy_import_t1_entity"): str,
                        vol.Optional("total_energy_import_t2_entity"): str,
                        vol.Optional("total_energy_export_t1_entity"): str,
                        vol.Optional("total_energy_export_t2_entity"): str,
                    }
                ),
                vol.Optional("polling"): vol.Schema(
                    {
                        vol.Optional("voltage_interval", default=5): vol.Coerce(float),
                        vol.Optional("current_interval", default=1): vol.Coerce(float),
                        vol.Optional("active_power_interval", default=0.25): vol.Coerce(float),
                        vol.Optional("reactive_power_interval", default=0.25): vol.Coerce(float),
                        vol.Optional("apparent_power_interval", default=0.25): vol.Coerce(float),
                        vol.Optional("power_factor_interval", default=0.25): vol.Coerce(float),
                        vol.Optional("frequency_interval", default=5): vol.Coerce(float),
                        vol.Optional("energy_interval", default=10): vol.Coerce(float),
                    }
                ),
                vol.Optional("registers"): vol.Schema(
                    {
                        vol.Optional("firmware_version", default=504): int,
                        vol.Optional("clear_energy", default=0): int,
                        vol.Optional("type_protocol", default=166): int,
                        vol.Optional("communication_protocol", default=5): int,
                        vol.Optional("modbus_address", default=3): int,
                        vol.Optional("baudrate", default=3): int,
                        vol.Optional("frequency"): vol.Any(float, str),
                        vol.Optional("reserved_4", default=5): int,
                        vol.Optional("reserved_7", default=10): int,
                        vol.Optional("reserved_8", default=1): int,
                        vol.Optional("reserved_9", default=5): int,
                        vol.Optional("reserved_10", default=0): int,
                        vol.Optional("meter_type", default=166): int,
                    }
                ),
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Setup via configuration.yaml."""
    if DOMAIN not in config:
        return True

    conf = config[DOMAIN]
    hass.data.setdefault(DOMAIN, {})

    hass.async_create_task(
        hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": "import"},
            data=conf,
        )
    )
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Setup vanuit een config entry."""
    modbus_config = entry.data.get("modbus", {})
    ha_config = entry.data.get("home_assistant", {})
    polling_config = entry.data.get("polling", {})
    register_config = entry.data.get("registers", {})

    host = modbus_config.get("host", DEFAULT_HOST)
    port = modbus_config.get("port", DEFAULT_PORT)
    slave_id = modbus_config.get("slave_id", DEFAULT_SLAVE_ID)
    timeout = modbus_config.get("timeout", DEFAULT_TIMEOUT)
    debug = modbus_config.get("debug", False)

    if debug:
        _LOGGER.setLevel(logging.DEBUG)

    server = ModbusServer(
        host=host,
        port=port,
        slave_id=slave_id,
        timeout=timeout,
        debug=debug,
    )

    # Laad statische registerwaarden uit configuratie
    for name, address in REGISTERS.items():
        if name not in DEFAULT_VALUES:
            continue
        value = register_config.get(name, DEFAULT_VALUES[name])
        if name in VALIDATION_RULES:
            rules = VALIDATION_RULES[name]
            if not (rules["min"] <= value <= rules["max"]):
                _LOGGER.warning(
                    "[growatt_meter_emulator]: Ongeldige waarde voor %s: %s. "
                    "Gebruik standaardwaarde: %s",
                    name, value, DEFAULT_VALUES[name],
                )
                value = DEFAULT_VALUES[name]
        if name in FLOAT_REGISTER_NAMES:
            high_word, low_word = float_to_modbus(float(value))
            server._register_values[address] = high_word
            server._register_values[address + 1] = low_word
        else:
            server._register_values[address] = int(value)

    # Start de Modbus-server in een aparte thread
    server_thread = threading.Thread(
        target=server.start,
        daemon=True,
    )
    server_thread.start()

    hass.data[DOMAIN][entry.entry_id] = {
        "server": server,
        "thread": server_thread,
    }

    # Bepaal frequentie: entity of vast getal
    frequency_value = register_config.get("frequency", DEFAULT_FREQUENCY)
    frequency_is_entity = isinstance(frequency_value, str)

    # Polling van Home Assistant entiteiten
    async def _poll_entities(now=None):
        """Poll Home Assistant entiteiten en update Modbus-registers."""
        for name, address in REGISTERS.items():
            if name == "frequency":
                continue

            entity_key = f"{name}_entity"
            entity_id = ha_config.get(entity_key)
            if not entity_id:
                continue

            state = hass.states.get(entity_id)
            if state is None or state.state in ("unknown", "unavailable"):
                continue

            try:
                value = float(state.state)
            except (ValueError, TypeError):
                continue

            if name in CONVERSION_FACTORS:
                value = value * CONVERSION_FACTORS[name]

            server.update_register(name, value)

        # Totale energie import: T1 + T2 (zoals in de Node-RED flow)
        t1_import = _get_entity_value(hass, ha_config.get("total_energy_import_t1_entity"))
        t2_import = _get_entity_value(hass, ha_config.get("total_energy_import_t2_entity"))
        if t1_import is not None or t2_import is not None:
            total_import = (t1_import or 0) + (t2_import or 0)
            server.update_register("total_energy_import", total_import)
            server.update_register("total_energy_import_2", total_import)

        # Totale energie export: T1 + T2 (zoals in de Node-RED flow)
        t1_export = _get_entity_value(hass, ha_config.get("total_energy_export_t1_entity"))
        t2_export = _get_entity_value(hass, ha_config.get("total_energy_export_t2_entity"))
        if t1_export is not None or t2_export is not None:
            total_export = (t1_export or 0) + (t2_export or 0)
            server.update_register("total_energy_export", total_export)
            server.update_register("total_energy_export_2", total_export)

        # Frequentie: entity of vast getal
        if frequency_is_entity:
            freq = _get_entity_value(hass, frequency_value)
            if freq is not None:
                server.update_register("frequency", freq)
        else:
            server.update_register("frequency", float(frequency_value))

    # Polling intervals per register (uit config of Node-RED flow defaults)
    for name, default_interval in POLLING_INTERVALS.items():
        interval_key = f"{name}_interval"
        interval = polling_config.get(interval_key, default_interval)
        async_track_time_interval(
            hass,
            _poll_entities,
            timedelta(seconds=interval),
        )

    return True


def _get_entity_value(hass: HomeAssistant, entity_id: str | None) -> float | None:
    """Haal een numerieke waarde op uit een Home Assistant entity."""
    if not entity_id:
        return None
    state = hass.states.get(entity_id)
    if state is None or state.state in ("unknown", "unavailable"):
        return None
    try:
        return float(state.state)
    except (ValueError, TypeError):
        return None


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload een config entry."""
    data = hass.data[DOMAIN].pop(entry.entry_id, None)
    if data:
        server = data["server"]
        server.stop()
    return True
