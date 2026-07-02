"""Modbus TCP-server voor de CHINT DDSU666 emulator.

Slave ID-filtering gebaseerd op Modbus-proxy (silent drop, geen RST, connectie blijft open).
Registerdefinities en data-conversie gebaseerd op de Node-RED flow.
"""

import socket
import struct
import threading
import logging
from typing import Optional

from .const import (
    DEFAULT_HOST,
    DEFAULT_PORT,
    DEFAULT_SLAVE_ID,
    DEFAULT_TIMEOUT,
    REGISTERS,
    DEFAULT_VALUES,
    CONVERSION_FACTORS,
    FLOAT_REGISTER_NAMES,
    STATIC_REGISTERS,
    VALID_REGISTER_RANGES,
    DEFAULT_65535_RANGES,
    FUNC_READ_HOLDING_REGISTERS,
    FUNC_WRITE_SINGLE_REGISTER,
    FUNC_WRITE_MULTIPLE_REGISTERS,
    EXCEPTION_ILLEGAL_FUNCTION,
    EXCEPTION_ILLEGAL_DATA_ADDRESS,
)
from .data_converter import float_to_modbus

logger = logging.getLogger(__name__)


class ModbusServer:
    """Modbus TCP-server die de CHINT DDSU666 emuleert."""

    def __init__(
        self,
        host: str = DEFAULT_HOST,
        port: int = DEFAULT_PORT,
        slave_id: int = DEFAULT_SLAVE_ID,
        timeout: int = DEFAULT_TIMEOUT,
        debug: bool = False,
    ):
        self.host = host
        self.port = port
        self.slave_id = slave_id
        self.timeout = timeout
        self.debug = debug

        self._register_values: dict[int, int] = {}
        self._server_socket: Optional[socket.socket] = None
        self._running = False

        self._init_register_values()

    def _init_register_values(self) -> None:
        """Initialiseer de registerwaarden met standaardwaarden uit de Node-RED flow."""
        for name, address in REGISTERS.items():
            if name not in DEFAULT_VALUES:
                continue
            if name in FLOAT_REGISTER_NAMES:
                value = DEFAULT_VALUES[name]
                high_word, low_word = float_to_modbus(value)
                self._register_values[address] = high_word
                self._register_values[address + 1] = low_word
            else:
                self._register_values[address] = int(DEFAULT_VALUES[name])

    def _is_valid_register(self, addr: int) -> bool:
        """Controleer of een registeradres binnen de geldige ranges valt."""
        for start, end in VALID_REGISTER_RANGES:
            if start <= addr <= end:
                return True
        return False

    def _log(self, level: int, message: str) -> None:
        """Log een bericht met de [growatt_meter_emulator] prefix."""
        logger.log(level, "[growatt_meter_emulator]: %s", message)

    def update_register(self, name: str, value: float) -> None:
        """Update een register met een nieuwe waarde (vanuit Home Assistant)."""
        address = REGISTERS.get(name)
        if address is None:
            self._log(logging.WARNING, f"Onbekend register: {name}")
            return

        if name in CONVERSION_FACTORS:
            value = value * CONVERSION_FACTORS[name]

        high_word, low_word = float_to_modbus(value)
        self._register_values[address] = high_word
        self._register_values[address + 1] = low_word

        if self.debug:
            self._log(
                logging.DEBUG,
                f"Register {name} (0x{address:04X}) bijgewerkt naar {value}",
            )

    def start(self) -> None:
        """Start de Modbus TCP-server."""
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._server_socket.bind((self.host, self.port))
        self._server_socket.listen(5)
        self._running = True

        self._log(
            logging.INFO,
            f"Modbus-server gestart op {self.host}:{self.port} (slave ID: {self.slave_id})",
        )

        while self._running:
            try:
                client_socket, client_address = self._server_socket.accept()
                if self.debug:
                    self._log(
                        logging.DEBUG,
                        f"Nieuwe connectie van {client_address}",
                    )
                threading.Thread(
                    target=self._handle_client,
                    args=(client_socket,),
                    daemon=True,
                ).start()
            except OSError:
                if not self._running:
                    break

    def stop(self) -> None:
        """Stop de Modbus TCP-server."""
        self._running = False
        if self._server_socket:
            self._server_socket.close()
        self._log(logging.INFO, "Modbus-server gestopt")

    def _handle_client(self, client_socket: socket.socket) -> None:
        """Verwerk een client-connectie (thread per connectie)."""
        unit_id = None
        try:
            while True:
                header = b""
                while len(header) < 6:
                    chunk = client_socket.recv(6 - len(header))
                    if not chunk:
                        return
                    header += chunk

                length = int.from_bytes(header[4:6], byteorder="big")

                unit_id_byte = client_socket.recv(1)
                if not unit_id_byte:
                    return
                unit_id = unit_id_byte[0]

                remaining_length = length - 1
                remaining_data = b""
                while len(remaining_data) < remaining_length:
                    chunk = client_socket.recv(
                        remaining_length - len(remaining_data)
                    )
                    if not chunk:
                        break
                    remaining_data += chunk

                full_frame = header + unit_id_byte + remaining_data

                if unit_id != self.slave_id:
                    if self.debug:
                        self._log(
                            logging.DEBUG,
                            f"Request voor niet-geconfigureerde slave ID {unit_id} genegeerd",
                        )
                    try:
                        client_socket.settimeout(self.timeout)
                        while True:
                            data = client_socket.recv(1024)
                            if not data:
                                break
                    except socket.timeout:
                        pass
                    return

                response = self._process_request(full_frame)
                if response:
                    client_socket.sendall(response)

        except Exception as e:
            if self.debug:
                self._log(logging.ERROR, f"Fout bij verwerken client: {e}")
        finally:
            if unit_id is None or unit_id == self.slave_id:
                try:
                    client_socket.close()
                except OSError:
                    pass

    def _process_request(self, request: bytes) -> Optional[bytes]:
        """Verwerk een Modbus-request en retourneer een response."""
        if len(request) < 8:
            return None

        transaction_id = request[0:2]
        protocol_id = request[2:4]
        unit_id = request[6]
        function_code = request[7]

        if self.debug:
            self._log(
                logging.DEBUG,
                f"Functie {function_code} ontvangen voor slave ID {unit_id}",
            )

        if function_code == FUNC_READ_HOLDING_REGISTERS:
            return self._handle_read_holding_registers(
                transaction_id, protocol_id, unit_id, request
            )
        elif function_code == FUNC_WRITE_SINGLE_REGISTER:
            return self._handle_write_single_register(
                transaction_id, protocol_id, unit_id, request
            )
        elif function_code == FUNC_WRITE_MULTIPLE_REGISTERS:
            return self._handle_write_multiple_registers(
                transaction_id, protocol_id, unit_id, request
            )
        else:
            return self._build_exception_response(
                transaction_id, protocol_id, unit_id,
                function_code, EXCEPTION_ILLEGAL_FUNCTION,
            )

    def _handle_read_holding_registers(
        self,
        transaction_id: bytes,
        protocol_id: bytes,
        unit_id: int,
        request: bytes,
    ) -> bytes:
        """Verwerk een Read Holding Registers request (functie 0x03)."""
        if len(request) < 12:
            return self._build_exception_response(
                transaction_id, protocol_id, unit_id,
                FUNC_READ_HOLDING_REGISTERS, EXCEPTION_ILLEGAL_DATA_VALUE,
            )

        start_address = int.from_bytes(request[8:10], byteorder="big")
        quantity = int.from_bytes(request[10:12], byteorder="big")

        if self.debug:
            self._log(
                logging.DEBUG,
                f"Lees register 0x{start_address:04X}, aantal: {quantity}",
            )

        for offset in range(quantity):
            addr = start_address + offset
            if not self._is_valid_register(addr):
                self._log(
                    logging.WARNING,
                    f"Register buiten bereik aangeroepen: 0x{addr:04X}",
                )
                return self._build_exception_response(
                    transaction_id, protocol_id, unit_id,
                    FUNC_READ_HOLDING_REGISTERS, EXCEPTION_ILLEGAL_DATA_ADDRESS,
                )

        byte_count = quantity * 2
        response = bytearray()
        response.extend(transaction_id)
        response.extend(protocol_id)
        response.extend((byte_count + 3).to_bytes(2, byteorder="big"))
        response.append(unit_id)
        response.append(FUNC_READ_HOLDING_REGISTERS)
        response.append(byte_count)

        for offset in range(quantity):
            addr = start_address + offset
            if any(start <= addr <= end for start, end in DEFAULT_65535_RANGES):
                value = self._register_values.get(addr, 65535)
            else:
                value = self._register_values.get(addr, 0)
            response.extend(struct.pack('>H', value & 0xFFFF))

        return bytes(response)

    def _handle_write_single_register(
        self,
        transaction_id: bytes,
        protocol_id: bytes,
        unit_id: int,
        request: bytes,
    ) -> bytes:
        """Verwerk een Write Single Register request (functie 0x06)."""
        if len(request) < 12:
            return self._build_exception_response(
                transaction_id, protocol_id, unit_id,
                FUNC_WRITE_SINGLE_REGISTER, EXCEPTION_ILLEGAL_DATA_VALUE,
            )

        register_address = int.from_bytes(request[8:10], byteorder="big")
        register_value = int.from_bytes(request[10:12], byteorder="big")

        if self.debug:
            self._log(
                logging.DEBUG,
                f"Schrijf register 0x{register_address:04X} = {register_value}",
            )

        if not self._is_valid_register(register_address):
            self._log(
                logging.WARNING,
                f"Ongedefinieerd register aangeroepen voor schrijfactie: 0x{register_address:04X}",
            )
            return self._build_exception_response(
                transaction_id, protocol_id, unit_id,
                FUNC_WRITE_SINGLE_REGISTER, EXCEPTION_ILLEGAL_DATA_ADDRESS,
            )

        self._register_values[register_address] = register_value
        return request

    def _handle_write_multiple_registers(
        self,
        transaction_id: bytes,
        protocol_id: bytes,
        unit_id: int,
        request: bytes,
    ) -> bytes:
        """Verwerk een Write Multiple Registers request (functie 0x10)."""
        if len(request) < 13:
            return self._build_exception_response(
                transaction_id, protocol_id, unit_id,
                FUNC_WRITE_MULTIPLE_REGISTERS, EXCEPTION_ILLEGAL_DATA_VALUE,
            )

        start_address = int.from_bytes(request[8:10], byteorder="big")
        quantity = int.from_bytes(request[10:12], byteorder="big")
        byte_count = request[12]

        if self.debug:
            self._log(
                logging.DEBUG,
                f"Schrijf meerdere registers vanaf 0x{start_address:04X}, aantal: {quantity}",
            )

        for i in range(quantity):
            addr = start_address + i
            if not self._is_valid_register(addr):
                self._log(
                    logging.WARNING,
                    f"Ongedefinieerd register aangeroepen voor schrijfactie: 0x{addr:04X}",
                )
                return self._build_exception_response(
                    transaction_id, protocol_id, unit_id,
                    FUNC_WRITE_MULTIPLE_REGISTERS, EXCEPTION_ILLEGAL_DATA_ADDRESS,
                )

        for i in range(quantity):
            addr = start_address + i
            offset = 13 + i * 2
            value = int.from_bytes(request[offset:offset + 2], byteorder="big")
            self._register_values[addr] = value

        response = bytearray()
        response.extend(transaction_id)
        response.extend(protocol_id)
        response.extend((6).to_bytes(2, byteorder="big"))
        response.append(unit_id)
        response.append(FUNC_WRITE_MULTIPLE_REGISTERS)
        response.extend(start_address.to_bytes(2, byteorder="big"))
        response.extend(quantity.to_bytes(2, byteorder="big"))

        return bytes(response)

    def _build_exception_response(
        self,
        transaction_id: bytes,
        protocol_id: bytes,
        unit_id: int,
        function_code: int,
        exception_code: int,
    ) -> bytes:
        """Bouw een Modbus-exception response."""
        response = bytearray()
        response.extend(transaction_id)
        response.extend(protocol_id)
        response.extend((3).to_bytes(2, byteorder="big"))
        response.append(unit_id)
        response.append(function_code | 0x80)
        response.append(exception_code)
        return bytes(response)
