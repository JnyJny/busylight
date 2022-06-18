"""BusyLight API
"""

from os import environ
from secrets import compare_digest
from typing import Callable, List, Dict, Any

from fastapi import Depends, FastAPI, HTTPException, Path, Request, status
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from loguru import logger

from .. import __version__

from ..color import ColorTuple, parse_color, colortuple_to_name, ColorLookupError
from ..effects import Effects
from ..lights import USBLight, Speed
from ..lights import LightUnavailable, NoLightsFound, LightNotFound


from .models import LightOperation, LightDescription, EndPoint


__description__ = """
<!-- markdown formatted for HTML rendering -->
An API server for USB connected presence lights.

**Supported USB lights:**
_Agile Innovative_
  - BlinkStick
  - BlinkStick Pro
  - BlinkStick Square
  - BlinkStick Strip
  - BlinkStick Nano
  - BlinkStick Flex
_Embrava_
  - Blynclight
  - Blynclight Mini
  - Blynclight Plus
_Plantronics_
  - Status Indicator
_Kuando_
  - Busylight Alpha
  - Busylight Omega
_Luxafor_
  - Flag
  - Mute
  - Orb
_ThingM_
  - Blink(1)

[Source](https://github.com/JnyJny/busylight.git)
"""

# FastAPI Security Scheme
busylightapi_security = HTTPBasic()


class BusylightAPI(FastAPI):
    def __init__(self):

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

        super().__init__(
            title="Busylight Server: A USB Light Server",
            description=__description__,
            version=__version__,
            dependencies=dependencies,
        )
        self.lights: List[USBLight] = []
        self.endpoints: List[str] = []

    def update(self) -> None:

        self.lights.extend(USBLight.all_lights())

    def release(self) -> None:

        for light in self.lights:
            light.release()

        self.lights.clear()

    async def off(self, light_id: int = None) -> None:

        lights = self.lights if light_id is None else [self.lights[light_id]]

        for light in lights:
            light.off()

    async def apply_effect(self, effect: Effects, light_id: int = None) -> None:

        lights = self.lights if light_id is None else [self.lights[light_id]]

        for light in lights:
            # EJO cancel_tasks will cancel any keepalive tasks, but that's ok
            #     since we are going to drive the light with an active effect
            #     which will re-start any keepalive tasks if necessary.
            light.cancel_tasks()
            light.add_task(effect.name, effect)

    def get(self, path: str, **kwargs) -> Callable:
        self.endpoints.append(path)
        kwargs.setdefault("response_model_exclude_unset", True)
        return super().get(path, **kwargs)

    def authenticate_user(
        self, credentials: HTTPBasicCredentials = Depends(busylightapi_security)
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

## Startup & Shutdown
##
@busylightapi.on_event("startup")
async def startup():
    busylightapi.update()
    await busylightapi.off()


@busylightapi.on_event("shutdown")
async def shutdown():
    await busylightapi.off()


## Exception Handlers
##
@busylightapi.exception_handler(LightUnavailable)
async def light_unavailable_handler(
    request: Request,
    error: LightUnavailable,
) -> JSONResponse:
    """Handle lights which are unavailable."""
    return JSONResponse(
        status_code=404,
        content={"message": str(error)},
    )


@busylightapi.exception_handler(LightNotFound)
async def light_not_found_handler(
    request: Request,
    error: LightNotFound,
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


## Middleware Handlers
##
@busylightapi.middleware("http")
async def light_manager_update(request: Request, call_next):
    """Check for plug/unplug events and update the light manager."""

    busylightapi.update()

    return await call_next(request)


## GET API Routes
##
@busylightapi.get("/", response_model=List[EndPoint])
async def Available_Endpoints() -> List[Dict[str, str]]:
    """API endpoint listing.

    List of valid endpoints recognized by this API.
    """
    return [{"path": endpoint} for endpoint in busylightapi.endpoints]


@busylightapi.get(
    "/light/{light_id}/status",
    response_model=LightDescription,
)
async def Light_Description(
    light_id: int = Path(..., title="Numeric light identifier", ge=0)
) -> Dict[str, Any]:
    """Information about the light selected by `light_id`."""
    light = busylightapi.lights[light_id]
    return {
        "light_id": light_id,
        "name": light.name,
        "info": light.hidinfo,
        "is_on": light.is_on,
        "color": colortuple_to_name(light.color),
        "rgb": light.color,
    }


@busylightapi.get(
    "/lights/status",
    response_model=List[LightDescription],
)
async def Lights_Description() -> List[Dict[str, Any]]:
    """Information about all available lights."""
    result = []
    for light_id, light in enumerate(busylightapi.lights):
        result.append(
            {
                "light_id": light_id,
                "name": light.name,
                "info": light.hidinfo,
                "is_on": light.is_on,
                "color": colortuple_to_name(light.color),
                "rgb": light.color,
            }
        )
    return result


@busylightapi.get(
    "/light/{light_id}/on",
    response_model=LightOperation,
)
async def Turn_On_Light_With_Optional_Color(
    light_id: int = Path(..., title="Numeric light identifier", ge=0),
    color: str = "green",
) -> Dict[str, Any]:
    """Turn on the specified light with the given `color`.

    `light_id` is an integer value identifying a light and ranges
    between zero and number_of_lights-1.

    `color` can be a color name or a hexadecimal string e.g. "red",
    "#ff0000", "#f00", "0xff0000", "0xf00", "f00", "ff0000"
    """

    rgb = parse_color(color)
    steady = Effects.for_name("steady")(rgb)
    await busylightapi.apply_effect(steady, light_id)

    return {
        "action": "on",
        "light_id": light_id,
        "color": color,
        "rgb": rgb,
    }


@busylightapi.get(
    "/lights/on",
    response_model=LightOperation,
)
async def Turn_On_Lights_With_Optional_Color(color: str = "green") -> Dict[str, Any]:
    """Turn on all lights with the given `color`.

    `color` can be a color name or a hexadecimal string e.g. "red",
    "#ff0000", "#f00", "0xff0000", "0xf00", "f00", "ff0000"
    """

    rgb = parse_color(color)
    steady = Effects.for_name("steady")(rgb)
    await busylightapi.apply_effect(steady)

    return {
        "action": "on",
        "light_id": "all",
        "color": color,
        "rgb": rgb,
    }


@busylightapi.get(
    "/light/{light_id}/off",
    response_model=LightOperation,
)
async def Turn_Off_Light(
    light_id: int = Path(..., title="Numeric light identifier", ge=0)
) -> Dict[str, Any]:
    """Turn off the specified light.
    `light_id` is an integer value identifying a light and ranges
    between zero and number_of_lights-1.

    `color` can be a color name or a hexadecimal string e.g. "red",
    "#ff0000", "#f00", "0xff0000", "0xf00", "f00", "ff0000"
    """

    await busylightapi.off(light_id)

    return {
        "action": "off",
        "light_id": light_id,
    }


@busylightapi.get(
    "/lights/off",
    response_model=LightOperation,
)
async def Turn_Off_Lights() -> Dict[str, Any]:
    """Turn off all lights."""

    await busylightapi.off()

    return {
        "action": "off",
        "light_id": "all",
    }


@busylightapi.get(
    "/light/{light_id}/blink",
    response_model=LightOperation,
)
async def Blink_Light_With_Optional_Color_And_Speed(
    light_id: int = Path(..., title="Numeric light identifier", ge=0),
    color: str = "red",
    speed: Speed = Speed.Slow,
) -> Dict[str, Any]:
    """Start blinking the specified light: color and off.

    `light_id` is an integer value identifying a light and ranges
    between zero and number_of_lights-1.

    The `color` can be a color name or a hexadecimal string: red,
    #ff0000, #f00, 0xff0000, 0xf00, f00, ff0000
    """

    rgb = parse_color(color)

    effect = Effects.for_name("blink")(rgb, speed.duty_cycle)

    await busylightapi.apply_effect(effect, light_id)

    return {
        "action": "blink",
        "light_id": light_id,
        "color": color,
        "rgb": rgb,
        "speed": speed,
    }


@busylightapi.get(
    "/lights/blink",
    response_model=LightOperation,
)
async def Blink_Lights_With_Optional_Color_And_Speed(
    color: str = "red",
    speed: Speed = Speed.Slow,
) -> Dict[str, Any]:
    """Start blinking all the lights: red and off
    <p>Note: lights will not be synchronized.</p>
    """

    rgb = parse_color(color)

    blink = Effects.for_name("blink")(rgb, speed.duty_cycle)

    await busylightapi.apply_effect(blink)

    return {
        "action": "blink",
        "light_id": "all",
        "color": "red",
        "rgb": rgb,
        "speed": speed,
    }


@busylightapi.get(
    "/light/{light_id}/rainbow",
    response_model=LightOperation,
)
async def Rainbow_Light_With_Optional_Speed(
    light_id: int = Path(..., title="Numeric light identifier", ge=0),
    speed: Speed = Speed.Slow,
) -> Dict[str, Any]:
    """Start a rainbow animation on the specified light.

    `light_id` is an integer value identifying a light and ranges
    between zero and number_of_lights-1.
    """

    rainbow = Effects.for_name("spectrum")(speed.duty_cycle / 4)

    await busylightapi.apply_effect(rainbow, light_id)

    return {
        "action": "effect",
        "name": "rainbow",
        "light_id": light_id,
        "speed": speed,
    }


@busylightapi.get(
    "/lights/rainbow",
    response_model=LightOperation,
)
async def Rainbow_Lights_With_Optional_Speed(
    speed: Speed = Speed.Slow,
) -> Dict[str, Any]:
    """Start a rainbow animation on all lights.
    <p><em>Note:</em> lights will not be synchronized.</p>
    """

    rainbow = Effects.for_name("spectrum")(speed.duty_cycle / 4)

    await busylightapi.apply_effect(rainbow)

    return {
        "action": "effect",
        "name": "rainbow",
        "light_id": "all",
    }


@busylightapi.get(
    "/light/{light_id}/fli",
    response_model=LightOperation,
)
async def Flash_Light_Impressively_With_Optional_Colors_And_Speed(
    light_id: int = Path(..., title="Numeric light identifier", ge=0),
    color_a: str = "red",
    color_b: str = "blue",
    speed: Speed = Speed.Slow,
) -> Dict[str, Any]:
    """Flash the specified light impressively [default: red/blue].

    `light_id` is an integer value identifying a light and ranges
    between zero and number_of_lights-1.
    """

    rgb_a = parse_color(color_a)
    rgb_b = parse_color(color_b)

    fli = Effects.for_name("blink")(rgb_a, speed.duty_cycle / 10, off_color=rgb_b)

    await busylightapi.apply_effect(fli, light_id)

    return {
        "action": "effect",
        "name": "fli",
        "light_id": light_id,
        "speed": speed,
        "color": color_a,
    }


@busylightapi.get(
    "/lights/fli",
    response_model=LightOperation,
)
async def Flash_Lights_Impressively_With_Optional_Colors_And_Speed(
    color_a: str = "red",
    color_b: str = "blue",
    speed: Speed = Speed.Slow,
):
    """Flash all lights impressively [default: red/blue]"""

    rgb_a = parse_color(color_a)
    rgb_b = parse_color(color_b)

    fli = Effects.for_name("blink")(rgb_a, speed.duty_cycle / 10, off_color=rgb_b)

    await busylightapi.apply_effect(fli)

    return {
        "action": "effect",
        "name": "fli",
        "light_id": "all",
        "speed": speed,
        "color": color_a,
    }


@busylightapi.get(
    "/light/{light_id}/pulse",
    response_model=LightOperation,
)
async def Pulse_Light_With_Optional_Color_And_Speed(
    light_id: int = Path(..., title="Numeric light identifier", ge=0),
    color: str = "red",
    speed: Speed = Speed.Slow,
) -> Dict[str, Any]:
    """Pulse a light with a specified color [default: red].

    `light_id` is an integer value identifying a light and ranges
    between zero and number_of_lights-1.
    """
    rgb = parse_color(color)

    throb = Effects.for_name("throb")(rgb, speed.duty_cycle / 16, 8)

    await busylightapi.apply_effect(throb, light_id)

    return {
        "action": "effect",
        "name": "pulse",
        "light_id": light_id,
        "color": color,
        "rgb": rgb,
        "speed": speed,
    }


@busylightapi.get(
    "/lights/pulse",
    response_model=LightOperation,
)
async def Pulse_Lights_With_Optional_Color_And_Speed(
    color: str = "red",
    speed: Speed = Speed.Slow,
):
    """Pulse all lights with a color [default: red]."""

    rgb = parse_color(color)

    throb = Effects.for_name("throb")(rgb, speed.duty_cycle / 16, 8)

    await busylight.apply_effect(throb)

    return {
        "action": "effect",
        "name": "pulse",
        "light_id": "all",
        "color": color,
        "speed": speed,
        "rgb": rgb,
    }
