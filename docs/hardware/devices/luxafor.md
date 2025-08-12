![BusyLight Project Logo][1]

## Luxafor Flag

The [Luxafor][0] line of products includes three USB connected presence
lights: the Flag, the Mute and the Orb.

### Physical Description

#### Luxafor Flag
The Luxafor Flag is small device with six LEDs and a female mini-USB
port. The main body of the device is rectangular; roughly 1.75 inches
long, 0.5 inches wide and 0.25 inches deep. The device's transluscent
flag defuser sticks out of "top" of the enclosure, roughly 1.25 inches
square and maybe an eighth of an inch in width. There are three
forward firing LEDs which light the flag and three rear firing LEDs
which are easily visible through the opaque enclosure. Lastly, there
is a relatively strong magnet embedded in the enclosure, near the USB
port, which can be used with the supplied adhesive-backed magnet to
"mount" the light.

#### Luxafor Mute

#### Luxafor Orb

#### Luxafor Bluetooth

### Basic Human Interface Device Info

- Vendor ID values:
  - 0x04d8, 0xf372: Flag, Mute, Orb and Bluetooth
- I/O Interface: `HID` write
- Command Length: 8-bytes

### Command Format

The Luxafor family of lights are [USB HID][H] accessible devices whose
attributes are controlled by writing an 8 byte packet to the device.
All four devices share the same product/vendor identifier so they
are discerned by the embedded product string; BT, Flag, Mute, or Orb.

#### Steady Color Command
```C
typedef struct {
  unsigned int command: 8; /* 56:63 */
  unsigned int leds:    8; /* 48:55 */
  unsigned int red:     8; /* 40:47 */
  unsigned int green:   8; /* 32:39 */
  unsigned int blue:    8; /* 24:31 */
  unsigned int pad:    24; /* 00:23 */
} flag_color_cmd_t;
```

#### Fade Color Command
```C
typedef struct {
  unsigned int command: 8; /* 56:63 */
  unsigned int leds:    8; /* 48:55 */
  unsigned int red:     8; /* 40:47 */
  unsigned int green:   8; /* 32:39 */
  unsigned int blue:    8; /* 24:31 */
  unsigned int fade:    8; /* 16:23 */
  unsigned int pad:    16; /* 00:15 */
} flag_fade_cmd_t;
```

#### Strobe Color Command
```C
typedef struct {
  unsigned int command: 8; /* 56:63 */
  unsigned int leds:    8; /* 48:55 */
  unsigned int red:     8; /* 40:47 */
  unsigned int green:   8; /* 32:39 */
  unsigned int blue:    8; /* 24:31 */
  unsigned int speed:   8; /* 16:23 */
  unsigned int pad:     8; /* 08:15 */
  unsigned int repeat   8; /* 00:07
} flag_strobe_cmd_t;
```

#### Wave Color Command
```C
typedef struct {
  unsigned int command: 8; /* 56:63 */
  unsigned int leds:    8; /* 48:55 */
  unsigned int red:     8; /* 40:47 */
  unsigned int green:   8; /* 32:39 */
  unsigned int blue:    8; /* 24:31 */
  unsigned int pad:     8; /* 16:23 */
  unsigned int repeat   8; /* 08:15 */
  unsigned int speed:   8; /* 00:07 */
} flag_wave_cmd_t;
```

#### Pattern Color Command
```C
typedef struct {
  unsigned int command: 8; /* 56:63 */
  unsigned int pattern: 8; /* 48:55 */
  unsigned int repeat:  8; /* 40:47 */
  unsigned int pad  :   8; /* 00:39 */
} flag_pattern_cmd_t;
```


### Device Operation

#### Activating with a RGB Color

#### Turning the Light Off

#### Read Button State - Mute Only

### Observations

### Functionality Wishlist

[0]: https://luxafor.com
[1]: ../assets/Unstacked-Logo-Light.png
[H]: https://github.com/libusb/hidapi
