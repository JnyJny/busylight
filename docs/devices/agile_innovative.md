![BusyLight Project Logo][1]

## Agile Innovative LTD BlinkStick

Agile Innovative LTD offers a variety of [BlinkStick][0] branded
products: the BlinkStick, the Nano, the Flex, the Square, the Strip
and the Pro. I worked with the BlinkStick Square.

### Physical Description

#### BlinkStick Square

The BlinkStick Square is a roughly one inch square device with a
USB-mini female connector and eight upward firing LEDs, arranged two
on each side of the square. I purchased the optional diffuser, a 3d
printed opaque cube roughly an inch on a side. 

### Basic Human Interface Device Info

- Vendor ID values:
  - 0x20a0, 0x41e5: BlinkStick
- I/O Interface: `HID` write
- Command Length: variable

### Device Operation

The BlinkStick family of devices is controlled by writing the appropriate
command buffer to the device. Command buffers all start with a report
value which indicates the format and length of the buffer.


#### Command Formats

The BlinkStick command protocol supports many different physical
implementations that vary by the number of addressable LEDs. The
command format has variable length and format and is determined
by the value of the first byte labled 'report'. The following
report values known are:

```C
typedef enum {
  SINGLE  = 1,
  MODE    = 4,
  INDEXED = 5,
  LEDS8   = 6,
  LEDS16  = 7,
  LEDS32  = 8,
  LEDS64  = 9,
} blinkstick_report_t;
```

The `channel` field is documented as 8-bit value that can take on
three values; 0:red, 1:green, 2: blue. It not docummented what the
channel value effects and values other than zero result in no
change to LED color values on a BlinkStick Square.

###### Single LED Command
This command is used to update the RGB values of the first LED.

```C
typedef struct {
    unsigned int report: 8; /* 24:31 CONSTANT SINGLE */
    unsigned int red:    8; /* 16:23 */
    unsigned int green:  8; /* 08:15 */
    unsigned int blue:   8; /* 00:07 */
} blinkstick_led0_t;
```

###### Indexed LED Command
This command is used to update the RGB values of the LED selected by
`index`.

```C
typedef struct {
    unsigned int report:  8; /* 40:47  CONSTANT INDEXED */
    unsigned int channel: 8; /* 32:39 */
    unsigned int index:   8; /* 24:31 */
    unsigned int red:     8; /* 16:23 */
    unsigned int green:   8; /* 08:15 */
    unsigned int blue:    8; /* 00:07 */
} blinkstick_indexed_led_t;
```

###### Eight LED Dataframe
This command is used to update the RGB values of 8 LEDs
with one write operation.

```C
typedef struct {
    unsigned int report:  8; /*200:207 CONSTANT LEDS8*/
    unsigned int channel: 8; /*192:199 */
    unsigned int led0:   24; /*168:024 LED 0 24-bit color */
    unsigned int led1:   24; /*144:167 LED 1 24-bit color */
    unsigned int led2:   24; /*120:143 LED 2 24-bit color */
    unsigned int led3:   24; /*096:119 LED 3 24-bit color */
    unsigned int led4:   24; /*072:095 LED 4 24-bit color */
    unsigned int led5:   24; /*048:071 LED 5 24-bit color */
    unsigned int led6:   24; /*024:047 LED 6 24-bit color */
    unsigned int led7:   24; /*000:023 LED 7 24-bit color */
} blinkstick_dataframe8_t;
```

###### Sixteen LED Dataframe
This command is used to update the RGB values of 16 LEDs
with one write operation.
```C
typedef struct {
   unsigned int report:  8; /* CONSTANT LEDS16 */
   unsigned int channel: 8;
   unsigned int led0:    24;
   ...
   unsigned int led15:    24;
} blinkstick_dataframe16_t;
```

###### Thirty-two LED Dataframe
This command is used to update the RGB values of 32 LEDs
with one write operation.
```C
typedef struct {
   unsigned int report:  8; /* CONSTANT LEDS32 */
   unsigned int channel: 8;
   unsigned int led0:    24;
   ...
   unsigned int led31:    24;
} blinkstick_dataframe32_t;

```

###### Sixty-four LED Dataframe
This command is used to update the RGB values of 64 LEDs
with one write operation.
```C
typedef struct {
   unsigned int report:  8; /* CONSTANT LEDS64 */
   unsigned int channel: 8;
   unsigned int led0:    24;
   ...
   unsigned int led63:    24;
} blinkstick_dataframe64_t;
```


#### Activating With a RGB Color

The following activates all eight LEDs of a BlinkLight Square with the
color '#aabbcc'. Note that the 24-bit color value written to the
device has the red and green bytes swapped in order from #RRGGBB to
#GGRRBB.

```C
    int color;
    int r, g, b;

    blinkstick_dataframe8_t df;
    df.report = 6;
    df.channel = 0;

    color = 0xaabbcc;
    r = (color >> 16) & 0xff;
    g = (color >> 8) & 0xff;
    b = (color & 0xff)
    color = (g<<16) | (r<<8) | b;

    df.led0 = color;
    df.led1 = color;
    df.led2 = color;
    df.led3 = color;
    df.led4 = color;
    df.led5 = color;
    df.led6 = color;
    df.led7 = color;
    /* write the dataframe to the device */
```

#### Turning the Light Off

The light can be turned off by building a dataframe whose red, green,
and blue values are zero and writing it to the device.

#### Blinking The Light On and Off

The BlinkStick family of devices has a command set that is limited to
activating or deactivating lights, so it is necessary to activately
animate the blink effect by sending alternating on and off dataframes
sized appropriately for the number of LEDs on the device.


### Observations

The BlinkStick family of products is relatively unique in that it
provides access to individual LEDs on a device. Unfortunately, this
flexibility tends to make it somewhat cumbersome to work with. The
documentation for the BlinkStick family is lacking, although there are
many different open source reference implementations in a variety of
languages.

### Functionality Wishlist

The main missing functionality, with respect to BusyLight, is the lack of
a builtin blink operation.

[0]: https://blinkstick.com
[1]: ../assets/Unstacked-Logo-Light.png
[H]: https://github.com/libusb/hidapi
