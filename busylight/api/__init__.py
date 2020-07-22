"""BusyLight API
"""

import asyncio
from typing import List

from fastapi import FastAPI, HTTPException, Path, Request
from fastapi.responses import JSONResponse

from .exceptions import LightIdRangeError, ColorLookupError
from .models import LightOperation, LightDescription

from ..__version__ import __version__
from ..effects import rainbow, throbber, flash_lights_impressively
from ..manager import LightManager, BlinkSpeed


api = FastAPI(
    title="Busylight API Server",
    description="""An API server for USB connected presense lights.

**Supported USB lights:**
- Embrava BlyncLight, BlyncLight +, BlyncLight Mini
- ThingM blink(1)
- Luxafor Flag
- Kuando BusyLight UC Omega

[Source](https://github.com/JnyJny/busylight.git)
""",
    version=__version__,
)


##
## Startup & Shutdown
##


@api.on_event("startup")
async def startup():
    api.manager = LightManager()
    api.manager.light_off()


@api.on_event("shutdown")
async def shutdown():
    api.manager.light_off()


##
## Exception Handlers
##


@api.exception_handler(LightIdRangeError)
async def light_id_range_error_handler(request: Request, error: LightIdRangeError):
    """Handle light_id that are out of bounds.
    """
    nlights = len(api.manager.lights)
    return JSONResponse(
        status_code=404,
        content={
            "message": f"Light {error.light_id} is out of range. Must be an integer between zero and {nlights-1}"
        },
    )


@api.exception_handler(ColorLookupError)
async def color_lookup_error_handler(request: Request, error: ColorLookupError):
    """Handle malformed color specifications.
    """
    return JSONResponse(status_code=404, content={"message": str(error)})


##
## API Routes
##


@api.get("/1/light/{light_id}", response_model=LightDescription)
async def Light_Description(
    light_id: int = Path(..., title="Light identifier", ge=0)
) -> dict:
    """Information about the light selected by `light_id`.
    """

    try:
        light = api.manager.lights[light_id]
        return {
            "light_id": light_id,
            "name": light.name,
            "info": light.info,
        }
    except IndexError:
        raise LightIdRangeError(light_id)


@api.get("/1/lights", response_model=List[LightDescription])
async def Lights_Description() -> dict:
    """Information about all available lights.
    """
    result = []
    for index, light in enumerate(api.manager.lights):
        result.append(
            {"light_id": index, "name": light.name, "info": light.info,}
        )
    return result


@api.get(
    "/1/light/{light_id}/on",
    response_model=LightOperation,
    response_model_exclude_unset=True,
)
async def Turn_On_Light(light_id: int = Path(..., title="Light identifier", ge=0)):
    """Turn on the specified light with the default color, green.
    """
    try:
        api.manager.light_on(light_id)
        return {"action": "on", "light": light_id, color: "green"}
    except IndexError:
        raise LightIdRangeError(light_id)


@api.get(
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
    string: red, #ff0000, #f00, 0xff0000, 0xf00
    """

    try:
        api.manager.light_on(light_id, color)
        return {"action": "on", "light_id": light_id, "color": color}
    except IndexError:
        raise LightIdRangeError(light_id)
    except ValueError:
        raise ColorLookupError(color)


@api.get(
    "/1/lights/on", response_model=LightOperation, response_model_exclude_unset=True,
)
async def Turn_On_Lights() -> dict:
    """Turn on all lights with the default color, green.
    """
    try:
        api.manager.light_on(-1)
        return {"action": "on", "light_id": "all", "color": "green"}
    except IndexError:
        raise LightIdRangeError(light_id)


@api.get(
    "/1/lights/on/{color}",
    response_model=LightOperation,
    response_model_exclude_unset=True,
)
async def Turn_On_Lights_With_Color(
    color: str = Path(..., title="Color specifier string")
) -> dict:
    """Turn on all lights with the given `color`.

    The `color` can be a color name or a hexadecimal string: red,
    #ff0000, #f00, 0xff0000, 0xf00
    """
    try:
        api.manager.light_on(-1, color)
        return {"action": "on", "light_id": "all", "color": color}
    except IndexError:
        raise LightIdRangeError(light_id)
    except ValueError:
        raise ColorLookupError(color)


@api.get(
    "/1/light/{light_id}/off",
    response_model=LightOperation,
    response_model_exclude_unset=True,
)
async def Turn_Off_Light(
    light_id: int = Path(..., title="Light identifier", ge=0)
) -> dict:

    """Turn off the specified light.
    """
    try:
        api.manager.light_off(light_id)
        return {"action": "off", "light_id": light_id}
    except IndexError:
        raise LightIdRangeError(light_id)


@api.get(
    "/1/lights/off", response_model=LightOperation, response_model_exclude_unset=True,
)
async def Turn_Off_Lights() -> dict:
    """Turn off all lights.
    """
    try:
        api.manager.light_off(-1)
        return {"action": "off", "light_id": "all"}
    except IndexError:
        raise LightIdRangeError(light_id)


@api.get(
    "/1/light/{light_id}/blink",
    response_model=LightOperation,
    response_model_exclude_unset=True,
)
async def Blink_Light(
    light_id: int = Path(..., title="Light identifier", ge=0)
) -> dict:
    """Start blinking the specified light: red and off.
    """
    try:
        api.manager.light_blink(light_id)
        return {
            "action": "blink",
            "light_id": light_id,
            "color": "red",
            "speed": BlinkSpeed.SLOW,
        }
    except IndexError:
        raise LightIdRangeError(light_id)


@api.get(
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
    #ff0000, #f00, 0xff0000, 0xf00
    """
    try:
        api.manager.light_blink(light_id, color)
        return {
            "action": "blink",
            "light_id": light_id,
            "color": color,
            "speed": BlinkSpeed.SLOW,
        }
    except IndexError:
        raise LightIdRangeError(light_id)
    except ValueError:
        raise ColorLookupError(color)


@api.get(
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
    #ff0000, #f00, 0xff0000, 0xf00
    """
    try:
        api.manager.light_blink(light_id, color, speed)
        return {"action": "blink", "light_id": light_id, "color": color, "speed": speed}
    except IndexError:
        raise HTTPException(
            status_code=404, detail=f"Light {light_id} not found."
        ) from None
    except ValueError:
        raise HTTPException(
            status_code=404, detail=f"Color {color} not found."
        ) from None


@api.get(
    "/1/lights/blink", response_model=LightOperation, response_model_exclude_unset=True,
)
async def Blink_Lights() -> dict:
    """Start blinking all the lights: red and off
    <p>Note: lights will not be synchronized.</p>
    """
    try:
        api.manager.light_blink(-1)
        return {"action": "blink", "light_id": "all", "color": "red", "speed": "slow"}
    except IndexError:
        raise HTTPException(status_code=404, detail="No lights found.") from None


@api.get(
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
    string: red, #ff0000, #f00, 0xff0000, 0xf00 </p>
    <p><em>Note:</em> Lights will not be synchronized.</p>
    """
    try:
        api.manager.light_blink(-1, color)
        return {
            "action": "blink",
            "light_id": light_id,
            "color": color,
            "speed": "slow",
        }
    except IndexError:
        raise HTTPException(status_code=404, detail="No lights found.") from None
    except ValueError:
        raise HTTPException(
            status_code=404, detail=f"Color {color} not found."
        ) from None


@api.get(
    "/1/lights/blink/{color}/{speed}",
    response_model=LightOperation,
    response_model_exclude_unset=True,
)
async def Blink_Lights_With_Color_and_Speed(
    color: str = Path(..., title="Color specifier string"),
    speed: BlinkSpeed = Path(..., title="Speed: slow, medium, fast"),
) -> dict:
    """Start blinking all the lights: `color` and off with the specified speed.
  
    The `color` can be a color name or a hexadecimal string: red, #ff0000, #f00, 0xff0000, 0xf00 </p>

    <p><em>Note:</em> Lights will not be synchronized.</p>
    """
    try:
        api.manager.light_blink(-1, color, speed)
        return {"action": "blink", "light_id": "all", "color": color, "speed": speed}
    except IndexError:
        raise HTTPException(status_code=404, detail="No lights found.") from None
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from None


@api.get(
    "/1/light/{light_id}/rainbow",
    response_model=LightOperation,
    response_model_exclude_unset=True,
)
async def Rainbow_Light(
    light_id: int = Path(..., title="Light identifier", ge=0)
) -> dict:
    """Start a rainbow animation on the specified light.
    """
    try:
        api.manager.apply_effect_to_light(light_id, rainbow)
        return {"action": "effect", "name": "rainbow", "light_id": light_id}
    except IndexError:
        raise HTTPException(
            status_code=404, detail=f"Light {light_id} not found."
        ) from None


@api.get(
    "/1/lights/rainbow",
    response_model=LightOperation,
    response_model_exclude_unset=True,
)
async def Rainbow_Lights():
    """Start a rainbow animation on all lights.
    <p><em>Note:</em> lights will not be synchronized.</p>
    """
    try:
        api.manager.apply_effect_to_light(-1, rainbow)
        return {"action": "effect", "name": "rainbow", "light_id": "all"}
    except IndexError:
        raise HTTPException(status_code=404, detail=f"No lights found.") from None
