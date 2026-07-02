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
    # Eerste 16 registers (0x0000 - 0x0010) — 16-bit integers
    "reserved_0": 0x0000,
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
    "reserved_13": 0x000D,
    "reserved_14": 0x000E,
    "reserved_15": 0x000F,
    "reserved_16": 0x0010,

    # Meetwaarden (0x2000 - 0x200E) — 32-bit floats
    "voltage": 0x2000,
    "current": 0x2002,
    "active_power": 0x2004,
    "reactive_power": 0x2006,
    "apparent_power": 0x2008,
    "power_factor": 0x200A,
    "frequency": 0x200E,

    # Test register (0x206C) — 32-bit float
    "test_register": 0x206C,

    # Totale energie (0x4000 - 0x400D) — 32-bit floats
    "total_energy_import": 0x4000,
    "total_energy_import_2": 0x4002,
    "total_energy_export": 0x400A,
    "total_energy_export_2": 0x400C,
}

# Geldige register ranges (gebaseerd op Growatt queries)
# register 0 count 16 → 0x0000-0x000F
# register 8192 count 32 → 0x2000-0x201F
# register 16384 count 24 → 0x4000-0x4017
# register 8210 count 18 → 0x2012-0x2023
# Node-RED flow schrijft 36 reserved registers vanaf 0x2012 → 0x2012-0x2035
VALID_REGISTER_RANGES = [
    (0x0000, 0x0010),
    (0x2000, 0x2035),
    (0x4000, 0x401F),
]

# Ranges waar ongedefinieerde registers 65535 retourneren (matching Node-RED flow)
DEFAULT_65535_RANGES = [
    (0x2012, 0x2023),
]

# Statische integer registers (niet float, niet gepolled uit HA)
STATIC_REGISTERS = {
    "reserved_0", "firmware_version", "clear_energy", "type_protocol",
    "reserved_4", "communication_protocol", "modbus_address",
    "reserved_7", "reserved_8", "reserved_9", "reserved_10",
    "meter_type", "baudrate",
    "reserved_13", "reserved_14", "reserved_15", "reserved_16",
}

# Float registers (32-bit, 2× 16-bit Modbus registers)
FLOAT_REGISTER_NAMES = {
    "voltage", "current", "active_power", "reactive_power",
    "apparent_power", "power_factor", "frequency",
    "total_energy_import", "total_energy_import_2",
    "total_energy_export", "total_energy_export_2",
    "test_register",
}

# Standaardwaarden (uit de Node-RED flow inject nodes)
DEFAULT_VALUES = {
    # Statische registers
    "reserved_0": 701,
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
    "reserved_13": 0,
    "reserved_14": 1,
    "reserved_15": 108,
    "reserved_16": 101,

    # Meetwaarden (float)
    "voltage": 230.0,
    "current": 0.0,
    "active_power": 0.0,
    "reactive_power": 0.0,
    "apparent_power": 0.0,
    "power_factor": 1.0,
    "frequency": 50.0,

    # Test register (float)
    "test_register": 0.0,

    # Totale energie (float)
    "total_energy_import": 0.0,
    "total_energy_import_2": 0.0,
    "total_energy_export": 0.0,
    "total_energy_export_2": 0.0,
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
FIXED_FREQUENCY = 50.0

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
