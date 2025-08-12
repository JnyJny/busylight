![Busylight Project Logo][0]

## MuteMe

The [MuteMe][1] family of products are designed as physical mute buttons to
control a computer's microphone function. There are three versions of the
MuteMe extant:

- MuteMe Original (prototype)
- MuteMe Original (production)
- MuteMe Mini

I have tested with the MuteMe Origianl (production) batch 1 variant of
the device which was produced during the company's Kickstarter
campaign.

## Physical Description

### MuteMe Original

The MuteMe Original is a cylindrical puck-shaped device, approximately
two inches in diameter and an inch high. The sides of the cylinder are
transluscent and the top is circular metal plate which I guess is
aluminum. The top plate is a capacitance surface which detects touch
events. The device has a female USB-C connector at it's base. The
bottom of the device is opaque, has four grippy feet and a device
information placard affixed to the center.

### Basic Human Interface Device Info

- Vendor/Product ID values:
   - 0x16c0, 0x27db: MuteMe Original (prototype)
   - 0x20a0, 0x42da: MuteMe Original (production)
   - 0x20a0, 0x42db: MuteMe Mini
- I/O Interface: HID `write` and `read`
- Write Command Length: 2-bytes
- Read Command Length: 4-bytes (??)

### Command Format

The MuteMe family of devices are [USB HID][H] accessible devices
whose attributes are controlled by writing a two (2) byte packet to
a device.

The following is a C language structure type definition using bit
fields to illustrate the structure of the 2-byte packet. Examples
for configuring the device for different functions will be given
in C, however they should be very accessible regardless of what
language the reader may be familiar with. 

A structure bit field in C is declared as a member of a `struct`,
usually an `unsigned int`, followed by a width specifier. Fir
instance, the `header` field specified below is an 8-bit (1-byte)
field, while the `sleep` field is a single bit field.

```C
typedef struct {
  unsigned int header:8;   /* 08:15 Constant: 0x00 */

  unsigned int pad0:1;
  unsigned int sleep:1;    /* 06:06 Initiates a ten second sleep mode */
  unsigned int blink:1;	   /* 05:05 Blink */
  unsigned int dim:1;	   /* 04:04 Set is dim, cleared is bright*/
  unsigned int reserved:1; /* 03:03 Reserved for future use. */
  unsigned int blue:1;	   /* 02:02 Set is full value blue */
  unsigned int green:1;	   /* 01:01 Set is full value green */
  unsigned int red:1;      /* 00:00 Set is full value red */
} muteme_ctl_t;
```

### Read Format

TBD

### Device Operation

The device requires the initial byte of the control word to be zero
and control attributes in the following byte.  The device can be written
to and read from. The results of reading the device are the status of the
touch-sensitive button of the device. 

### Activating With a RGB Color

Turning the light on requires the user supply a control word with non-zero
red, blue or green values. The MuteMe family of devices only specifies three
bits for color compared to 24-bits for most other devices. Note also that
the color order for the device is BGR rather than the expected RGB.

**Example: Active Light with White Color.**
```C
muteme_ctl_t cword;
	
cword.red = 1;
cword.green = 1;
cword.blue = 1;
/* write control word to device. */
```

### Turn Light Off

Turning the light off requires zeroing all the color fields and writing
the control word to the device.

### Dimming the Light

The light can be toggled into dim mode by setting the `dim` bit, resuming
bright operation when `dim` is cleared.

### Blink Mode

The light can blink at two different speeds: slow and fast.
Fast blink is indicated by setting blink and clearing dim.
Slow blink is indicated by setting blink and setting dim.

## Observations

The MuteMe Original (production) item I tested with seems to be
somewhat fragile. Writes with unrecognized values can "confuse" the
device and require a hard reboot (removing and reconnecting power via
the USB cable). Reading from the device with a buffer length of less
than 4 or reading at high frequency can also push the device into an
error state that can be recovered by closing and re-opening the device.

While the command word for the device is extremely compact, the
restriction of specifying color with only 3-bits reduces the
flexibility of the device. The light when initially connected via USB
will power up and cycle thru a rainbow spectrum of colors indicating
that the LED lights in the device are at least 24-bit color devices.

With the aid of the [documentation][2] provided by MuteMe.com, I was
able to get this light up and running within a couple of hours of
receiving my test article.

Reading the state of the touch surface has proved elusive. The provided
documentation states that the following values are returned:

- 0x00 Clear
- 0x01 Touching
- 0x02 End Touch
- 0x40 Start Touch


## Functionality Wishlist

Full 24-bit color support would bring this device inline with capabilities 
of other supported devices.


[0]: ../assets/Unstacked-Logo-Light.png
[1]: https://muteme.com
[2]: https://muteme.com/pages/muteme-hid-key
[H]: https://github.com/libusb/hidapi
