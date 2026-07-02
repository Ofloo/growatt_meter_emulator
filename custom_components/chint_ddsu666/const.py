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

    # Meetwaarden (0x2000 - 0x200E) — 32-bit floats
    "voltage": 0x2000,
    "current": 0x2002,
    "active_power": 0x2004,
    "reactive_power": 0x2006,
    "apparent_power": 0x2008,
    "power_factor": 0x200A,
    "frequency": 0x200E,

    # Totale energie (0x4000 - 0x400A) — 32-bit floats
    "total_energy_import": 0x4000,
    "total_energy_export": 0x400A,

    # Ongedefinieerde registers (0x2010 - 0x201F) — retourneren 65535
    "unknown_2010": 0x2010,
    "unknown_2012": 0x2012,
    "unknown_2014": 0x2014,
    "unknown_2016": 0x2016,
    "unknown_2018": 0x2018,
    "unknown_201A": 0x201A,
    "unknown_201C": 0x201C,
    "unknown_201E": 0x201E,

    # Ongedefinieerde registers (0x4002 - 0x401F) — retourneren 65535
    "unknown_4002": 0x4002,
    "unknown_4004": 0x4004,
    "unknown_4006": 0x4006,
    "unknown_4008": 0x4008,
    "unknown_400C": 0x400C,
    "unknown_400E": 0x400E,
    "unknown_4010": 0x4010,
    "unknown_4012": 0x4012,
    "unknown_4014": 0x4014,
    "unknown_4016": 0x4016,
    "unknown_4018": 0x4018,
    "unknown_401A": 0x401A,
    "unknown_401C": 0x401C,
    "unknown_401E": 0x401E,
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

    # Meetwaarden (0x2000 - 0x200E) — 32-bit floats
    "voltage": 230.0,
    "current": 0.0,
    "active_power": 0.0,
    "reactive_power": 0.0,
    "apparent_power": 0.0,
    "power_factor": 1.0,
    "frequency": 50.0,

    # Totale energie (0x4000 - 0x400A) — 32-bit floats
    "total_energy_import": 0.0,
    "total_energy_export": 0.0,

    # Ongedefinieerde registers — retourneren 65535
    "unknown_2010": 65535,
    "unknown_2012": 65535,
    "unknown_2014": 65535,
    "unknown_2016": 65535,
    "unknown_2018": 65535,
    "unknown_201A": 65535,
    "unknown_201C": 65535,
    "unknown_201E": 65535,
    "unknown_4002": 65535,
    "unknown_4004": 65535,
    "unknown_4006": 65535,
    "unknown_4008": 65535,
    "unknown_400C": 65535,
    "unknown_400E": 65535,
    "unknown_4010": 65535,
    "unknown_4012": 65535,
    "unknown_4014": 65535,
    "unknown_4016": 65535,
    "unknown_4018": 65535,
    "unknown_401A": 65535,
    "unknown_401C": 65535,
    "unknown_401E": 65535,
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
