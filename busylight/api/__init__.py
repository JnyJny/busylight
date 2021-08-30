"""BusyLight API
"""

from os import environ
from secrets import compare_digest
from typing import Callable, List, Dict, Any

from fastapi import Depends, FastAPI, HTTPException, Path, Request, status
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from loguru import logger

from .models import LightOperation, LightDescription, EndPoint

from ..__version__ import __version__
from ..effects import rainbow, pulse, flash_lights_impressively
from ..manager import LightManager, BlinkSpeed
from ..manager import LightIdRangeError, ColorLookupError
from ..manager import ALL_LIGHTS
from ..color import rgb_to_hex

# FastAPI Security Scheme
busylightapi_security = HTTPBasic()

class BusylightAPI(FastAPI):
    def __init__(self):
        # Set up authentication, if env. variables set
        dependencies = []
        try:
            self.username = environ['BUSYLIGHT_API_USER']
            self.password = environ['BUSYLIGHT_API_PASS']
            dependencies.append(Depends(self.authenticate_user))
        except KeyError:
            # Env. variables not set, so auth disabled
            self.username = None
            self.password = None

        super().__init__(
            title="Busylight Server: A USB Light Server",
            description="""
<!-- markdown formatted for HTML rendering -->
An API server for USB connected presence lights.

**Supported USB lights:**
- Agile Innovative BlinkStick family of devices
- Embrava Blynclight, Blynclight +, Blynclight Mini
- Kuando BusyLight UC Omega
- Luxafor Flag
- Plantronics Status Indicator
- ThingM blink(1)
                        
[Source](https://github.com/JnyJny/busylight.git)
""",
            version=__version__,
            dependencies=dependencies,
        )
        self.manager: LightManager = None
        self.endpoints: List[str] = []

    def get(self, path: str, **kwargs) -> Callable:
        self.endpoints.append(path)
        kwargs.setdefault("response_model_exclude_unset", True)
        return super().get(path, **kwargs)
    
    def authenticate_user(
        self, 
        credentials: HTTPBasicCredentials = Depends(busylightapi_security)
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
    busylightapi.manager = LightManager()
    busylightapi.manager.light_off()


@busylightapi.on_event("shutdown")
async def shutdown():
    busylightapi.manager.light_off()


## Exception Handlers
##
@busylightapi.exception_handler(LightIdRangeError)
async def light_id_range_error_handler(
    request: Request,
    error: LightIdRangeError,
) -> JSONResponse:
    """Handle light_id values that are out of bounds."""
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

    logger.debug("pre manager.update")
    busylightapi.manager.update()
    logger.debug("post manager.update")
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
    light = busylightapi.manager.lights_for(light_id)[0]
    return {
        "light_id": light_id,
        "name": light.name,
        "info": light.info,
        "is_on": light.is_on,
        "color": rgb_to_hex(*light.color),
    }


@busylightapi.get(
    "/lights/status",
    response_model=List[LightDescription],
)
async def Lights_Description() -> List[Dict[str, Any]]:
    """Information about all available lights."""
    result = []
    for index, light in enumerate(busylightapi.manager.lights):
        result.append(
            {
                "light_id": index,
                "name": light.name,
                "info": light.info,
                "is_on": light.is_on,
                "color": rgb_to_hex(*light.color),
            }
        )
    return result


@busylightapi.get(
    "/light/{light_id}/on",
    response_model=LightOperation,
)
async def Turn_On_Light(
    light_id: int = Path(..., title="Numeric light identifier", ge=0),
) -> Dict[str, Any]:
    """Turn on the specified light with the default color, green."""
    busylightapi.manager.light_on(light_id)
    return {
        "action": "on",
        "light_id": light_id,
        "color": "green",
    }


@busylightapi.get(
    "/light/{light_id}/on/{color}",
    response_model=LightOperation,
)
async def Turn_On_Light_With_Color(
    light_id: int = Path(..., title="Numeric light identifier", ge=0),
    color: str = Path(..., title="Color name or hexadecimal string"),
) -> Dict[str, Any]:
    """Turn on the specified light with the given `color`.

    `light_id` is an integer value identifying a light and ranges
    between zero and number_of_lights-1.

    `color` can be a color name or a hexadecimal string e.g. "red",
    "#ff0000", "#f00", "0xff0000", "0xf00", "f00", "ff0000"
    """
    busylightapi.manager.light_on(light_id, color)
    return {
        "action": "on",
        "light_id": light_id,
        "color": color,
    }


@busylightapi.get(
    "/lights/on",
    response_model=LightOperation,
)
async def Turn_On_Lights() -> Dict[str, Any]:
    """Turn on all lights with the default color, green."""
    busylightapi.manager.light_on(ALL_LIGHTS)
    return {
        "action": "on",
        "light_id": "all",
        "color": "green",
    }


@busylightapi.get(
    "/lights/on/{color}",
    response_model=LightOperation,
)
async def Turn_On_Lights_With_Color(
    color: str = Path(..., title="Color name or hexadecimal string")
) -> Dict[str, Any]:
    """Turn on all lights with the given `color`.

    `color` can be a color name or a hexadecimal string e.g. "red",
    "#ff0000", "#f00", "0xff0000", "0xf00", "f00", "ff0000"
    """
    busylightapi.manager.light_on(ALL_LIGHTS, color)
    return {
        "action": "on",
        "light_id": "all",
        "color": color,
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
    busylightapi.manager.light_off(light_id)
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
    busylightapi.manager.light_off(ALL_LIGHTS)
    return {
        "action": "off",
        "light_id": "all",
    }


@busylightapi.get(
    "/light/{light_id}/blink",
    response_model=LightOperation,
)
async def Blink_Light(
    light_id: int = Path(..., title="Numeric light identifier", ge=0)
) -> Dict[str, Any]:
    """Start blinking the specified light: red and off.

    `light_id` is an integer value identifying a light and ranges
    between zero and number_of_lights-1.

    """
    busylightapi.manager.light_blink(light_id)
    return {
        "action": "blink",
        "light_id": light_id,
        "color": "red",
        "speed": BlinkSpeed.SLOW,
    }


@busylightapi.get(
    "/light/{light_id}/blink/{color}",
    response_model=LightOperation,
)
async def Blink_Light_With_Color(
    light_id: int = Path(..., title="Numeric light identifier", ge=0),
    color: str = Path(..., title="Color name or hexadecimal string"),
) -> Dict[str, Any]:
    """Start blinking the specified light: color and off.

    `light_id` is an integer value identifying a light and ranges
    between zero and number_of_lights-1.

    The `color` can be a color name or a hexadecimal string: red,
    #ff0000, #f00, 0xff0000, 0xf00, f00, ff0000
    """
    busylightapi.manager.light_blink(light_id, color)
    return {
        "action": "blink",
        "light_id": light_id,
        "color": color,
        "speed": BlinkSpeed.SLOW,
    }


@busylightapi.get(
    "/light/{light_id}/blink/{color}/{speed}",
    response_model=LightOperation,
)
async def Blink_Light_With_Color_and_Speed(
    light_id: int = Path(..., title="Numeric light identifier", ge=0),
    color: str = Path(..., title="Color name or hexadecimal string"),
    speed: BlinkSpeed = Path(..., title="Speed: slow, medium, fast"),
) -> Dict[str, Any]:
    """Start blinking the specified light using `color` and `speed`.

    `light_id` is an integer value identifying a light and ranges
    between zero and number_of_lights-1.

    `color` can be a color name or a hexadecimal string e.g. "red",
    "#ff0000", "#f00", "0xff0000", "0xf00", "f00", "ff0000"

    `speed` should be a string "slow", "medium" or "fast".
    """
    busylightapi.manager.light_blink(light_id, color, speed)
    return {
        "action": "blink",
        "light_id": light_id,
        "color": color,
        "speed": speed,
    }


@busylightapi.get(
    "/lights/blink",
    response_model=LightOperation,
)
async def Blink_Lights() -> Dict[str, Any]:
    """Start blinking all the lights: red and off
    <p>Note: lights will not be synchronized.</p>
    """
    busylightapi.manager.light_blink(ALL_LIGHTS)
    return {
        "action": "blink",
        "light_id": "all",
        "color": "red",
        "speed": "slow",
    }


@busylightapi.get(
    "/lights/blink/{color}",
    response_model=LightOperation,
)
async def Blink_Lights_With_Color(
    color: str = Path(..., title="Color name or hexadecimal string")
) -> Dict[str, Any]:
    """Start blinking all the lights: `color` and off.
    <p>
    `color` can be a color name or a hexadecimal string e.g. "red",
    "#ff0000", "#f00", "0xff0000", "0xf00", "f00", "ff0000"
    <p><em>Note:</em> Lights will not be synchronized.</p>
    """
    busylightapi.manager.light_blink(ALL_LIGHTS, color)
    return {
        "action": "blink",
        "light_id": "all",
        "color": color,
        "speed": "slow",
    }


@busylightapi.get(
    "/lights/blink/{color}/{speed}",
    response_model=LightOperation,
)
async def Blink_Lights_With_Color_and_Speed(
    color: str = Path(..., title="Color name or hexadecimal string"),
    speed: BlinkSpeed = Path(..., title="Speed: slow, medium, fast"),
) -> Dict[str, Any]:
    """Start blinking all the lights: `color` and off with the specified speed.

    <p>`color` can be a color name or a hexadecimal string e.g. "red",
    "#ff0000", "#f00", "0xff0000", "0xf00", "f00", "ff0000"
    <p><em>Note:</em> Lights will not be synchronized.</p>
    """
    busylightapi.manager.light_blink(ALL_LIGHTS, color, speed)
    return {
        "action": "blink",
        "light_id": "all",
        "color": color,
        "speed": speed,
    }


@busylightapi.get(
    "/light/{light_id}/rainbow",
    response_model=LightOperation,
)
async def Rainbow_Light(
    light_id: int = Path(..., title="Numeric light identifier", ge=0)
) -> Dict[str, Any]:
    """Start a rainbow animation on the specified light.

    `light_id` is an integer value identifying a light and ranges
    between zero and number_of_lights-1.
    """

    busylightapi.manager.apply_effect_to_light(light_id, rainbow)
    return {
        "action": "effect",
        "name": "rainbow",
        "light_id": light_id,
    }


@busylightapi.get(
    "/lights/rainbow",
    response_model=LightOperation,
)
async def Rainbow_Lights():
    """Start a rainbow animation on all lights.
    <p><em>Note:</em> lights will not be synchronized.</p>
    """
    busylightapi.manager.apply_effect_to_light(ALL_LIGHTS, rainbow)
    return {
        "action": "effect",
        "name": "rainbow",
        "light_id": "all",
    }


@busylightapi.get(
    "/light/{light_id}/fli",
    response_model=LightOperation,
)
async def Flash_Light_Impressively(
    light_id: int = Path(..., title="Numeric light identifier", ge=0)
) -> Dict[str, Any]:
    """Flash the specified light impressively.

    `light_id` is an integer value identifying a light and ranges
    between zero and number_of_lights-1.
    """
    busylightapi.manager.apply_effect_to_light(light_id, flash_lights_impressively)
    return {
        "action": "effect",
        "name": "fli",
        "light_id": light_id,
    }


@busylightapi.get(
    "/lights/fli",
    response_model=LightOperation,
)
async def Flash_Lights_Impressively():
    """Flash all lights impressively."""
    busylightapi.manager.apply_effect_to_light(ALL_LIGHTS, flash_lights_impressively)
    return {
        "action": "effect",
        "name": "fli",
        "light_id": "all",
    }


@busylightapi.get(
    "/light/{light_id}/pulse",
    response_model=LightOperation,
)
async def Pulse_Light(
    light_id: int = Path(..., title="Numeric light identifier", ge=0)
) -> Dict[str, Any]:
    """Pulse a light red.

    `light_id` is an integer value identifying a light and ranges
    between zero and number_of_lights-1.
    """
    busylightapi.manager.apply_effect_to_light(light_id, pulse)
    return {
        "action": "effect",
        "name": "pulse",
        "light_id": light_id,
        "color": "red",
    }


@busylightapi.get(
    "/light/{light_id}/pulse/{color}",
    response_model=LightOperation,
)
async def Pulse_Light_With_Color(
    light_id: int = Path(..., title="Numeric light identifier", ge=0),
    color: str = Path(..., title="Color name or hexadecimal string"),
) -> Dict[str, Any]:
    """Pulse a light with the specified color.

    `light_id` is an integer value identifying a light and ranges
    between zero and number_of_lights-1.

    `color` can be a color name or a hexadecimal string e.g. "red",
    "#ff0000", "#f00", "0xff0000", "0xf00", "f00", "ff0000"
    """
    busylightapi.manager.apply_effect_to_light(light_id, pulse, color=color)
    return {
        "action": "effect",
        "name": "pulse",
        "light_id": light_id,
        "color": color,
    }


@busylightapi.get(
    "/lights/pulse",
    response_model=LightOperation,
)
async def Pulse_Lights():
    """Pulse all lights red."""
    busylightapi.manager.apply_effect_to_light(ALL_LIGHTS, pulse)
    return {
        "action": "effect",
        "name": "pulse",
        "light_id": "all",
        "color": "red",
    }


@busylightapi.get(
    "/lights/pulse/{color}",
    response_model=LightOperation,
)
async def Pulse_Lights_With_Color(
    color: str = Path(..., title="Color name or hexadecimal string")
):
    """Pulse all lights with the specified color.

    `color` can be a color name or a hexadecimal string e.g. "red",
    "#ff0000", "#f00", "0xff0000", "0xf00", "f00", "ff0000"
    """
    busylightapi.manager.apply_effect_to_light(ALL_LIGHTS, pulse, color=color)
    return {
        "action": "effect",
        "name": "pulse",
        "light_id": "all",
        "color": color,
    }


# @busylightapi.get("/light", response_model=LightOperation)
# async def Light(
#    light_id: int = 0,
#    operation: str = "on",
#    color: str = "green",
#    speed: str = None,
#    name: str = None,
# ) -> Dict[str, Any]:
#    """Query style interface to interact with one light.
#
#    `light_id` is an integer value identifying a light and ranges
#    between zero and number_of_lights-1.
#
#    `op` is a string; "on", "off", "blink", "pulse", "fli", "rainbow"
#
#    `color` can be a color name or a hexadecimal string e.g. "red",
#    "#ff0000", "#f00", "0xff0000", "0xf00", "f00", "ff0000"
#
#    `speed` should be None, "slow", "medium", "fast"
#    """
#
#    return {
#        "light_id": light_id,
#        "action": op,
#        "color": color,
#        "speed": speed,
#    }
#
#
# @busylightapi.get("/lights", response_model=LightOperation)
# async def Light(
#    operation: str = "on",
#    color: str = "green",
#    speed: str = None,
#    name: str = None,
# ) -> Dict[str, Any]:
#    """Query style interface to interact with all light.
#
#    `op` is a string; "on", "off", "blink", "pulse", "fli", "rainbow"
#
#    `color` can be a color name or a hexadecimal string e.g. "red",
#    "#ff0000", "#f00", "0xff0000", "0xf00", "f00", "ff0000"
#
#    `speed` should be None, "slow", "medium", or "fast"
#    """
#
#    return {
#        "light_id": "all",
#        "action": op,
#        "color": color,
#        "speed": speed,
#    }
