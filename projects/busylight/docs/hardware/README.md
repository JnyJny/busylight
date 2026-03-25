![BusyLight Project Logo][1]

The [BusyLight for Humans™][0] project provides a common interface to
several types of USB connected LED lights from multiple vendors. This
would not be possible without the hard work and generosity of
these excellent projects:

- [LibUSB HIDAPI][H]
- [TREZOR Cython HID API][T]
- [PySerial][S]

## USB Connected Presence Lights Overview

The general use case for most these products is integration with a
communication application via a plugin of some sort: Skype, Teams,
Jabber, and Zoom being common. Those plugins detect when a user is
communicating and changes the color of the light to signal they
are busy. The general capabilities of the presence lights tend to be
similar: turn on with a color, and turn off.

After that, the capabilities of lights begin to diverge. Several
lights can also blink between alternate colors or play a tune from a
selection stored in firmware. Some lights are "write-only" and others
provide introspection into the current state of the device. Most
devices can maintain their current state without further software
intervention, while some require presistent software intervention to
operate. Unsurprisingly, there are many different approaches to a very
simple concept.

## Technical Reviews

The following is a technical review of each family of USB-connected
lights; their capabilties, and difficulties encountered while adding
support for them. These devices are accessible via the USB
Human Interface Device (HID) application programming interface
(API) or via a more traditional USB serial interface.

- [Agile Innovative BlinkStick Family][6]
- [BusyTag][10]
- [Compulab fit-statUSB][9]
- [Embrava Blynclight Family][2]
- [Kuando BusyLight Family][3]
- [Luxafor Bluetooth, Flag, Orb, and Mute][4]
- [MuteMe MuteMe][7]
- [MuteSync MuteSync][8]
- [Plantronics Status Indicator][2]
- [ThingM blink(1)][5]


[0]: https://github.com/JnyJny/busylight
[1]: assets/Unstacked-Logo-Light.png

[H]: https://github.com/libusb/hidapi
[T]: https://github.com/trezor/cython-hidapi
[S]: https://github.com/pyserial/pyserial

[2]: devices/embrava.md
[3]: devices/kuando.md
[4]: devices/luxafor.md
[5]: devices/thingm.md
[6]: devices/agile_innovative.md
[7]: devices/muteme.md
[8]: devices/mutesync.md
[9]: devices/compulab.md
[10]: devices/busytag.md
