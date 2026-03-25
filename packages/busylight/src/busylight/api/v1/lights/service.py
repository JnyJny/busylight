"""Light Business Logic Service."""

from typing import Any

from busylight_core import Light

from ....color import colortuple_to_name, parse_color_string
from ....controller import LightController, LightSelection
from ....speed import Speed
from ...exceptions import LightNotFoundError, NoLightsAvailableError
from .schemas import LightHardwareInfo, LightOperationResponse, LightStatus


class LightService:
    """Service layer for light operations."""

    def __init__(self, controller: LightController):
        self.controller = controller

    def _get_light_selection(self, light_id: int | None = None) -> LightSelection:
        """Get light selection by ID or all lights."""
        if not self.controller.lights:
            raise NoLightsAvailableError()

        if light_id is None:
            return self.controller.all()

        try:
            return self.controller.by_index(light_id)
        except IndexError:
            raise LightNotFoundError(light_id)

    def _light_to_status(self, light: Light, light_id: int) -> LightStatus:
        """Convert Light object to LightStatus schema."""
        return LightStatus(
            light_id=light_id,
            name=light.name,
            info=LightHardwareInfo(
                path=light.hardware.path,
                vendor_id=light.hardware.vendor_id,
                product_id=light.hardware.product_id,
                serial_number=light.hardware.serial_number,
                manufacturer_string=light.hardware.manufacturer_string,
                product_string=light.hardware.product_string,
                release_number=light.hardware.release_number,
                is_acquired=light.hardware.is_acquired,
            ),
            is_on=light.is_lit,
            color=colortuple_to_name(light.color),
            rgb=light.color,
        )

    def get_light_status(self, light_id: int) -> LightStatus:
        """Get status of a specific light."""
        if not self.controller.lights:
            raise NoLightsAvailableError()

        try:
            light = self.controller.lights[light_id]
        except IndexError:
            raise LightNotFoundError(light_id)

        return self._light_to_status(light, light_id)

    def get_all_lights_status(self) -> list[LightStatus]:
        """Get status of all available lights."""
        if not self.controller.lights:
            return []

        return [
            self._light_to_status(light, light_id)
            for light_id, light in enumerate(self.controller.lights)
        ]

    def turn_on_light(
        self, color: str, dim: float = 1.0, led: int = 0, light_id: int | None = None
    ) -> LightOperationResponse:
        """Turn on light(s) with specified color."""
        rgb = parse_color_string(color, dim)
        selection = self._get_light_selection(light_id)

        selection.turn_on(rgb, led=led)

        return LightOperationResponse(
            success=True,
            action="on",
            light_id=light_id if light_id is not None else "all",
            color=color,
            rgb=rgb,
            dim=dim,
            led=led,
        )

    def turn_off_light(self, light_id: int | None = None) -> LightOperationResponse:
        """Turn off light(s)."""
        selection = self._get_light_selection(light_id)
        selection.turn_off()

        return LightOperationResponse(
            success=True,
            action="off",
            light_id=light_id if light_id is not None else "all",
        )

    def blink_light(
        self,
        color: str,
        dim: float = 1.0,
        speed: str = "slow",
        count: int = 0,
        led: int = 0,
        light_id: int | None = None,
    ) -> LightOperationResponse:
        """Blink light(s) with specified parameters."""
        rgb = parse_color_string(color, dim)
        selection = self._get_light_selection(light_id)

        selection.blink(rgb, count=count, speed=speed, led=led)

        return LightOperationResponse(
            success=True,
            action="blink",
            light_id=light_id if light_id is not None else "all",
            color=color,
            rgb=rgb,
            dim=dim,
            speed=speed,
            count=count,
            led=led,
        )
