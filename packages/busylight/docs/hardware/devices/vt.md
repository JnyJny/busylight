![BusyLight Project Logo][1]

## VT DND

The VT DND line of do-not-disturb lights consists of the DND Alpha and
the DND Omega. Support was contributed by the manufacturer in
[PR #831][2]. I do not have either device, so this page is a stub
based on the contributed implementation.

### Physical Description

#### DND Alpha

<!-- missing -->

#### DND Omega

<!-- missing -->

### Basic Human Interface Device Info

- Vendor/Product ID values:
  - 0x340b, 0xf002 : DND Alpha
  - 0x340b, 0xf001 : DND Omega
- I/O Interface: HID `write`
- Command Length: 5 bytes

### Command Format

Each command is a 5-byte HID report: a report number, an action, and
three argument bytes whose meaning depends on the action.

```C
typedef struct {
    unsigned int report: 8; /* 32:39 HID report number, always 0x01 */
    unsigned int action: 8; /* 24:31 Command to execute */
    unsigned int data0:  8; /* 16:23 First argument byte */
    unsigned int data1:  8; /* 08:15 Second argument byte */
    unsigned int data2:  8; /* 00:07 Third argument byte */
} command_t;
```

| Action | Value | Arguments |
|--------|-------|-----------|
| Off | 0x01 | none |
| Flash | 0x02 | data0: 1 breathes red, 2 breathes blue |
| Set Color | 0x04 | data0-data2: red, green, blue |
| Set Brightness | 0x09 | data0: level, 1 (low) to 3 (high) |

### Device Operation

#### Activating with a RGB Color

Write a Set Color command with the RGB values in the argument bytes.

#### Turning the Light Off

Write an Off command with zeroed argument bytes.

#### Changing Brightness

Write a Set Brightness command, wait about 100 milliseconds, then
resend the current color with a Set Color command.

### Observations

The report number is non-zero, so on Windows the leading zero byte
normally prepended to HID writes must be omitted.

The current brightness level cannot be read from the device and
persists between connections. Resetting the light sets level 2.

The Flash command starts a breathing pattern in a fixed color, red
or blue. The color set beforehand is ignored. An Off command sent
while breathing takes effect after the current breath finishes,
about one second later.

A command written immediately after another, with no delay, may be
dropped. A 100 millisecond gap was sufficient in testing.

### Functionality Wishlist

[1]: ../assets/Unstacked-Logo-Light.png
[2]: https://github.com/JnyJny/busylight/pull/831
