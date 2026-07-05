"""Config flow voor de CHINT DDSU666 Modbus Emulator.

Ondersteunt configuratie via configuration.yaml (YAML-only, geen UI).
"""

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback

from .const import (
    DOMAIN,
    DEFAULT_HOST,
    DEFAULT_PORT,
    DEFAULT_SLAVE_ID,
    DEFAULT_TIMEOUT,
    DEFAULT_FREQUENCY,
    DEFAULT_VALUES,
    VALIDATION_RULES,
)

CONFIG_SCHEMA = vol.Schema(
    {
        vol.Required("modbus"): vol.Schema(
            {
                vol.Optional("host", default=DEFAULT_HOST): str,
                vol.Optional("port", default=DEFAULT_PORT): int,
                vol.Optional("slave_id", default=DEFAULT_SLAVE_ID): int,
                vol.Optional("timeout", default=DEFAULT_TIMEOUT): int,
                vol.Optional("debug", default=False): bool,
            }
        ),
        vol.Required("home_assistant"): vol.Schema(
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
                vol.Optional("current_interval", default=0.02): vol.Coerce(float),
                vol.Optional("active_power_interval", default=0.02): vol.Coerce(float),
                vol.Optional("reactive_power_interval", default=0.02): vol.Coerce(float),
                vol.Optional("apparent_power_interval", default=0.02): vol.Coerce(float),
                vol.Optional("power_factor_interval", default=0.02): vol.Coerce(float),
                vol.Optional("frequency_interval", default=5): vol.Coerce(float),
                vol.Optional("energy_interval", default=10): vol.Coerce(float),
            }
        ),
        vol.Optional("registers"): vol.Schema(
            {
                vol.Optional("firmware_version", default=DEFAULT_VALUES["firmware_version"]): int,
                vol.Optional("clear_energy", default=DEFAULT_VALUES["clear_energy"]): vol.All(
                    int, vol.Range(min=0, max=1)
                ),
                vol.Optional("type_protocol", default=DEFAULT_VALUES["type_protocol"]): int,
                vol.Optional("communication_protocol", default=DEFAULT_VALUES["communication_protocol"]): int,
                vol.Optional("modbus_address", default=DEFAULT_VALUES["modbus_address"]): int,
                vol.Optional("baudrate", default=DEFAULT_VALUES["baudrate"]): vol.All(
                    int, vol.Range(min=0, max=3)
                ),
                vol.Optional("frequency", default=DEFAULT_FREQUENCY): vol.Any(
                    vol.All(vol.Coerce(float), vol.Range(min=40.0, max=70.0)),
                    str,
                ),
                vol.Optional("reserved_4", default=DEFAULT_VALUES["reserved_4"]): int,
                vol.Optional("reserved_7", default=DEFAULT_VALUES["reserved_7"]): int,
                vol.Optional("reserved_8", default=DEFAULT_VALUES["reserved_8"]): int,
                vol.Optional("reserved_9", default=DEFAULT_VALUES["reserved_9"]): int,
                vol.Optional("reserved_10", default=DEFAULT_VALUES["reserved_10"]): int,
                vol.Optional("meter_type", default=DEFAULT_VALUES["meter_type"]): int,
            }
        ),
    }
)


class ChintDDSU666ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow voor CHINT DDSU666."""

    VERSION = 1

    async def async_step_import(self, user_input=None):
        """Importeer configuratie vanuit configuration.yaml."""
        if user_input is None:
            return self.async_abort(reason="no_config")

        port = user_input.get("modbus", {}).get("port", DEFAULT_PORT)
        await self.async_set_unique_id(f"chint_ddsu666_port_{port}")
        self._abort_if_unique_id_configured(updates=user_input)

        return self.async_create_entry(
            title=f"CHINT DDSU666 Emulator (poort {port})",
            data=user_input,
        )

    async def async_step_user(self, user_input=None):
        """Handle een user-initiated config flow (niet ondersteund, gebruik YAML)."""
        return self.async_abort(reason="yaml_only")
