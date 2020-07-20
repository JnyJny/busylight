"""A generic USB attached LED light.
"""

import hid

from contextlib import contextmanager
from functools import partial
from threading import Thread
from typing import Dict, Generator, Tuple, Union

from bitvector import BitVector, BitField

from .effect_thread import EffectThread


class USBLightInUse(Exception):
    pass


class USBLightNotFound(Exception):
    pass


class UnknownUSBLight(Exception):
    pass


class USBLightAttribute(BitField):
    """Read-write USB light attribute.
    """


class USBLightImmediateAttribute(BitField):
    """Read-write USB light attribute that also optionally updates
    hardware state.
    """

    def __set__(self, obj, value) -> None:
        super().__set__(obj, value)
        if value:
            obj.update()


class USBLightReadOnlyAttribute(BitField):
    """Read-only USB light attribute. 
    """

    def __set__(self, obj, value) -> None:
        return


class USBLight(BitVector):
    """A generic USB light that uses HIDAPI to control devices.

    The assumption is most hardware devices have a control word
    of N-bits that describes the capabilities of the device. Since
    the capabilities of lights varies widely, the generic device
    only supports these features:
    
    - on
    - off
    - blink
    
    This class only provides stub methods for those features which
    all raise NotImplementedError. It is up to concrete subclasses
    to fill in the blanks.

    See `busylight.lights.blynclight` and `busylight.lights.luxafor`
    for two different implementations based on USBLight.

    The USBLight models the state of the light in-memory and updates
    the physical device. Updates to the device can be made immediately
    whenever an attribute is modified, or in batch-mode to avoid
    unwanted physical artificts (flickering, chirping, etc). Subclasses
    can use the `USBLightImmediateAttribute` descriptor class to define
    sub-bitfields in the device command buffer which can be controlled
    this way. 

    """

    VENDOR_IDS = []  # subclasses must provide
    __vendor__ = "generic"  # subclasses must provide

    @classmethod
    def from_dict(cls, info: Dict[str, Union[int, str]]):
        """Returns a configured USBLight for the device described in 
        the input dictionary.

        :param info: Dict[str, Union[int, str]]
        
        Raises:
        - USBLightInUse
        - UnknownUSBLight
        - USBLightNotFound
        - ValueError
        """

        try:
            return cls(info["vendor_id"], info["product_id"])
        except KeyError:
            raise ValueError("Dictionary is missing vendor_id or product_id keys.")

    def __init__(
        self,
        vendor_id: int,
        product_id: int,
        default_state: int = 0,
        cmd_length: int = 128,
    ):
        """A generic USB light device.

        :param vendor_id: 16-bit integer
        :param product_id: 16-bit integer
        :param default_state: integer
        :param cmd_length: USB command length in bits

        Raises:
        - USBLightInUse
        - USBLightNotFound
        """
        self.immediate_mode = False
        super().__init__(value=default_state, size=cmd_length)
        self.default_state = default_state
        self.vendor_id = vendor_id
        self.product_id = product_id
        try:
            self.device.open(vendor_id, product_id)
        except OSError:
            raise USBLightInUse(self) from None
        except ValueError:
            raise USBLightNotFound(self) from None

    def __repr__(self):
        class_name = self.__class__.__name__
        vendor_id = f"vendor_id=0x{self.vendor_id:04x}"
        product_id = f"product_id=0x{self.product_id:04x}"
        default = f"default_state={self.hex}"
        cmdlen = f"cmd_length={len(self)}"

        return f"{class_name}({vendor_id}, {product_id}, {default}, {cmdlen})"

    def __str__(self):
        return f"{self.info['product_string'].title()}:{self.identifier}"

    @property
    def info(self) -> Dict[str, Union[int, str]]:
        """A dictionary of HIDAPI attributes for this light.
        """
        try:
            return self._info
        except AttributeError:
            pass
        self._info = hid.enumerate(self.vendor_id, self.product_id)
        return self._info

    def __del__(self):
        self.close()

    @property
    def identifier(self) -> str:
        """A string identifier for this device."""
        return f"0x{self.vendor_id:04x}:0x{self.product_id:04x}"

    @property
    def name(self) -> str:
        """Concatenation of the light's vendor and class names."""
        return f"{self.__vendor__} {self.__class__.__name__}"

    @property
    def immediate_mode(self) -> bool:
        """The immediate_mode attribute controls whether updates to the
        in-memory state of the device cause an immediate write to the
        device.
        """
        return getattr(self, "_immediate_mode", False)

    @immediate_mode.setter
    def immediate_mode(self, new_mode: bool) -> None:
        self._immediate_mode = new_mode
        self.update()

    @property
    def device(self) -> hid.device:
        """A hid.device instance.
        """
        try:
            return self._device
        except AttributeError:
            pass
        self._device = hid.device()
        return self._device

    @property
    def helper_thread(self) -> Union[EffectThread, None]:
        """Starts a helper thread if the USBLight subclass
        implements a generator helper method [see EffectThread].
        """
        try:
            return self._helper_thread
        except AttributeError:
            pass

        try:
            self._helper_thread = EffectThread(self.helper, f"helper-{self.identifier}")
        except AttributeError:
            self._helper_thread = None

        return self._helper_thread

    @property
    def effect_thread(self) -> Union[EffectThread, None]:
        """An EffectThread that is currently animating the
        light. Returns None if not animating.
        """
        return getattr(self, "_effect_thread", None)

    def close(self, turn_off: bool = False) -> None:
        """Shutdown any helper or effect threads active for this light,
        optionally turn the light off and close the USB HIDAPI device.

        The light cannot be re-used after it's closed. 

        :param turn_off: bool
        """
        try:
            self.helper_thread.cancel()
            while self.helper_thread.is_alive():
                self.helper_thread.join(0.1)
            self._helper_thread = None
        except AttributeError:
            pass

        self.stop_effect()

        if turn_off:
            self.off()

        self.device.close()

    def update(self, flush: bool = False) -> None:
        """Writes the in-memory state of the device to the hardware.

        The update is skipped if immediate_mode is False and flush
        is False. If flush is True, the value of immediate_mode is
        ignored.

        :param flush: bool
        """

        if flush or self.immediate_mode:
            self.device.write(self.bytes)
            # raise exception if bytes written != len(self.bytes)?

    def reset(self, flush: bool = False) -> None:
        """Reset the in-memory state to the default configuration.

        If flush is True, write the in-memory state to the hardware.

        :param flush: bool
        """
        self.value = self.default_state
        self.update(flush=flush)

    @contextmanager
    def updates_paused(self):
        """Context manager that pauses device updates. This is useful
        for making multiple updates to a device and avoiding unwanted
        physical artifacts from manifesting (flickering, chirping, etc).

        with light.updates_paused():
            self.on = 1
            self.red = 0xff
            self.green = 0
            self.blue = 0
        # changes will be flushed on exit from the context manager

        """
        prev_mode = self.immediate_mode
        self.immediate_mode = False
        yield
        self.immediate_mode = prev_mode

    def start_effect(self, effect: Generator) -> None:
        """Start an effect in another thread. The effect subroutine
        is expected to be a generator that takes the light object as
        it's only argument.  The effect generator should call yield
        as often as possible to make the thread more  responsive to
        canceling [see EffectThread].

        :param effect: Generator
        """
        self._effect_thread = EffectThread(
            partial(effect, self), f"effect-{self.identifier}"
        )
        self._effect_thread.start()

    def stop_effect(self) -> None:
        """Cancels the effect_thread (if it is an EffectThread)). The
        light is left in an unknown color/on/off state after this method
        returns.
        """
        try:
            self.effect_thread.cancel()
            while self.effect_thread.is_alive():
                self.effect_thread.join(0.1)
            self._effect_thread = None
        except AttributeError:
            pass

    # EJO The color property might not belong here.

    @property
    def color(self) -> Tuple[int, int, int]:
        """A tuple of red, green and blue integer values. 
        """
        return tuple([self.red, self.green, self.blue])

    @color.setter
    def color(self, new_value: Tuple[int, int, int]) -> None:

        with self.updates_paused():
            self.red, self.green, self.blue = new_value

    def on(self, color: Tuple[int, int, int] = None):
        """Stub on method.
        """
        raise NotImplementedError("on")

    def off(self):
        """Stub off method.
        """
        raise NotImplementedError("off")

    def blink(self, color: Tuple[int, int, int], speed: int):
        """Stub blink method
        """
        raise NotImplementedError("blink")
