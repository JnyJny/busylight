# USBLight - Abstract Base Class

The `busylight.lights.USBLight` abstract base class provides access to
USB connected devices, providing a common infrastructure for managing
device state. Subclasses of USBLight implement the hardware dependent
details.

## Adding Support for a New USB Light (TL;DR)

1. Create a new package rooted in busylight.lights
2. Identify the device's vendor identifer, 16-bit integer
3. Identify the device's product identifier, 16-bit integer (optional)
4. Identify the device's vendor, `string`
5. Implement a subclass of USBLight with:
   - Properties:
     * VENDOR_IDS : `List[int]`
     * PRODUCT_IDS : `List[int]`
     * vendor : `string`
   - Methods:
     * `__bytes__(self) -> bytes`
	 * `on(self, color: Tuple[int, int, int]) -> None`
	 * `blink(self, color: Tuple[int, int, int], speed: int) -> None`
	 * `reset(self) -> None`
6. Import your new subclass in `busylight.lights.__init__.py`


   






