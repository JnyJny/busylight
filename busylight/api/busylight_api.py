"""BusyLight API
"""

from os import environ
from secrets import compare_digest
from typing import Callable, List, Dict, Any

from fastapi import Depends, FastAPI, HTTPException, Path, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from json import loads as json_loads
from loguru import logger

from .. import __version__
from ..__main__ import GlobalOptions

from ..color import parse_color_string, colortuple_to_name, ColorLookupError
from ..effects import Effects
from ..lights import Light
from ..lights import LightUnavailable, NoLightsFound
from ..speed import Speed


from .models import LightOperation, LightDescription, EndPoint


__description__ = """
<!-- markdown formatted for HTML rendering -->
An API server for USB connected presence lights.

[Source](https://github.com/JnyJny/busylight.git)
"""

# FastAPI Security Scheme
busylightapi_security = HTTPBasic()


class BusylightAPI(FastAPI):
    def __init__(self):

        # Get and save the debug flag
        global_options = GlobalOptions(debug=environ.get("BUSYLIGHT_DEBUG", False))
        logger.info("Debug: {debug_value}".format(debug_value=global_options.debug))

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

        # Get and save the CORS Access-Control-Allow-Origin header
        logger.info(
            "Set up CORS Access-Control-Allow-Origin header, if environment variable BUSYLIGHT_API_CORS_ORIGINS_LIST is set."
        )
        self.origins = json_loads(environ.get("BUSYLIGHT_API_CORS_ORIGINS_LIST", "[]"))

        # Validate that BUSYLIGHT_API_CORS_ORIGINS_LIST is a list of strings
        if (not isinstance(self.origins, list)) or any(
            not isinstance(item, str) for item in self.origins
        ):
            logger.warning(
                "BUSYLIGHT_API_CORS_ORIGINS_LIST is invalid: {origins_list}".format(
                    origins_list=self.origins
                )
            )
            logger.info("Will NOT set the CORS Access-Control-Allow-Origin header.")
            self.origins = None

        logger.info(
            "CORS Access-Control-Allow-Origin list: {origins_list}".format(
                origins_list=self.origins
            )
        )

        if (global_options.debug == True) and (self.origins == None):
            logger.info(
                'However, debug mode is enabled! Using debug mode CORS allowed origins: \'["http://localhost", "http://127.0.0.1"]\''
            )
            self.origins = ["http://localhost", "http://127.0.0.1"]

        super().__init__(
            title="Busylight Server: A USB Light Server",
            description=__description__,
            version=__version__,
            dependencies=dependencies,
        )
        self.lights: List[Light] = []
        self.endpoints: List[str] = []

    def update(self) -> None:

        self.lights.extend(Light.all_lights())

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

        # CORS allowed origins (for the Access-Control-Allow-Origin header)
        # are set through an environment variable BUSYLIGHT_API_CORS_ORIGINS_LIST
        # e.g.: export BUSYLIGHT_API_CORS_ORIGINS_LIST='["http://localhost", "http://localhost:8080"]'
        # (see https://fastapi.tiangolo.com/tutorial/cors/ for details)
        if self.origins:
            self.add_middleware(
                CORSMiddleware,
                allow_origins=self.origins,
            )

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
    try:
        await busylightapi.off()
    except Exception as error:
        logger.debug("problem during shutdown: {error}")


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


@busylightapi.exception_handler(NoLightsFound)
async def light_not_found_handler(
    request: Request,
    error: NoLightsFound,
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
async def available_endpoints() -> List[Dict[str, str]]:
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
    light_id: int = Path(..., title="Numeric light identifier", ge=0)
) -> Dict[str, Any]:
    """Information about the light selected by `light_id`."""
    light = busylightapi.lights[light_id]
    return {
        "light_id": light_id,
        "name": light.name,
        "info": light.info,
        "is_on": light.is_on,
        "color": colortuple_to_name(light.color),
        "rgb": light.color,
    }


@busylightapi.get(
    "/lights/status",
    response_model=List[LightDescription],
)
@busylightapi.get(
    "/lights",
    response_model=List[LightDescription],
)
async def lights_status() -> List[Dict[str, Any]]:
    """Information about all available lights."""
    result = []
    for light_id, light in enumerate(busylightapi.lights):
        result.append(
            {
                "light_id": light_id,
                "name": light.name,
                "info": light.info,
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
async def light_on(
    light_id: int = Path(..., title="Numeric light identifier", ge=0),
    color: str = "green",
    dim: float = 1.0,
) -> Dict[str, Any]:
    """Turn on the specified light with the given `color`.

    `light_id` is an integer value identifying a light and ranges
    between zero and number_of_lights-1.

    `color` can be a color name or a hexadecimal string e.g. "red",
    "#ff0000", "#f00", "0xff0000", "0xf00", "f00", "ff0000"
    """

    rgb = parse_color_string(color, dim)
    steady = Effects.for_name("steady")(rgb)
    await busylightapi.apply_effect(steady, light_id)

    return {
        "action": "on",
        "light_id": light_id,
        "color": color,
        "rgb": rgb,
        "dim": dim,
    }


@busylightapi.get(
    "/lights/on",
    response_model=LightOperation,
)
async def lights_on(
    color: str = "green",
    dim: float = 1.0,
) -> Dict[str, Any]:
    """Turn on all lights with the given `color`.

    `color` can be a color name or a hexadecimal string e.g. "red",
    "#ff0000", "#f00", "0xff0000", "0xf00", "f00", "ff0000"
    """

    rgb = parse_color_string(color, dim)
    steady = Effects.for_name("steady")(rgb)
    await busylightapi.apply_effect(steady)

    return {
        "action": "on",
        "light_id": "all",
        "color": color,
        "rgb": rgb,
        "dim": dim,
    }


@busylightapi.get(
    "/light/{light_id}/off",
    response_model=LightOperation,
)
async def light_off(
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
async def lights_off() -> Dict[str, Any]:
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
async def blink_light(
    light_id: int = Path(..., title="Numeric light identifier", ge=0),
    color: str = "red",
    speed: Speed = Speed.Slow,
    dim: float = 1.0,
) -> Dict[str, Any]:
    """Start blinking the specified light: color and off.

    `light_id` is an integer value identifying a light and ranges
    between zero and number_of_lights-1.

    The `color` can be a color name or a hexadecimal string: red,
    #ff0000, #f00, 0xff0000, 0xf00, f00, ff0000
    """

    rgb = parse_color_string(color, dim)

    effect = Effects.for_name("blink")(rgb, speed.duty_cycle)

    await busylightapi.apply_effect(effect, light_id)

    return {
        "action": "blink",
        "light_id": light_id,
        "color": color,
        "rgb": rgb,
        "speed": speed,
        "dim": dim,
    }


@busylightapi.get(
    "/lights/blink",
    response_model=LightOperation,
)
async def blink_lights(
    color: str = "red",
    speed: Speed = Speed.Slow,
    dim: float = 1.0,
) -> Dict[str, Any]:
    """Start blinking all the lights: red and off
    <p>Note: lights will not be synchronized.</p>
    """

    rgb = parse_color_string(color, dim)

    blink = Effects.for_name("blink")(rgb, speed.duty_cycle)

    await busylightapi.apply_effect(blink)

    return {
        "action": "blink",
        "light_id": "all",
        "color": "red",
        "rgb": rgb,
        "speed": speed,
        "dim": dim,
    }


@busylightapi.get(
    "/light/{light_id}/rainbow",
    response_model=LightOperation,
)
async def rainbow_light(
    light_id: int = Path(..., title="Numeric light identifier", ge=0),
    speed: Speed = Speed.Slow,
    dim: float = 1.0,
) -> Dict[str, Any]:
    """Start a rainbow animation on the specified light.

    `light_id` is an integer value identifying a light and ranges
    between zero and number_of_lights-1.
    """

    rainbow = Effects.for_name("spectrum")(speed.duty_cycle / 4, scale=dim)

    await busylightapi.apply_effect(rainbow, light_id)

    return {
        "action": "effect",
        "name": "rainbow",
        "light_id": light_id,
        "speed": speed,
        "dim": dim,
    }


@busylightapi.get(
    "/lights/rainbow",
    response_model=LightOperation,
)
async def rainbow_lights(
    speed: Speed = Speed.Slow,
    dim: float = 1.0,
) -> Dict[str, Any]:
    """Start a rainbow animation on all lights.
    <p><em>Note:</em> lights will not be synchronized.</p>
    """

    rainbow = Effects.for_name("spectrum")(speed.duty_cycle / 4, scale=dim)

    await busylightapi.apply_effect(rainbow)

    return {
        "action": "effect",
        "name": "rainbow",
        "light_id": "all",
        "dim": dim,
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
) -> Dict[str, Any]:
    """Flash the specified light impressively [default: red/blue].

    `light_id` is an integer value identifying a light and ranges
    between zero and number_of_lights-1.
    """

    rgb_a = parse_color_string(color_a, dim)
    rgb_b = parse_color_string(color_b, dim)

    fli = Effects.for_name("blink")(rgb_a, speed.duty_cycle / 10, off_color=rgb_b)

    await busylightapi.apply_effect(fli, light_id)

    return {
        "action": "effect",
        "name": "fli",
        "light_id": light_id,
        "speed": speed,
        "color": color_a,
        "dim": dim,
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
):
    """Flash all lights impressively [default: red/blue]"""

    rgb_a = parse_color_string(color_a, dim)
    rgb_b = parse_color_string(color_b, dim)

    fli = Effects.for_name("blink")(rgb_a, speed.duty_cycle / 10, off_color=rgb_b)

    await busylightapi.apply_effect(fli)

    return {
        "action": "effect",
        "name": "fli",
        "light_id": "all",
        "speed": speed,
        "color": color_a,
        "dim": dim,
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
) -> Dict[str, Any]:
    """Pulse a light with a specified color [default: red].

    `light_id` is an integer value identifying a light and ranges
    between zero and number_of_lights-1.
    """
    rgb = parse_color_string(color, dim)

    throb = Effects.for_name("Gradient")(rgb, speed.duty_cycle / 16, 8)

    await busylightapi.apply_effect(throb, light_id)

    return {
        "action": "effect",
        "name": "pulse",
        "light_id": light_id,
        "color": color,
        "rgb": rgb,
        "speed": speed,
        "dim": dim,
    }


@busylightapi.get(
    "/lights/pulse",
    response_model=LightOperation,
)
async def pulse_lights(
    color: str = "red",
    speed: Speed = Speed.Slow,
    dim: float = 1.0,
):
    """Pulse all lights with a color [default: red]."""

    rgb = parse_color_string(color, dim)

    throb = Effects.for_name("Gradient")(rgb, speed.duty_cycle / 16, 8)

    await busylightapi.apply_effect(throb)

    return {
        "action": "effect",
        "name": "pulse",
        "light_id": "all",
        "color": color,
        "speed": speed,
        "rgb": rgb,
        "dim": dim,
    }
