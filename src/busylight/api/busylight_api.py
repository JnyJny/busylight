"""BusyLight API"""

from json import loads as json_loads
from os import environ
from secrets import compare_digest
from typing import Any, Callable

from busylight_core import Light, LightUnavailableError, NoLightsFoundError
from fastapi import Depends, FastAPI, HTTPException, Path, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from loguru import logger

from .. import __version__
from ..color import ColorLookupError, colortuple_to_name, parse_color_string
from ..controller import LightController
from ..effects import Effects
from ..speed import Speed
from .models import EndPoint, LightDescription, LightOperation

__description__ = """
<!-- markdown formatted for HTML rendering -->
An API server for USB connected presence lights.

[Source](https://github.com/JnyJny/busylight.git)
"""

busylightapi_security = HTTPBasic()


class BusylightAPI(FastAPI):
    def __init__(self):
        debug = environ.get("BUSYLIGHT_DEBUG", False)
        logger.info(f"Debug: {debug}")

        dependencies = []
        logger.info("Set up authentication, if environment variables set.")
        try:
            self.username = environ["BUSYLIGHT_API_USER"]
            self.password = environ["BUSYLIGHT_API_PASS"]
            dependencies.append(Depends(self.authenticate_user))
            logger.info("Found user credentials in environment.")
        except KeyError:
            logger.info("Did NOT find user credentials in environment.")
            logger.info("Access authentication disabled.")
            self.username = None
            self.password = None

        logger.info(
            "Set up CORS Access-Control-Allow-Origin header, if environment variable BUSYLIGHT_API_CORS_ORIGINS_LIST is set.",
        )
        self.origins = json_loads(environ.get("BUSYLIGHT_API_CORS_ORIGINS_LIST", "[]"))

        if (not isinstance(self.origins, list)) or any(
            not isinstance(item, str) for item in self.origins
        ):
            logger.warning(
                f"BUSYLIGHT_API_CORS_ORIGINS_LIST is invalid: {self.origins}",
            )
            logger.info("Will NOT set the CORS Access-Control-Allow-Origin header.")
            self.origins = None

        logger.info(
            f"CORS Access-Control-Allow-Origin list: {self.origins}",
        )

        if (debug == True) and (self.origins == None):
            logger.info(
                'However, debug mode is enabled! Using debug mode CORS allowed origins: \'["http://localhost", "http://127.0.0.1"]\'',
            )
            self.origins = ["http://localhost", "http://127.0.0.1"]

        super().__init__(
            title="Busylight Server: A USB Light Server",
            description=__description__,
            version=__version__,
            dependencies=dependencies,
        )
        self.controller = LightController()
        self.endpoints: list[str] = []

    @property
    def lights(self) -> list[Light]:
        """Get all lights for compatibility."""
        return self.controller.lights

    def update(self) -> None:
        _ = self.controller.lights

    def release(self) -> None:
        self.controller.release_lights()

    def off(self, light_id: int = None) -> None:
        if light_id is None:
            self.controller.all().turn_off()
        else:
            self.controller.by_index(light_id).turn_off()

    async def apply_effect(self, effect: Effects, light_id: int = None, led: int = 0) -> None:
        if light_id is None:
            self.controller.all().apply_effect(effect, led=led)
        else:
            self.controller.by_index(light_id).apply_effect(effect, led=led)

    def get(self, path: str, **kwargs) -> Callable:
        self.endpoints.append(path)

        if self.origins:
            self.add_middleware(
                CORSMiddleware,
                allow_origins=self.origins,
            )

        kwargs.setdefault("response_model_exclude_unset", True)
        return super().get(path, **kwargs)

    def authenticate_user(
        self,
        credentials: HTTPBasicCredentials = Depends(busylightapi_security),
    ) -> None:
        username_correct = compare_digest(credentials.username, self.username)
        password_correct = compare_digest(credentials.password, self.password)
        if not (username_correct and password_correct):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Basic"},
            )


busylightapi = BusylightAPI()


@busylightapi.on_event("startup")
async def startup() -> None:
    busylightapi.update()
    busylightapi.off()


@busylightapi.on_event("shutdown")
async def shutdown() -> None:
    try:
        busylightapi.off()
    except Exception:
        logger.debug("problem during shutdown: {error}")


@busylightapi.exception_handler(LightUnavailableError)
async def light_unavailable_handler(
    request: Request,
    error: LightUnavailableError,
) -> JSONResponse:
    """Handle lights which are unavailable."""
    return JSONResponse(
        status_code=404,
        content={"message": str(error)},
    )


@busylightapi.exception_handler(NoLightsFoundError)
async def light_not_found_handler(
    request: Request,
    error: NoLightsFoundError,
) -> JSONResponse:
    """Handle light not found."""
    return JSONResponse(
        status_code=404,
        content={"message": str(error)},
    )


@busylightapi.exception_handler(IndexError)
async def index_error_handler(
    request: Request,
    error: IndexError,
) -> JSONResponse:
    """Handle light not found at index."""
    return JSONResponse(
        status_code=404,
        content={"message": str(error)},
    )


@busylightapi.exception_handler(ColorLookupError)
async def color_lookup_error_handler(
    request: Request,
    error: ColorLookupError,
) -> JSONResponse:
    """Handle color strings that do not result in a valid color."""
    return JSONResponse(
        status_code=404,
        content={"message": str(error)},
    )


@busylightapi.middleware("http")
async def light_manager_update(request: Request, call_next: Callable) -> Response:
    """Check for plug/unplug events and update the light manager."""
    busylightapi.update()

    return await call_next(request)


@busylightapi.get("/", response_model=list[EndPoint])
async def available_endpoints() -> list[dict[str, str]]:
    """API endpoint listing.

    List of valid endpoints recognized by this API.
    """
    return [{"path": endpoint} for endpoint in busylightapi.endpoints]


@busylightapi.get(
    "/light/{light_id}/status",
    response_model=LightDescription,
)
@busylightapi.get(
    "/light/{light_id}",
    response_model=LightDescription,
)
async def light_status(
    light_id: int = Path(..., title="Numeric light identifier", ge=0),
) -> dict[str, Any]:
    """Information about the light selected by `light_id`."""
    light = busylightapi.lights[light_id]

    return {
        "light_id": light_id,
        "name": light.name,
        "info": {
            "path": light.hardware.path,
            "vendor_id": light.hardware.vendor_id,
            "product_id": light.hardware.product_id,
            "serial_number": light.hardware.serial_number,
            "manufacturer_string": light.hardware.manufacturer_string,
            "product_string": light.hardware.product_string,
            "release_number": light.hardware.release_number,
            "is_acquired": light.hardware.is_acquired,
        },
        "is_on": light.is_lit,
        "color": colortuple_to_name(light.color),
        "rgb": light.color,
    }


@busylightapi.get(
    "/lights/status",
    response_model=list[LightDescription],
)
@busylightapi.get(
    "/lights",
    response_model=list[LightDescription],
)
async def lights_status() -> list[dict[str, Any]]:
    """Information about all available lights."""
    result = []
    for light_id, light in enumerate(busylightapi.lights):
        result.append(
            {
                "light_id": light_id,
                "name": light.name,
                "info": {
                    "path": light.hardware.path,
                    "vendor_id": light.hardware.vendor_id,
                    "product_id": light.hardware.product_id,
                    "serial_number": light.hardware.serial_number,
                    "manufacturer_string": light.hardware.manufacturer_string,
                    "product_string": light.hardware.product_string,
                    "release_number": light.hardware.release_number,
                    "is_acquired": light.hardware.is_acquired,
                },
                "is_on": light.is_lit,
                "color": colortuple_to_name(light.color),
                "rgb": light.color,
            },
        )
    return result


@busylightapi.get(
    "/light/{light_id}/on",
    response_model=LightOperation,
)
async def light_on(
    light_id: int = Path(..., title="Numeric light identifier", ge=0),
    color: str = "green",
    dim: float = 1.0,
    led: int = 0,
) -> dict[str, Any]:
    """Turn on the specified light with the given `color`.

    `light_id` is an integer value identifying a light and ranges
    between zero and number_of_lights-1.

    `color` can be a color name or a hexadecimal string e.g. "red",
    "#ff0000", "#f00", "0xff0000", "0xf00", "f00", "ff0000"

    `led` parameter targets specific LEDs on multi-LED devices:
    - 0 = all LEDs (default)
    - 1+ = specific LED (1=first/top, 2=second/bottom, etc.)
    """
    rgb = parse_color_string(color, dim)

    busylightapi.controller.by_index(light_id).turn_on(rgb, led=led)

    return {
        "action": "on",
        "light_id": light_id,
        "color": color,
        "rgb": rgb,
        "dim": dim,
        "led": led,
    }


@busylightapi.get(
    "/lights/on",
    response_model=LightOperation,
)
async def lights_on(
    color: str = "green",
    dim: float = 1.0,
    led: int = 0,
) -> dict[str, Any]:
    """Turn on all lights with the given `color`.

    `color` can be a color name or a hexadecimal string e.g. "red",
    "#ff0000", "#f00", "0xff0000", "0xf00", "f00", "ff0000"

    `led` parameter targets specific LEDs on multi-LED devices:
    - 0 = all LEDs (default)
    - 1+ = specific LED (1=first/top, 2=second/bottom, etc.)
    """
    rgb = parse_color_string(color, dim)

    busylightapi.controller.all().turn_on(rgb, led=led)

    return {
        "action": "on",
        "light_id": "all",
        "color": color,
        "rgb": rgb,
        "dim": dim,
        "led": led,
    }


@busylightapi.get(
    "/light/{light_id}/off",
    response_model=LightOperation,
)
async def light_off(
    light_id: int = Path(..., title="Numeric light identifier", ge=0),
) -> dict[str, Any]:
    """Turn off the specified light.
    `light_id` is an integer value identifying a light and ranges
    between zero and number_of_lights-1.

    `color` can be a color name or a hexadecimal string e.g. "red",
    "#ff0000", "#f00", "0xff0000", "0xf00", "f00", "ff0000"
    """
    busylightapi.off(light_id)

    return {
        "action": "off",
        "light_id": light_id,
    }


@busylightapi.get(
    "/lights/off",
    response_model=LightOperation,
)
async def lights_off() -> dict[str, Any]:
    """Turn off all lights."""
    busylightapi.off()

    return {
        "action": "off",
        "light_id": "all",
    }


@busylightapi.get(
    "/light/{light_id}/blink",
    response_model=LightOperation,
)
async def blink_light(
    light_id: int = Path(..., title="Numeric light identifier", ge=0),
    color: str = "red",
    speed: Speed = Speed.Slow,
    dim: float = 1.0,
    count: int = 0,
    led: int = 0,
) -> dict[str, Any]:
    """Start blinking the specified light: color and off.

    `light_id` is an integer value identifying a light and ranges
    between zero and number_of_lights-1.

    The `color` can be a color name or a hexadecimal string: red,
    #ff0000, #f00, 0xff0000, 0xf00, f00, ff0000

    `count` is the number of times to blink the light.

    `led` parameter targets specific LEDs on multi-LED devices:
    - 0 = all LEDs (default)
    - 1+ = specific LED (1=first/top, 2=second/bottom, etc.)
    """
    rgb = parse_color_string(color, dim)

    selection = busylightapi.controller.by_index(light_id)
    selection.blink(rgb, count=count, speed=speed.name.lower(), led=led)

    return {
        "action": "blink",
        "light_id": light_id,
        "color": color,
        "rgb": rgb,
        "speed": speed,
        "dim": dim,
        "count": count,
        "led": led,
    }


@busylightapi.get(
    "/lights/blink",
    response_model=LightOperation,
)
async def blink_lights(
    color: str = "red",
    speed: Speed = Speed.Slow,
    dim: float = 1.0,
    count: int = 0,
    led: int = 0,
) -> dict[str, Any]:
    """Start blinking all the lights: red and off
    <p>Note: lights will not be synchronized.</p>

    `led` parameter targets specific LEDs on multi-LED devices:
    - 0 = all LEDs (default)
    - 1+ = specific LED (1=first/top, 2=second/bottom, etc.)
    """
    rgb = parse_color_string(color, dim)

    selection = busylightapi.controller.all()
    selection.blink(rgb, count=count, speed=speed.name.lower(), led=led)

    return {
        "action": "blink",
        "light_id": "all",
        "color": color,
        "rgb": rgb,
        "speed": speed,
        "dim": dim,
        "count": count,
        "led": led,
    }


@busylightapi.get(
    "/light/{light_id}/rainbow",
    response_model=LightOperation,
)
async def rainbow_light(
    light_id: int = Path(..., title="Numeric light identifier", ge=0),
    speed: Speed = Speed.Slow,
    dim: float = 1.0,
    led: int = 0,
) -> dict[str, Any]:
    """Start a rainbow animation on the specified light.

    `light_id` is an integer value identifying a light and ranges
    between zero and number_of_lights-1.

    `led` parameter targets specific LEDs on multi-LED devices:
    - 0 = all LEDs (default)
    - 1+ = specific LED (1=first/top, 2=second/bottom, etc.)
    """
    rainbow = Effects.for_name("spectrum")(scale=dim)

    await busylightapi.apply_effect(rainbow, light_id, led=led)

    return {
        "action": "effect",
        "name": "rainbow",
        "light_id": light_id,
        "speed": speed,
        "dim": dim,
        "led": led,
    }


@busylightapi.get(
    "/lights/rainbow",
    response_model=LightOperation,
)
async def rainbow_lights(
    speed: Speed = Speed.Slow,
    dim: float = 1.0,
    led: int = 0,
) -> dict[str, Any]:
    """Start a rainbow animation on all lights.
    <p><em>Note:</em> lights will not be synchronized.</p>

    `led` parameter targets specific LEDs on multi-LED devices:
    - 0 = all LEDs (default)
    - 1+ = specific LED (1=first/top, 2=second/bottom, etc.)
    """
    rainbow = Effects.for_name("spectrum")(scale=dim)

    await busylightapi.apply_effect(rainbow, led=led)

    return {
        "action": "effect",
        "name": "rainbow",
        "light_id": "all",
        "dim": dim,
        "led": led,
    }


@busylightapi.get(
    "/light/{light_id}/fli",
    response_model=LightOperation,
)
async def flash_light_impressively(
    light_id: int = Path(..., title="Numeric light identifier", ge=0),
    color_a: str = "red",
    color_b: str = "blue",
    speed: Speed = Speed.Slow,
    dim: float = 1.0,
    count: int = 0,
    led: int = 0,
) -> dict[str, Any]:
    """Flash the specified light impressively [default: red/blue].

    `light_id` is an integer value identifying a light and ranges
    between zero and number_of_lights-1.

    `count` is the number of times to blink the light.

    `led` parameter targets specific LEDs on multi-LED devices:
    - 0 = all LEDs (default)
    - 1+ = specific LED (1=first/top, 2=second/bottom, etc.)
    """
    rgb_a = parse_color_string(color_a, dim)
    rgb_b = parse_color_string(color_b, dim)

    fli = Effects.for_name("blink")(
        rgb_a,
        off_color=rgb_b,
        count=count,
    )

    await busylightapi.apply_effect(fli, light_id, led=led)

    return {
        "action": "effect",
        "name": "fli",
        "light_id": light_id,
        "speed": speed,
        "color": color_a,
        "dim": dim,
        "count": count,
        "led": led,
    }


@busylightapi.get(
    "/lights/fli",
    response_model=LightOperation,
)
async def flash_lights_impressively(
    color_a: str = "red",
    color_b: str = "blue",
    speed: Speed = Speed.Slow,
    dim: float = 1.0,
    count: int = 0,
    led: int = 0,
):
    """Flash all lights impressively [default: red/blue]

    `led` parameter targets specific LEDs on multi-LED devices:
    - 0 = all LEDs (default)
    - 1+ = specific LED (1=first/top, 2=second/bottom, etc.)
    """
    rgb_a = parse_color_string(color_a, dim)
    rgb_b = parse_color_string(color_b, dim)

    fli = Effects.for_name("blink")(
        rgb_a,
        off_color=rgb_b,
        count=count,
    )

    await busylightapi.apply_effect(fli, led=led)

    return {
        "action": "effect",
        "name": "fli",
        "light_id": "all",
        "speed": speed,
        "color": color_a,
        "dim": dim,
        "count": count,
        "led": led,
    }


@busylightapi.get(
    "/light/{light_id}/pulse",
    response_model=LightOperation,
)
async def pulse_light(
    light_id: int = Path(..., title="Numeric light identifier", ge=0),
    color: str = "red",
    speed: Speed = Speed.Slow,
    dim: float = 1.0,
    count: int = 0,
    led: int = 0,
) -> dict[str, Any]:
    """Pulse a light with a specified color [default: red].

    `light_id` is an integer value identifying a light and ranges
    between zero and number_of_lights-1.

    `count` is the number of times to blink the light.

    `led` parameter targets specific LEDs on multi-LED devices:
    - 0 = all LEDs (default)
    - 1+ = specific LED (1=first/top, 2=second/bottom, etc.)
    """
    rgb = parse_color_string(color, dim)

    throb = Effects.for_name("gradient")(rgb, step=8, count=count)

    await busylightapi.apply_effect(throb, light_id, led=led)

    return {
        "action": "effect",
        "name": "pulse",
        "light_id": light_id,
        "color": color,
        "rgb": rgb,
        "speed": speed,
        "dim": dim,
        "count": count,
        "led": led,
    }


@busylightapi.get(
    "/lights/pulse",
    response_model=LightOperation,
)
async def pulse_lights(
    color: str = "red",
    speed: Speed = Speed.Slow,
    dim: float = 1.0,
    count: int = 0,
    led: int = 0,
):
    """Pulse all lights with a color [default: red].

    `led` parameter targets specific LEDs on multi-LED devices:
    - 0 = all LEDs (default)
    - 1+ = specific LED (1=first/top, 2=second/bottom, etc.)
    """
    rgb = parse_color_string(color, dim)

    throb = Effects.for_name("gradient")(rgb, step=8, count=count)

    await busylightapi.apply_effect(throb, led=led)

    return {
        "action": "effect",
        "name": "pulse",
        "light_id": "all",
        "color": color,
        "speed": speed,
        "rgb": rgb,
        "dim": dim,
        "count": count,
        "led": led,
    }
