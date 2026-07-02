#!/bin/bash
# Testscript voor de CHINT DDSU666 Modbus-emulator met mbpoll.
# Gebruik: ./test_modbus_emulator.sh [IP] [PORT] [SLAVE_ID]
# Voorbeeld: ./test_modbus_emulator.sh 10.13.35.10 502 3

IP=${1:-10.13.35.10}    # Standaard: huidige emulator
PORT=${2:-502}          # Standaard: poort 502
SLAVE_ID=${3:-3}        # Standaard: slave ID 3

echo "=== Testing Modbus Emulator (CHINT DDSU666) ==="
echo "IP: $IP, Port: $PORT, Slave ID: $SLAVE_ID"
echo ""

# Test 1: Firmwareversie (register 0x0001, 16-bit integer)
echo "Test 1: Firmwareversie (register 0x0001)"
mbpoll -a "$SLAVE_ID" -r 1 -c 1 -t 3 -0 -p "$PORT" "$IP"
echo ""

# Test 2: CLr.E (register 0x0002, 16-bit integer)
echo "Test 2: CLr.E (register 0x0002)"
mbpoll -a "$SLAVE_ID" -r 2 -c 1 -t 3 -0 -p "$PORT" "$IP"
echo ""

# Test 3: Type Protocol (register 0x0003, 16-bit integer)
echo "Test 3: Type Protocol (register 0x0003)"
mbpoll -a "$SLAVE_ID" -r 3 -c 1 -t 3 -0 -p "$PORT" "$IP"
echo ""

# Test 4: Communicatieprotocol (register 0x0005, 16-bit integer)
echo "Test 4: Communicatieprotocol (register 0x0005)"
mbpoll -a "$SLAVE_ID" -r 5 -c 1 -t 3 -0 -p "$PORT" "$IP"
echo ""

# Test 5: Modbus-adres (register 0x0006, 16-bit integer)
echo "Test 5: Modbus-adres (register 0x0006)"
mbpoll -a "$SLAVE_ID" -r 6 -c 1 -t 3 -0 -p "$PORT" "$IP"
echo ""

# Test 6: Meter Type (register 0x000B, 16-bit integer)
echo "Test 6: Meter Type (register 0x000B)"
mbpoll -a "$SLAVE_ID" -r 11 -c 1 -t 3 -0 -p "$PORT" "$IP"
echo ""

# Test 7: Baudrate (register 0x000C, 16-bit integer)
echo "Test 7: Baudrate (register 0x000C)"
mbpoll -a "$SLAVE_ID" -r 12 -c 1 -t 3 -0 -p "$PORT" "$IP"
echo ""

# Test 8: Spanning (register 0x2000, 32-bit float)
echo "Test 8: Spanning (register 0x2000-0x2001)"
mbpoll -a "$SLAVE_ID" -r 8192 -c 2 -t 4:float -0 -p "$PORT" "$IP"
echo ""

# Test 9: Stroom (register 0x2002, 32-bit float)
echo "Test 9: Stroom (register 0x2002-0x2003)"
mbpoll -a "$SLAVE_ID" -r 8194 -c 2 -t 4:float -0 -p "$PORT" "$IP"
echo ""

# Test 10: Actief vermogen (register 0x2004, 32-bit float)
echo "Test 10: Actief vermogen (register 0x2004-0x2005)"
mbpoll -a "$SLAVE_ID" -r 8196 -c 2 -t 4:float -0 -p "$PORT" "$IP"
echo ""

# Test 11: Reactief vermogen (register 0x2006, 32-bit float)
echo "Test 11: Reactief vermogen (register 0x2006-0x2007)"
mbpoll -a "$SLAVE_ID" -r 8198 -c 2 -t 4:float -0 -p "$PORT" "$IP"
echo ""

# Test 12: Schijnbaar vermogen (register 0x2008, 32-bit float)
echo "Test 12: Schijnbaar vermogen (register 0x2008-0x2009)"
mbpoll -a "$SLAVE_ID" -r 8200 -c 2 -t 4:float -0 -p "$PORT" "$IP"
echo ""

# Test 13: Power Factor (register 0x200A, 32-bit float)
echo "Test 13: Power Factor (register 0x200A-0x200B)"
mbpoll -a "$SLAVE_ID" -r 8202 -c 2 -t 4:float -0 -p "$PORT" "$IP"
echo ""

# Test 14: Frequentie (register 0x200E, 32-bit float)
echo "Test 14: Frequentie (register 0x200E-0x200F)"
mbpoll -a "$SLAVE_ID" -r 8206 -c 2 -t 4:float -0 -p "$PORT" "$IP"
echo ""

# Test 15: Totale energie import (register 0x4000, 32-bit float)
echo "Test 15: Totale energie import (register 0x4000-0x4001)"
mbpoll -a "$SLAVE_ID" -r 16384 -c 2 -t 4:float -0 -p "$PORT" "$IP"
echo ""

# Test 16: Totale energie export (register 0x400A, 32-bit float)
echo "Test 16: Totale energie export (register 0x400A-0x400B)"
mbpoll -a "$SLAVE_ID" -r 16394 -c 2 -t 4:float -0 -p "$PORT" "$IP"
echo ""

# Test 17: Niet-geconfigureerde slave ID (4) - Moet timeout geven
echo "Test 17: Niet-geconfigureerde slave ID (4) - Moet timeout geven"
mbpoll -a 4 -r 1 -c 1 -t 3 -0 -p "$PORT" "$IP"
echo ""

# Test 18: Ongedefinieerd register (0x1234) - Moet Illegal data address geven
echo "Test 18: Ongedefinieerd register (0x1234) - Moet Illegal data address geven"
mbpoll -a "$SLAVE_ID" -r 4660 -c 1 -t 3 -0 -p "$PORT" "$IP"
echo ""

echo "=== Test voltooid ==="
