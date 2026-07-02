"""Constantes voor de CHINT DDSU666 Modbus-emulator.

Registerdefinities gebaseerd op de Node-RED flow:
_data/chint_ddsu666_single_phase_emulatorv4.json
"""

DOMAIN = "chint_ddsu666"

DEFAULT_SLAVE_ID = 3
DEFAULT_TIMEOUT = 30
DEFAULT_HOST = "0.0.0.0"
DEFAULT_PORT = 502

# Registeradressen (hexadecimaal)
REGISTERS = {
    # Eerste 16 registers (0x0001 - 0x0010) — 16-bit integers
    "firmware_version": 0x0001,
    "clear_energy": 0x0002,
    "type_protocol": 0x0003,
    "reserved_4": 0x0004,
    "communication_protocol": 0x0005,
    "modbus_address": 0x0006,
    "reserved_7": 0x0007,
    "reserved_8": 0x0008,
    "reserved_9": 0x0009,
    "reserved_10": 0x000A,
    "meter_type": 0x000B,
    "baudrate": 0x000C,

    # Meetwaarden (0x2000 - 0x400A) — 32-bit floats
    "voltage": 0x2000,
    "current": 0x2002,
    "active_power": 0x2004,
    "reactive_power": 0x2006,
    "apparent_power": 0x2008,
    "power_factor": 0x200A,
    "frequency": 0x200E,
    "total_energy_import": 0x4000,
    "total_energy_export": 0x400A,
}

# Standaardwaarden voor de eerste 16 registers (uit de Node-RED flow)
DEFAULT_VALUES = {
    "firmware_version": 504,
    "clear_energy": 0,
    "type_protocol": 166,
    "reserved_4": 5,
    "communication_protocol": 5,
    "modbus_address": 3,
    "reserved_7": 10,
    "reserved_8": 1,
    "reserved_9": 5,
    "reserved_10": 0,
    "meter_type": 166,
    "baudrate": 3,
}

# Conversiefactoren (uit de Node-RED flow: ×0.001 voor vermogens)
CONVERSION_FACTORS = {
    "active_power": 0.001,
    "reactive_power": 0.001,
    "apparent_power": 0.001,
}

# Polling intervals in seconden (uit de Node-RED flow)
POLLING_INTERVALS = {
    "voltage": 5,
    "current": 1,
    "active_power": 1,
    "reactive_power": 1,
    "apparent_power": 1,
    "power_factor": 1,
    "frequency": 5,
    "total_energy_import": 10,
    "total_energy_export": 10,
}

# Standaard frequentie (uit de Node-RED inject-node)
DEFAULT_FREQUENCY = 50.0
FIXED_FREQUENCY = 50.0  # Vaste waarde voor register 0x200E (uit Node-RED flow)

# Validatieregels voor statische registers
VALIDATION_RULES = {
    "baudrate": {"min": 0, "max": 3},
    "clear_energy": {"min": 0, "max": 1},
    "frequency": {"min": 40.0, "max": 70.0},
}

# Modbus functiecodes
FUNC_READ_HOLDING_REGISTERS = 0x03
FUNC_WRITE_SINGLE_REGISTER = 0x06
FUNC_WRITE_MULTIPLE_REGISTERS = 0x10

# Modbus exception codes
EXCEPTION_ILLEGAL_FUNCTION = 0x01
EXCEPTION_ILLEGAL_DATA_ADDRESS = 0x02
EXCEPTION_ILLEGAL_DATA_VALUE = 0x03
