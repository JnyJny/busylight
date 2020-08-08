## Kuando BusyLight

The Kuando BusyLight line of products consists of the Busylight UC Alpha and the
BusyLight US Omega. For development, I tested with the Omega model. I have no
reason to believe that the Alpha varies in any significant way with respect to
it's software configuration.

### Physical Description

#### UC Omega

The UC Omega is vaguely cylindrical in shape, with a slightly wider
base and a narrower top. The device has a permamently attached USB
cord with a USB-A male connector. There is a small side-firing speaker
grill on the side opposite of the cable. The entire device is roughly
1.5 inches in diameter and 1.75 inches tall. The diffuser is secured
to the base, possibly glued, and I was not able to determine how many
LED lights the device has. 

### Basic Human Interface Device Info

- Vendor Id values: 0x27bb
- I/O Interface: HID `write`
- Command Length: 64 bytes

### Command Format

The Kuando UC Omega is a [USB HID][8] accessible device whose
attributes are controlled by writing a 64 byte packet to the device.

### Device Operation

#### Activating With a RGB Color

#### Turning the Light Off

### Observations

### Functionality Wishlist
