![BusyLight Project Logo][1]

## Embrava Early Blynclight Models (VID 0x1130)

These are early Blynclight USB status lights with vendor ID 0x1130, predating
the Embrava rebrand. They use different protocols than the newer Embrava
Blynclight family (VID 0x2C0D).

Two variants are supported:
- **BLYNCUSB10** (PID 0x0001, 0x0002): Uses the blynux 8-byte protocol
- **BLYNCUSB20** (PID 0x1E00): Uses the TENX20 2-byte protocol

### Physical Description

Early Blynclight models with an LED indicator light, labeled "Blync" on the
front with www.blynclight.com URL, and model number on the bottom.

### Basic Human Interface Device Info

| Variant | VID | PID | Interface | Protocol |
|---------|-----|-----|-----------|----------|
| BLYNCUSB10 | 0x1130 | 0x0001 | 1 | Blynux 8-byte feature report |
| BLYNCUSB10 | 0x1130 | 0x0002 | 1 | Blynux 8-byte feature report |
| BLYNCUSB20 | 0x1130 | 0x1E00 | 1 | TENX20 65-byte HID write |

All variants support the same 7 predefined colors plus OFF.

### Available Colors

| Color   | Blynux Value | TENX20 Code |
|---------|--------------|-------------|
| WHITE   | 0x8          | 0x07        |
| CYAN    | 0x9          | 0x17        |
| MAGENTA | 0xA          | 0x20        |
| BLUE    | 0xB          | 0x35        |
| YELLOW  | 0xC          | 0x40        |
| GREEN   | 0xD          | 0xD8        |
| RED     | 0xE          | 0x60        |
| OFF     | 0xF          | 0x73        |

---

## BLYNCUSB10 Protocol (PID 0x0001, 0x0002)

This protocol was reverse-engineered and documented in the
[blynux project](https://github.com/ticapix/blynux).

### Command Format

The command is an 8-byte payload sent via USB HID feature report:

```C
typedef struct {
    unsigned int header[7]; /* Bytes 0-6: Constant 0x55, 0x53, 0x42, 0x43, 0x00, 0x40, 0x02 */
    unsigned int color:  4; /* Bits 4-7 of byte 7: Color value from table above */
    unsigned int footer: 4; /* Bits 0-3 of byte 7: Constant 0xF */
} blynux_ctrl_t;
```

The base command payload is: `{ 0x55, 0x53, 0x42, 0x43, 0x00, 0x40, 0x02, 0x0F }`

To set a color, the color value is shifted left by 4 bits and ORed with the
footer nibble:

```C
data[7] = (color_mask << 4) | 0x0F;
```

### USB Transfer Details

- bmRequestType: 0x21 (Host-to-device, Class, Interface)
- bRequest: 9 (SET_REPORT)
- wValue: 0x0200
- wIndex: 1
- wLength: 8

This corresponds to a HID SET_REPORT request, which is handled via
`send_feature_report` in the busylight-core library.

---

## BLYNCUSB20 Protocol (PID 0x1E00) - TENX20 Chipset

This protocol was discovered by decompiling the official Blynclight.dll SDK.
The TENX20 chipset uses a simpler two-step command protocol.

### Command Format

Commands are sent as 65-byte HID writes on interface 1:
- Byte 0: Report ID (0x00)
- Byte 1: Control code
- Bytes 2-64: Padding (0x00)

### Two-Step Command Sequence

To set a color, two commands must be sent in sequence:

1. **Reset/Prepare Command**: Send control code `0x73`
2. **Color Command**: Send the TENX20 color code from the table above

```python notest
# Example: Set light to RED
buffer = bytes([0x00, 0x73] + [0] * 63)  # Step 1: Reset
device.write(buffer)

buffer = bytes([0x00, 0x60] + [0] * 63)  # Step 2: RED (0x60)
device.write(buffer)
```

---

## Linux udev Rules

To use the device without root privileges on Linux, add the following
udev rules to `/etc/udev/rules.d/10-blyncusb.rules`:

```
SUBSYSTEM=="input", GROUP="input", MODE="0666"
SUBSYSTEM=="usb", ATTRS{idVendor}=="1130", ATTRS{idProduct}=="0001", MODE:="666", GROUP="plugdev"
SUBSYSTEM=="usb", ATTRS{idVendor}=="1130", ATTRS{idProduct}=="0002", MODE:="666", GROUP="plugdev"
SUBSYSTEM=="usb", ATTRS{idVendor}=="1130", ATTRS{idProduct}=="1e00", MODE:="666", GROUP="plugdev"
```

## Limitations

- No full RGB color control - only 7 predefined colors
- No audio/sound playback capability
- No flash/blink patterns (must be implemented in software)
- No dim/bright control

## References

- [Blynux GitHub Repository](https://github.com/ticapix/blynux) - BLYNCUSB10 protocol
- Decompiled Blynclight.dll SDK - TENX20 protocol for PID 0x1E00

[1]: ../../assets/Unstacked-Logo-Light.png
