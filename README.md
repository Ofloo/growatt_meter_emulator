# CHINT DDSU666 Modbus Emulator

Emulates a CHINT DDSU666 single-phase energy meter via Modbus TCP for Home Assistant.

## Features

- Emulates all registers from the CHINT DDSU666 meter (`0x0001`-`0x400A`)
- Slave ID filtering — only responds to the configured slave ID, others get a timeout (no RST, connection stays open)
- Frequency configurable as a fixed value (e.g. `50.0`) or a Home Assistant entity (e.g. `sensor.netfrequentie`)
- T1 + T2 summation for total energy import/export
- Debug logging with prefix `[growatt_meter_emulator]`
- All static registers (`0x0001`-`0x0010`) configurable via YAML

## Installation

### Via HACS (Recommended)

1. Add this repository to HACS:
   - Go to **HACS** → **Integrations** → **⋮** → **Custom repositories**
   - Enter `https://github.com/Ofloo/growatt_meter_emulator` and select **Integration**
   - Click **Install**
2. Restart Home Assistant

### Manual Installation

1. Copy the `custom_components/chint_ddsu666/` directory to your Home Assistant `config/custom_components/` directory
2. Restart Home Assistant

## Configuration

See [`configuration.sample.yaml`](configuration.sample.yaml) for a full example with all options.

### Minimal Configuration

```yaml
chint_ddsu666:
  modbus:
    host: "0.0.0.0"
    port: 502
    slave_id: 3
  home_assistant:
    voltage_entity: "sensor.slimme_meter_voltage"
    current_entity: "sensor.slimme_meter_current"
```

### Frequency as Entity

```yaml
chint_ddsu666:
  modbus:
    host: "0.0.0.0"
    port: 502
    slave_id: 3
  home_assistant:
    voltage_entity: "sensor.slimme_meter_voltage"
    current_entity: "sensor.slimme_meter_current"
  registers:
    frequency: "sensor.netfrequentie"
```

### Frequency as Fixed Value (60 Hz)

```yaml
chint_ddsu666:
  modbus:
    host: "0.0.0.0"
    port: 502
    slave_id: 3
  home_assistant:
    voltage_entity: "sensor.slimme_meter_voltage"
    current_entity: "sensor.slimme_meter_current"
  registers:
    frequency: 60.0
```

## Testing

Use `mbpoll` to test the emulator:

```bash
# Test firmware version (register 0x0001)
mbpoll -a 3 -r 1 -c 1 -t 3 -0 -p 502 127.0.0.1

# Test voltage (register 0x2000)
mbpoll -a 3 -r 8192 -c 2 -t 4:float -0 -p 502 127.0.0.1

# Test unconfigured slave ID (4) — should timeout
mbpoll -a 4 -r 1 -c 1 -t 3 -0 -p 502 127.0.0.1

# Test undefined register (0x1234) — should return Illegal data address
mbpoll -a 3 -r 4660 -c 1 -t 3 -0 -p 502 127.0.0.1
```

Or use the included test script:

```bash
chmod +x test_modbus_emulator.sh
./test_modbus_emulator.sh 127.0.0.1 502 3
```

## Register Table

| Register  | Description               | Type               | Conversion          | Default |
|-----------|---------------------------|--------------------|---------------------|---------|
| `0x0001`  | Firmware version          | 16-bit integer     | None                | `504`   |
| `0x0002`  | CLr.E (clear energy)      | 16-bit integer     | None                | `0`     |
| `0x0003`  | Type Protocol             | 16-bit integer     | None                | `166`   |
| `0x0004`  | Reserved                  | 16-bit integer     | None                | `5`     |
| `0x0005`  | Communication protocol    | 16-bit integer     | None                | `5`     |
| `0x0006`  | Modbus address (slave ID) | 16-bit integer     | None                | `3`     |
| `0x0007`  | Reserved                  | 16-bit integer     | None                | `10`    |
| `0x0008`  | Reserved                  | 16-bit integer     | None                | `1`     |
| `0x0009`  | Reserved                  | 16-bit integer     | None                | `5`     |
| `0x000A`  | Reserved                  | 16-bit integer     | None                | `0`     |
| `0x000B`  | Meter Type                | 16-bit integer     | None                | `166`   |
| `0x000C`  | Baudrate                  | 16-bit integer     | None                | `3`     |
| `0x2000`  | Voltage (V)               | 32-bit float       | IEEE754 big-endian  | —       |
| `0x2002`  | Current (A)               | 32-bit float       | IEEE754 big-endian  | —       |
| `0x2004`  | Active power (kW)         | 32-bit float       | ×0.001              | —       |
| `0x2006`  | Reactive power (kVAR)     | 32-bit float       | ×0.001              | —       |
| `0x2008`  | Apparent power (kVA)      | 32-bit float       | ×0.001              | —       |
| `0x200A`  | Power Factor (cos φ)      | 32-bit float       | IEEE754 big-endian  | —       |
| `0x200E`  | Frequency (Hz)            | 32-bit float       | IEEE754 big-endian  | `50.0`  |
| `0x4000`  | Total energy import (kWh) | 32-bit float       | IEEE754 big-endian  | —       |
| `0x400A`  | Total energy export (kWh) | 32-bit float       | IEEE754 big-endian  | —       |

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Modbus server not starting | Check if port `502` is already in use: `netstat -tulnp \| grep 502` |
| Timeout for configured slave ID | Verify `slave_id` in `configuration.yaml` matches the test |
| Invalid register values | Check validation rules in `const.py` (e.g. `baudrate` must be `0`-`3`) |
| Frequency not working | Ensure `frequency` is either a number or a valid entity ID |
| Energy import/export not working | Verify T1 and T2 entities are set and contain numeric values |

## License

MIT
