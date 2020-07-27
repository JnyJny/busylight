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

### Physical Description

#### Blynclight & Blynclight Plus

These two lights are very similar and consist of a "pedastal" topped
by a cubical transluscent diffuser. The pedastal houses the PCB board
of the device and features five LEDs exposed on the top. The LEDs are
arranged in a "checkerboard" configuration and are not individually
addressable. There is a female USB mini connector which allows
connecting the device to a host with any in-spec length cable.

The Blynclight Plus appears to have a downward firing speaker, however
covering the bottom "grille" does not seem to attenuate how loud the
device is.

The devices are roughly 2 inches tall, and 1.5 inches on a side. 

### Basic Human Interface Device Info 

- Vendor Id values: 0x2c0d, 0x03e5
- I/O Interface: POSIX-style `write`
- I/O Control: 9 byte word

### Control Word Format

The Embrava Blynclight is a [USB HID][8] accessible device whose
attributes are controlled by writing a nine (9) byte packet to the
device.

The following is a C language structure type definition using bit
fields to illustrate the structure of the 9-byte packet. Examples
for configuring the device for different functions will be given
in C, however they should be very accessible regardless of what
language the reader may be familiar with. 

A structure bit field in C is declared as a member of a struct,
usually an `unsigned int`, followed by a width specifier. The
`header` field specified below is an 8-bit (1-byte) field, while
the `off` field is a single bit field. Fields prefixed with `pad`
are unused and defined to maintain the correct offsets within the
structure for fields that follow. 

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
   unsigned int pad2: 3;    /* 16:18 unused bits */
   
   unsigned int footer: 16; /* 00:15 Constant: 0xFF22 */
} blynclight_ctrl_t
```

### Device Operation

The devices requires the inital byte of the control word be zero and
the final two bytes of the word be set to 0xFF22. The device is
effectively write-only as I have not been able to get the device to
return anything via the `read` or `get_feature_report` interfaces
(beyond nulls).

#### Activating With a RGB Color

Turning the light on requires the user to supply a control word with
`off` de-asserted (zero) and one or more red, blue or green values.
Please note that this device does not follow the RGB convention of
color ordering; the order of green and blue is swapped, **RBG**.

**Example: Activate Light with Purple Color.**
```C
	blynclight_ctrl_t cword;
	
	cword.red = 0xff;
	cword.blue = 0xff;
	cword.green = 0x00;
	cword.off = 0;
	/* write control word to device */
```	

Please note that clearing the `off` field is not enough to provoke a
visible effect form the device; a color must also be given otherwise
the light is "on" with a black color. This can be frustrating.

#### Turning Light Off

Turning the light off only requires setting the `off` field and writing
the control word to the device.


#### Dimming the Light

The light can be put into a dim state by asserting the `dim` bit, resuming
"bright" operation when `dim` is cleared.

#### Flash Mode

The light can be made to flash on and off, alternating between the
specified RGB value and off. The flash speed is controlled by the
3-bit `speed` field which is used to specify three speeds: slow, medium
and fast. 

**Example: Configuring Flash Mode**
```C
	blynclight_ctl_t cword;
	
	cword.flash = 1
	cword.speed = 1 << 0; /* slow speed */
	cword.speed = 1 << 1; /* medium speed */
	cword.speed = 1 << 2; /* fast speed */
```

When `flash` is set and `speed` is set to any value other than (1, 2, 4),
the light will respond by strobing on and off very quickly. 

#### Sound Operation

Some models of Blynclight provide the ability to trigger playback of tones
stored in the firmware of the device, e.g. Blynclight Plus and others.

Playback of stored tones is controlled by the `play`, `repeat`,
`music`, `volume` and `mute` fields. The 4-bit `music` field selects
which stored sound to play. The `repeat` field toggles whether the
sound is played one time or repeated indefinitely.  The 4-bit `volume`
field specifies the volume the sound is played at where zero is silent
and 0xF is the maximum. The `mute` bit controls whether the volume
setting is respected or clamped to zero at the device. Finally, the
`play` bit initiates playback of the selected sound with the specified
volume and repeat value.

Practically, I could not distinguish any difference in loudness
for volume values between 1 and 0xf.

**Example: Playing the First Sound One Time**
```C
    blynclight_ctl_t cword;
	
	cword.play = 1
	cword.music = 1
	cword.volume = 1
	cword.mute = 0
	cword.repeat = 0
```

### Observations

The Embrava Blynclight is simple robust device. The only _edge_ case behavior I've
encountered is the strobe effect achieved when `flash` is set and `speed` is [0,3,5,7].
The light is very responsive and I have **not** been able to induce an error state in the
light that required "rebooting" (unplug/plug) the light to recover normal function.

### Functionality Wishlist 

- Read current state
- Individual control of the five LEDs


[0]: https://github.com/JnyJny/busylight
[1]: https://github.com/JnyJny/busylight/blob/master/docs/BusyLightLogo.png
[2]: https://embrava.com
[3]: https://busylight.com
[4]: https://luxafor.com
[5]: https://thingm.com/products
[6]: https://opensource.org
[7]: https://github.com/trezor/cython-hidapi
[8]: https://github.com/libusb/hidapi
