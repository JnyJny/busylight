"""BusyLight API
"""

import asyncio

from typing import List

from fastapi import FastAPI, HTTPException, Path, Request
from fastapi.responses import JSONResponse


from .models import LightOperation, LightDescription

from ..__version__ import __version__
from ..effects import rainbow, pulse, flash_lights_impressively
from ..manager import LightManager, BlinkSpeed
from ..manager import LightIdRangeError, ColorLookupError


server = FastAPI(
    title="Busylight API Server",
    description="""An API server for USB connected presence lights.

**Supported USB lights:**
- Embrava Blynclight, Blynclight +, Blynclight Mini
- ThingM blink(1)
- Luxafor Flag
- Kuando BusyLight UC Omega
- Agile Innovations BlinkStick family of devices.

[Source](https://github.com/JnyJny/busylight.git)
""",
    version=__version__,
)


##
## Startup & Shutdown
##


@server.on_event("startup")
async def startup():
    server.manager = LightManager()
    server.manager.light_off()


@server.on_event("shutdown")
async def shutdown():
    server.manager.light_off()


##
## Exception Handlers
##


@server.exception_handler(LightIdRangeError)
async def light_id_range_error_handler(request: Request, error: LightIdRangeError):
    """Handle light_id values that are out of bounds.
    """
    return JSONResponse(status_code=404, content={"message": str(error)},)


@server.exception_handler(ColorLookupError)
async def color_lookup_error_handler(request: Request, error: ColorLookupError):
    """Handle color strings that do not result in a valid color.
    """
    return JSONResponse(status_code=404, content={"message": str(error)})


##
## Middleware Handlers
##


@server.middleware("http")
async def light_manager_update(request: Request, call_next):
    """Check for plug/unplug events and update the light manager.
    """
    server.manager.update()
    return await call_next(request)


##
## API Routes
##


@server.get("/1/light/{light_id}", response_model=LightDescription)
async def Light_Description(
    light_id: int = Path(..., title="Light identifier", ge=0)
) -> dict:
    """Information about the light selected by `light_id`.
    """

    light = server.manager.lights[light_id]
    return {
        "light_id": light_id,
        "name": light.name,
        "info": light.info,
    }


@server.get("/1/lights", response_model=List[LightDescription])
async def Lights_Description() -> dict:
    """Information about all available lights.
    """
    result = []
    for index, light in enumerate(server.manager.lights):
        result.append(
            {"light_id": index, "name": light.name, "info": light.info,}
        )
    return result


@server.get(
    "/1/light/{light_id}/on",
    response_model=LightOperation,
    response_model_exclude_unset=True,
)
async def Turn_On_Light(light_id: int = Path(..., title="Light identifier", ge=0)):
    """Turn on the specified light with the default color, green.
    """

    server.manager.light_on(light_id)
    return {"action": "on", "light_id": light_id, "color": "green"}


@server.get(
    "/1/light/{light_id}/on/{color}",
    response_model=LightOperation,
    response_model_exclude_unset=True,
)
async def Turn_On_Light_With_Color(
    light_id: int = Path(..., title="Light identifier", ge=0),
    color: str = Path(..., title="Color specifier string"),
):
    """Turn on the specified light with the given `color`. 
    
    The `color` can be a color name or a hexadecimal
    string: red, #ff0000, #f00, 0xff0000, 0xf00, f00, ff0000
    """

    server.manager.light_on(light_id, color)

    return {"action": "on", "light_id": light_id, "color": color}


@server.get(
    "/1/lights/on", response_model=LightOperation, response_model_exclude_unset=True,
)
async def Turn_On_Lights() -> dict:
    """Turn on all lights with the default color, green.
    """

    server.manager.light_on(-1)
    return {"action": "on", "light_id": "all", "color": "green"}


@server.get(
    "/1/lights/on/{color}",
    response_model=LightOperation,
    response_model_exclude_unset=True,
)
async def Turn_On_Lights_With_Color(
    color: str = Path(..., title="Color specifier string")
) -> dict:
    """Turn on all lights with the given `color`.

    The `color` can be a color name or a hexadecimal string: red,
    #ff0000, #f00, 0xff0000, 0xf00, f00, ff0000
    """

    server.manager.light_on(-1, color)
    return {"action": "on", "light_id": "all", "color": color}


@server.get(
    "/1/light/{light_id}/off",
    response_model=LightOperation,
    response_model_exclude_unset=True,
)
async def Turn_Off_Light(
    light_id: int = Path(..., title="Light identifier", ge=0)
) -> dict:

    """Turn off the specified light.
    """

    server.manager.light_off(light_id)
    return {"action": "off", "light_id": light_id}


@server.get(
    "/1/lights/off", response_model=LightOperation, response_model_exclude_unset=True,
)
async def Turn_Off_Lights() -> dict:
    """Turn off all lights.
    """

    server.manager.light_off(-1)
    return {"action": "off", "light_id": "all"}


@server.get(
    "/1/light/{light_id}/blink",
    response_model=LightOperation,
    response_model_exclude_unset=True,
)
async def Blink_Light(
    light_id: int = Path(..., title="Light identifier", ge=0)
) -> dict:
    """Start blinking the specified light: red and off.
    """

    server.manager.light_blink(light_id)
    return {
        "action": "blink",
        "light_id": light_id,
        "color": "red",
        "speed": BlinkSpeed.SLOW,
    }


@server.get(
    "/1/light/{light_id}/blink/{color}",
    response_model=LightOperation,
    response_model_exclude_unset=True,
)
async def Blink_Light_With_Color(
    light_id: int = Path(..., title="Light identifier", ge=0),
    color: str = Path(..., title="Color specifier string"),
) -> dict:
    """Start blinking the specified light: color and off.

    The `color` can be a color name or a hexadecimal string: red,
    #ff0000, #f00, 0xff0000, 0xf00, f00, ff0000
    """

    server.manager.light_blink(light_id, color)
    return {
        "action": "blink",
        "light_id": light_id,
        "color": color,
        "speed": BlinkSpeed.SLOW,
    }


@server.get(
    "/1/light/{light_id}/blink/{color}/{speed}",
    response_model=LightOperation,
    response_model_exclude_unset=True,
)
async def Blink_Light_With_Color_and_Speed(
    light_id: int = Path(..., title="Light identifier", ge=0),
    color: str = Path(..., title="Color specifier string"),
    speed: BlinkSpeed = Path(..., title="Speed: slow, medium, fast"),
) -> dict:
    """Start blinking the specified light: `color` and off with the specified `speed`.
    
    The `color` can be a color name or a hexadecimal string: red,
    #ff0000, #f00, 0xff0000, 0xf00, f00, ff0000
    """

    server.manager.light_blink(light_id, color, speed)
    return {"action": "blink", "light_id": light_id, "color": color, "speed": speed}


@server.get(
    "/1/lights/blink", response_model=LightOperation, response_model_exclude_unset=True,
)
async def Blink_Lights() -> dict:
    """Start blinking all the lights: red and off
    <p>Note: lights will not be synchronized.</p>
    """

    server.manager.light_blink(-1)
    return {"action": "blink", "light_id": "all", "color": "red", "speed": "slow"}


@server.get(
    "/1/lights/blink/{color}",
    response_model=LightOperation,
    response_model_exclude_unset=True,
)
async def Blink_Lights_With_Color(
    color: str = Path(..., title="Color specifier string")
) -> dict:
    """Start blinking all the lights: `color` and off.
    <p>
    The `color` can be a color name or a hexadecimal
    string: red, #ff0000, #f00, 0xff0000, 0xf00, f00, ff0000</p>
    <p><em>Note:</em> Lights will not be synchronized.</p>
    """

    server.manager.light_blink(-1, color)
    return {
        "action": "blink",
        "light_id": "all",
        "color": color,
        "speed": "slow",
    }


@server.get(
    "/1/lights/blink/{color}/{speed}",
    response_model=LightOperation,
    response_model_exclude_unset=True,
)
async def Blink_Lights_With_Color_and_Speed(
    color: str = Path(..., title="Color specifier string"),
    speed: BlinkSpeed = Path(..., title="Speed: slow, medium, fast"),
) -> dict:
    """Start blinking all the lights: `color` and off with the specified speed.
  
    <p>The `color` can be a color name or a hexadecimal string: red,
    #ff0000, #f00, 0xff0000, 0xf00, f00, ff0000 </p>
    <p><em>Note:</em> Lights will not be synchronized.</p>
    """

    server.manager.light_blink(-1, color, speed)
    return {"action": "blink", "light_id": "all", "color": color, "speed": speed}


@server.get(
    "/1/light/{light_id}/rainbow",
    response_model=LightOperation,
    response_model_exclude_unset=True,
)
async def Rainbow_Light(
    light_id: int = Path(..., title="Light identifier", ge=0)
) -> dict:
    """Start a rainbow animation on the specified light.
    """

    server.manager.apply_effect_to_light(light_id, rainbow)
    return {"action": "effect", "name": "rainbow", "light_id": light_id}


@server.get(
    "/1/lights/rainbow",
    response_model=LightOperation,
    response_model_exclude_unset=True,
)
async def Rainbow_Lights():
    """Start a rainbow animation on all lights.
    <p><em>Note:</em> lights will not be synchronized.</p>
    """

    server.manager.apply_effect_to_light(-1, rainbow)
    return {"action": "effect", "name": "rainbow", "light_id": "all"}


@server.get(
    "/1/light/{light_id}/fli",
    response_model=LightOperation,
    response_model_exclude_unset=True,
)
async def Flash_Light_Impressively(
    light_id: int = Path(..., title="Light identifier", ge=0)
) -> dict:
    """Flash the specified light impressively.
    """

    server.manager.apply_effect_to_light(light_id, flash_lights_impressively)
    return {"action": "effect", "name": "fli", "light_id": light_id}


@server.get(
    "/1/lights/fli", response_model=LightOperation, response_model_exclude_unset=True
)
async def Flash_Lights_Impressively():
    """Flash all lights impressively.
    """

    server.manager.apply_effect_to_light(-1, flash_lights_impressively)
    return {"action": "effect", "name": "fli", "light_id": "all"}


@server.get(
    "/1/light/{light_id}/pulse",
    response_model=LightOperation,
    response_model_exclude_unset=True,
)
async def Pulse_Light(
    light_id: int = Path(..., title="Light identifier", ge=0)
) -> dict:
    """Pulse a light red.
    """
    server.manager.apply_effect_to_light(light_id, pulse)
    return {"action": "effect", "name": "pulse", "light_id": light_id, "color": "red"}


@server.get(
    "/1/light/{light_id}/pulse/{color}",
    response_model=LightOperation,
    response_model_exclude_unset=True,
)
async def Pulse_Light_With_Color(
    light_id: int = Path(..., title="Light identifier", ge=0),
    color: str = Path(..., title="Color specifier string"),
) -> dict:
    """Pulse a light with the specified color.
    """

    server.manager.apply_effect_to_light(light_id, pulse, color=color)
    return {"action": "effect", "name": "pulse", "light_id": light_id, "color": color}


@server.get(
    "/1/lights/pulse", response_model=LightOperation, response_model_exclude_unset=True
)
async def Pulse_Lights():
    """Pulse all lights red.
    """

    server.manager.apply_effect_to_light(-1, pulse)

    return {"action": "effect", "name": "pulse", "light_id": "all", "color": "red"}


@server.get(
    "/1/lights/pulse/{color}",
    response_model=LightOperation,
    response_model_exclude_unset=True,
)
async def Pulse_Lights_With_Color(
    color: str = Path(..., title="Color specifier string")
):
    """Pulse all lights with the specified color.
    """

    server.manager.apply_effect_to_light(-1, pulse, color=color)

    return {"action": "effect", "name": "pulse", "light_id": "all", "color": color}
