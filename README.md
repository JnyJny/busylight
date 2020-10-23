![BusyLight Project Logo][1]

![Python 3.7 Test][37] ![Python 3.8 Test][38] ![Python 3.9 Test][39]

                                                                  

[BusyLight for Humans™][0] gives you control of USB attached LED
lights from a variety of vendors. Lights can be controlled via
the command-line, using a HTTP API or incorporated into your own
python projects. 

![All Supported Lights][DemoGif]

> <em>Back to Front, Left to Right</em> <br>
> <b>BlyncLight, BlyncLight Plus, Busylight</b> <br>
> <b>Blink(1), Flag, BlinkStick</b>

## Features
- Control Lights via Command-Line:
  * Turn lights on with a color
  * Turn lights off
  * Blink lights with a color
  * Control multiple lights collectively or individually
- Control Lights via HTTP:
  * Turn lights on/off and blink
  * Light animations: rainbow, flash and pulse.
  * Self-documenting API

- Supports Lights from Five Vendors
  * Agile Innovations BlinkStick 
  * Embrava Blynclight
  * ThingM Blink1
  * Kuando BusyLight
  * Luxafor Flag
- Tested on MacOS and Linux (Windows and BSD reports welcome!)
- Tested on Raspberry Pi 3b+, Zero and 4

- Easy to Install
  * `python3 -m pip install busylight-for-humans`
  * `python3 -m pip install busylight-for-humans[webapi]`


## Examples

```console
$ 
```


[0]: https://github.com/JnyJny/busylight
[1]: https://github.com/JnyJny/busylight/blob/master/docs/assets/BusyLightLogo.png

[H]: https://github.com/libusb/hidapi
[T]: https://github.com/trezor/cython-hidapi


[37]: https://github.com/JnyJny/busylight/workflows/Python%203.7/badge.svg
[38]: https://github.com/JnyJny/busylight/workflows/Python%203.8/badge.svg
[39]: https://github.com/JnyJny/busylight/workflows/Python%203.9/badge.svg

[DemoGif]: https://github.com/JnyJny/busylight/raw/master/demo/demo.gif
