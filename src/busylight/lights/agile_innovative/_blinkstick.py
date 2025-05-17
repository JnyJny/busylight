""" Agile Innovative BlinkStick implementation details.
"""

from enum import IntEnum

from loguru import logger

from ..exceptions import LightUnsupported
from ..light import LightInfo


class Report(IntEnum):
    Single = 1
    Mode = 4
    Indexed = 5
    Leds8 = 6
    Leds16 = 7
    Leds32 = 8
    Leds64 = 9

    @classmethod
    def from_nleds(cls, nleds: int) -> "Report":
        if nleds == 1:
            return cls.Single
        if nleds <= 8:
            return cls.Leds8
        if nleds <= 16:
            return cls.Leds16
        if nleds <= 32:
            return cls.Leds32
        if nleds <= 64:
            return cls.Leds64
        raise ValueError("No {cls.__name__} match for {nleds} leds")


class BlinkStickType(IntEnum):
    BlinkStick = 1
    Pro = 2
    Square = 0x200
    Strip = 0x201
    Nano = 0x202
    Flex = 0x203

    @classmethod
    def from_dict(cls, light_info: LightInfo) -> "BlinkStickType":
        try:
            return cls(int(light_info["serial_number"].split("-")[-1].split(".")[0]))
        except KeyError as error:
            logger.error(
                f"serial_number missing from light_info -> {error} {light_info}"
            )
            raise LightUnsupported(light_info) from None
        except IndexError as error:
            logger.error(
                f"failed to parse major number in {light_info['serial_number']}: {error}"
            )
            raise LightUnsupported(light_info) from None
        except ValueError:
            pass

        try:
            return cls(int(light_info["release_number"]))
        except KeyError as error:
            logger.error(f"failed to find release_number {error}")
        except ValueError as error:
            logger.error(f"unknown release {light_info['release_number']!r} {error}")

        raise LightUnsupported(light_info)

    @property
    def name(self) -> "str":
        return {
            0x001: "BlinkStick",
            0x002: "BlinkStick Pro",
            0x200: "BlinkStick Square",
            0x201: "BlinkStick Strip",
            0x202: "BlinkStick Nano",
            0x203: "BlinkStick Flex",
        }[self.value]

    @property
    def nleds(self) -> int:
        try:
            return {
                0x001: 1,
                0x002: 192,
                0x200: 8,
                0x201: 8,
                0x202: 2,
                0x203: 32,
            }[self.value]
        except KeyError:
            raise ValueError(
                "Unknown {self.__class__.__name__} value {self.value}"
            ) from None

    @property
    def report(self) -> Report:
        try:
            return self._report
        except AttributeError:
            pass
        self._report: Report = Report.from_nleds(self.nleds)
        return self._report
