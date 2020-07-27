![BusyLight Project Logo][1]

The [BusyLight for Humans™][0] project provides a common interface to
several types of USB connected LED lights from multiple vendors:

- [Embrava][2] BlyncLight family of connected lights
- [Kuando][3] BusyLight UC Omega and UC Alpha
- [Luxafor][4] Flag
- [ThingM][5] blink(1)

The general use case for most these products is integration with a
communication application via a plugin of some sort: Skype, Teams,
Jabber, and Zoom being common. Those plugins detect when a user is
busy communicating and changes the color of the light to signal they
are busy. The general capabilities of the presense lights tend to be
similar: turn on with a color, turn off, and blink on and off.

After that, the capabilities of lights begin to diverge. Several lights
can also play a tune from a selection stored in firmware. Some lights are
"write-only" and others provide introspection into the current state
of the device. Most devices can maintain their current state without
further software intervention, while some require a keep-alive
heartbeat to continue their current state. Some are even capabable of
running rudimentary stored programs!

The following is a technical review of each of the lights, their capabilties,
and difficulties encountered while adding support for them. All of these
devices are accessible via the USB Human Interface Device (HID) application
programming interface (API). This project would not be possible without
the hard work and generosity of these two projects:

- [LibUSB HIDAPI][8]
- [TREZOR Cython HID API][7]


## Embrava Blynclight

The Embrava Blynclight family of products is diverse but the physical articles I've
tested all seem to share a base implementation. Specifically, I've personally
tested the BLYNCUSB30 (Blynclight) and BLYNCUSB40S (Blynclight Plus) models
and have secondhand accounts of success with the Blynclight mini.

### Basic Info

- Vendor Id values: 0x2c0d, 0x03e5
- I/O Interface: POSIX-style `write` 
- I/O Control: 9 byte word

### Control Word Format

The Embrava Blynclight is a USB HID accessible device whose attributes are
controlled by writing a nine (9) byte packet to the device. 

The C language specification supports bit fields in `struct` definitions,
so it's more natural to use C in this case to describe the control word.

```C
typedef struct {
   unsigned int header: 8;  /* 64:71 Constant 0x0 */
   unsigned int red: 8;     /* 56:63 Red color value [-255] */
   unsigned int blue: 8;    /* 48:55 Blue color value [0-255] */
   unsigned int green: 8;   /* 40:47 Green color value [0-255] */

   unsigned int off: 1;     /* 39:39 Set is off, zero is on */
   unsigned int dim: 1;     /* 38:38 Set is dim, zero is bright */
   unsigned int flash: 1;   /* 37:37 Set is flash on/off, zero is steady */
   unsigned int speed: 3;   /* 34:36 Flash speed mask: 1<<0, 1<<1, 1<<2 */
   unsigned int pad0: 2;    /* 32:33 Unused bits */
   
   unsigned int music: 4;   /* 28:31 Stored music index: [0-15]
   unsigned int play: 1;    /* 27:27 Set play selected music, zero is stop */
   unsigned int repeat: 1;  /* 26:26 Set repeats playing music, zero is once */
   unsigned int pad1: 2;    /* 24:25 Unused pits */
   
   unsigned int volume: 4;  /* 20:23 Volume of music: [0-15]
   unsigned int mute: 1;    /* 19:19 Set is mute, zero is unmute */
   unsigned int padX: 3;    /* 16:18 unused bits */
   
   unsigned int footer: 16; /* 00:15 Constant: 0xFF22 */
} blynclight_ctrl_t
```




[0]: https://github.com/JnyJny/busylight
[1]: https://github.com/JnyJny/busylight/blob/master/docs/BusyLightLogo.png
[2]: https://embrava.com
[3]: https://busylight.com
[4]: https://luxafor.com
[5]: https://thingm.com/products
[6]: https://opensource.org
[7]: https://github.com/trezor/cython-hidapi
[8]: https://github.com/libusb/hidapi
