![Busylight Project Logo][L]

## FreemanSoft Generic for Custom firmware

This is a driver for devices running custom firmware that
communicates over a USB serial port.  The firmware is written
in CircuitPython and supports any board with a board.NEOPIXEL definition.
It was tested with the Adafruit Trinkey Neo with for Neopixels
running freemansoft derived firmware.

### Physical Description

The test device is the size of a USB thumb drive and is designed as a programmable device

#### Adafruit Trinkey Neo

The fit-statUSB is a very small device with two LEDs mounted on the
dorsal and ventral sides of it's PCB. The entire package is A cm wide,
B cm high, and C cm long, the majority of the device residing inside
the female USB plug.

### USB Device Info

- Vendor/Product ID values:
   - 0x239A, 0x0080: ???

### Device Operation

The Circuit Python devices are accessed via a more traditional serial port rather
than the USB Human Interface Device used by the majority of status
light products. The device is still identifiable via conventional
sixteen bit vendor and product identifiers.

### Command Format

See [firmware docs on github](https://github.com/freemansoft/Adafruit-Trinkey-CircuitPython/tree/main/Indicator-Light-neopixel)

#### Turning the Light On

#### Turning the Light Off

### Observations


[0]: _add link here_

[L]: ../assets/Unstacked-Logo-Light.png
[S]: https://github.com/pyserial/pyserial
