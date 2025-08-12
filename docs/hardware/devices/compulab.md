![Busylight Project Logo][L]

## Compulab fit-statUSB

The [Compulab LTD fit-statUSB][0] is a very small USB device that is
barely bigger than a typical male USB connector. It is **tiny**.

### Physical Description

#### fit-statUSB

The fit-statUSB is a very small device with two LEDs mounted on the
dorsal and ventral sides of it's PCB. The entire package is A cm wide,
B cm high, and C cm long, the majority of the device residing inside
the female USB plug.

### USB Device Info

### Device Operation

The fit-statUSB is accessed via a more traditional serial port rather
than the USB Human Interface Device used by the majority of status
light products. The device is still identifiable via conventional
sixteen bit vendor and product identifiers.

- Vendor/Product ID values:
   - 0x2047, 0x03df: fit-statUSB

### Command Format

The fit-statUSB is [well documented][1] and relies on the user writing
a plain text string to the device via it's serial interface. 

#### Turning the Light On

#### Turning the Light Off

### Observations


[0]: https://fit-iot.com/web/product/fit-statusb/
[1]: http://fit-pc.com/wiki/index.php/Fit-statUSB

[L]: ../assets/Unstacked-Logo-Light.png
[S]: https://github.com/pyserial/pyserial
