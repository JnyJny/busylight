![BusyLight Project Logo][1]


The [BusyLight for Humans™][0] project provides a common interface to
several types of USB connected LED lights from multiple vendors and
would not be possible without the hard work and generosity of
these two projects:

- [LibUSB HIDAPI][H]
- [TREZOR Cython HID API][T]

## USB Connected Presence Lights Overview

The general use case for most these products is integration with a
communication application via a plugin of some sort: Skype, Teams,
Jabber, and Zoom being common. Those plugins detect when a user is
communicating and changes the color of the light to signal they
are busy. The general capabilities of the presence lights tend to be
similar: turn on with a color, turn off, and blink on and off.

After that, the capabilities of lights begin to diverge. Several
lights can also play a tune from a selection stored in firmware. Some
lights are "write-only" and others provide introspection into the
current state of the device. Most devices can maintain their current
state without further software intervention, while some require
software intervention to operate. Unsurprisingly, there are many
different approaches to a seemingly very simple concept.

## Technical Reviews

The following is a technical review of each family of USB-connected
lights; their capabilties, and difficulties encountered while adding
support for them. All of these devices are accessible via the USB
Human Interface Device (HID) application programming interface
(API). 

- [Embrava Blynclight][2]
- [Kuando BusyLight][3]
- [Luxafor Flag][4]
- [MuteMe][7]
- [ThingM blink(1)][5]
- [Agile Innovative BlinkStick][6]


[0]: https://github.com/JnyJny/busylight
[1]: https://github.com/JnyJny/busylight/blob/master/docs/assets/BusyLightLogo.png

[H]: https://github.com/libusb/hidapi
[T]: https://github.com/trezor/cython-hidapi

[2]: https://github.com/JnyJny/busylight/blob/master/docs/devices/embrava.md
[3]: https://github.com/JnyJny/busylight/blob/master/docs/devices/kuando.md
[4]: https://github.com/JnyJny/busylight/blob/master/docs/devices/luxafor.md
[5]: https://github.com/JnyJny/busylight/blob/master/docs/devices/thingm.md
[6]: https://github.com/JnyJny/busylight/blob/master/docs/devices/agile_innovative.md
[7]: https://github.com/JnyJny/busylight/blob/master/docs/devices/muteme.md

