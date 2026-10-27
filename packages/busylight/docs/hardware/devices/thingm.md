![BusyLight Project Logo][1]

## ThingM blink(1)

[ThingM][0] is a California company that describes themselves as a "device
studio" and offer many different LED based devices; the consumer
oriented blink(1) product line and for prototyping and hacking they
offer the BlinkM line of products. I worked with the blink(1) mk3 device.

### Tested Hardware

Only the blink(1) mk3 has been tested on physical hardware. The mk1 and mk2
devices share the same vendor and product ID and the same command set, so
they likely work, but they have not been physically tested. Reports from
mk1 and mk2 owners are welcome.

The firmware major version distinguishes the models: 1 is an mk1, 2 is an
mk2 and 3 is an mk3.

### Physical Description

#### blink(1)

The ThingM blink(1) is the smallest USB connected LED light I have
worked with so far. The device mostly consists of a USB-A male
connector with a wraparound transluscent diffuser. The device
dimensions are _roughly_ 1.5 inches long, (excluding USB-A male
connector), 1.25 inches wide and 0.25 inches deep.  The device has two
LEDs; one firing up and the other firing down. My ThingM blink(1) mk3
shipped with an approximately 3 foot long USB cable with a USB-A male
connector and a USB-A female connector.

### Basic Human Interface Device Info

- Vendor/Product ID values:
  - 0x27b8, 0x01ed : Blink(1)
- I/O Interface:
- Command Length:

### Command Format

### Device Operation

#### Activating with a RGB Color

#### Turning the Light Off

### Observations

The device will briefly flash a white color on both LEDs when first plugged in.

### Functionality Wishlist

[0]: https://thingm.com/products
[1]: ../assets/Unstacked-Logo-Light.png
[H]: https://github.com/libusb/hidapi
