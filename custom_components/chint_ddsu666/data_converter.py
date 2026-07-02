"""Data-conversie voor de CHINT DDSU666 Modbus-emulator.

IEEE754 float32 (big-endian) ↔ twee 16-bit Modbus-registers.
Gebaseerd op de Node-RED flow logica.
"""

import struct


def float_to_modbus(value: float) -> tuple[int, int]:
    """Converteer een float naar twee 16-bit Modbus-registers (big-endian).

    Voorbeeld: 230.5 → (0x4366, 0x8000)
    """
    packed = struct.pack(">f", value)
    return struct.unpack(">HH", packed)


def modbus_to_float(high_word: int, low_word: int) -> float:
    """Converteer twee 16-bit Modbus-registers naar een float (big-endian).

    Voorbeeld: (0x4366, 0x8000) → 230.5
    """
    packed = struct.pack(">HH", high_word, low_word)
    return struct.unpack(">f", packed)[0]


def int16_to_modbus(value: int) -> int:
    """Converteer een 16-bit signed integer naar Modbus-formaat.

    Uit de Node-RED flow: als bit 15 geset is, corrigeer naar signed.
    """
    if value & 0x8000:
        value = value - 0x10000
    return value & 0xFFFF
