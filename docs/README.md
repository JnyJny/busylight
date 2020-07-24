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






[0]: https://github.com/JnyJny/busylight
[1]: https://github.com/JnyJny/busylight/blob/master/docs/BusyLightLogo_200h.png
[2]: https://embrava.com
[3]: https://busylight.com
[4]: https://luxafor.com
[5]: https://thingm.com/products
[6]: https://opensource.org
[7]: https://github.com/trezor/cython-hidapi
[8]: https://github.com/libusb/hidapi
