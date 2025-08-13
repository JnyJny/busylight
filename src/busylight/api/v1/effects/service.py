"""Effects Business Logic Service."""

from ....color import parse_color_string
from ....controller import LightController, LightSelection
from ....effects import Effects
from ....speed import Speed
from ...exceptions import LightNotFoundError, NoLightsAvailableError
from .schemas import EffectOperationResponse


class EffectService:
    """Service layer for effect operations."""

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

    def _get_speed_interval(self, speed: str, base_interval: float) -> float:
        """Get interval based on speed setting."""
        speed_obj = Speed[speed.title()]
        return speed_obj.duty_cycle * base_interval

    async def apply_rainbow_effect(
        self,
        dim: float = 1.0,
        speed: str = "slow",
        led: int = 0,
        light_id: int | None = None,
    ) -> EffectOperationResponse:
        """Apply rainbow/spectrum effect."""
        selection = self._get_light_selection(light_id)
        effect = Effects.for_name("spectrum")(scale=dim)

        interval = self._get_speed_interval(speed, 0.1)
        selection.apply_effect(effect, interval=interval, led=led)

        return EffectOperationResponse(
            success=True,
            action="effect",
            effect_name="rainbow",
            light_id=light_id if light_id is not None else "all",
            dim=dim,
            speed=speed,
            led=led,
        )

    async def apply_pulse_effect(
        self,
        color: str,
        dim: float = 1.0,
        speed: str = "slow",
        count: int = 0,
        led: int = 0,
        light_id: int | None = None,
    ) -> EffectOperationResponse:
        """Apply pulse/gradient effect."""
        rgb = parse_color_string(color, dim)
        selection = self._get_light_selection(light_id)

        effect = Effects.for_name("gradient")(rgb, step=8, count=count)
        interval = self._get_speed_interval(speed, 0.00625)
        selection.apply_effect(effect, interval=interval, led=led)

        return EffectOperationResponse(
            success=True,
            action="effect",
            effect_name="pulse",
            light_id=light_id if light_id is not None else "all",
            color=color,
            rgb=rgb,
            dim=dim,
            speed=speed,
            count=count,
            led=led,
        )

    async def apply_flash_effect(
        self,
        color_a: str,
        color_b: str,
        dim: float = 1.0,
        speed: str = "slow",
        count: int = 0,
        led: int = 0,
        light_id: int | None = None,
    ) -> EffectOperationResponse:
        """Apply flash lights impressively (fli) effect."""
        rgb_a = parse_color_string(color_a, dim)
        rgb_b = parse_color_string(color_b, dim)
        selection = self._get_light_selection(light_id)

        effect = Effects.for_name("blink")(rgb_a, off_color=rgb_b, count=count)
        interval = self._get_speed_interval(speed, 1.0)
        selection.apply_effect(effect, interval=interval, led=led)

        return EffectOperationResponse(
            success=True,
            action="effect",
            effect_name="fli",
            light_id=light_id if light_id is not None else "all",
            color=color_a,
            rgb=rgb_a,
            dim=dim,
            speed=speed,
            count=count,
            led=led,
        )
