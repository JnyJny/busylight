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
   - 0x239A, 0x80f0: NeoPixel Trinkey M0

On the mac you see something like

```
NeoPixel Trinkey M0:

   Product ID: 0x80f0
   Vendor ID: 0x239a
   Version: 1.00
   Serial Number: CA1747C34B48585020312E3521280EFF
   Speed: Up to 12 Mb/s
   Manufacturer: Adafruit Industries LLC
   Location ID: 0x02100000 / 1
   Current Available (mA): 500
   Current Required (mA): 100
   Extra Operating Current (mA): 0
   Media:
   NeoPixel Trinkey:
      Capacity: 66 KB (66,048 bytes)
      Removable Media: Yes
      BSD Name: disk4
      Logical Unit: 0
      Partition Map Type: MBR (Master Boot Record)
      S.M.A.R.T. status: Verified
      USB Interface: 2
      Volumes:
         CIRCUITPY:
         Capacity: 66 KB (65,536 bytes)
         Free: 32 KB (32,256 bytes)
         Writable: Yes
         File System: MS-DOS FAT12
         BSD Name: disk4s1
         Mount Point: /Volumes/CIRCUITPY
         Content: DOS_FAT_12
         Volume UUID: D9E0500C-524E-39A8-A778-C125384249C0
```

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
