"""BusyLight API
"""

import asyncio

from fastapi import FastAPI, Path

from ..effects import rainbow, throbber, flash_lights_impressively
from ..lights.manager import LightManager

api = FastAPI()


@api.on_event("startup")
async def startup():
    api.manager = LightManager()
    api.manager.light_off()


@api.on_event("shutdown")
async def shutdown():
    api.manager.light_off()


@api.get("/supported")
async def Supported_Lights():
    """List of supported lights (may not be currently connected).
    """
    return {"supported": api.manager.supported}


@api.get("/available")
async def Available_Lights():
    """List of lights currently connected. 
    """
    return api.manager.available


@api.get("/helpers")
async def Helper_Threads():
    """Debug: lists of helper threads and the light they are associated with.
    """

    return [light.name for light in api.manager.managed if light.helper_thread]


@api.get("/light/{light_id}/on")
async def Turn_On_Light(light_id: int = Path(..., title="Light identifier", ge=1)):
    """
    """
    api.manager.light_on(light_id)


@api.get("/light/{light_id}/on/{color}")
async def Turn_On_Light_With_Color(
    light_id: int = Path(..., title="Light identifier", ge=1),
    color: str = Path(..., title="Color specifier string"),
):
    """Turn on a specific light with the given color. 
    
    The color can be a color nam or a hexadecimal
    string. Hexadecimal strings can be prefixed with # or 0x
    and can be 3 or 6 digits long. 

    Example color usage that all result in light zero being
    activated with the color "red":

    /light/0/on/red 
    /light/0/on/0xff0000
    /light/0/on/#ff0000
    /light/0/on/#f00

    :param light_id: integer in the range [0..NLIGHTS-1]
    :param color: string
    """
    api.manager.light_on(light_id, color)


@api.get("/lights/on")
async def Turn_On_Lights():
    """Turn on all lights with the default color, green.
    """
    api.manager.light_on(-1)


@api.get("/lights/on/{color}")
async def Turn_On_Lights_With_Color(color: str = "green") -> dict:
    """
    """
    api.manager.light_on(-1, color)


@api.get("/light/{light_id}/off")
async def Turn_Off_Light(light_id: int) -> dict:
    """
    """
    api.manager.light_off(light_id)


@api.get("/lights/off")
async def Turn_Off_Lights() -> dict:
    """
    """
    api.manager.light_off(-1)


@api.get("/light/{light_id}/blink")
async def Blink_Light(light_id: int) -> dict:
    """
    """
    api.manager.light_blink(light_id)


@api.get("/light/{light_id}/blink/{color}")
async def Blink_Light_With_Color(light_id: int, color: str = "red") -> dict:
    """
    """
    api.manager.light_blink(light_id, color)


@api.get("/light/{light_id}/blink/{color}/{speed}")
async def Blink_Light_With_Color_and_Speed(
    light_id: int, color: str = "red", speed: int = 1
) -> dict:
    """
    """
    manaber.light_blink(light_id, color, speed)


@api.get("/lights/blink")
async def Blink_Lights() -> dict:
    """
    """
    api.manager.light_blink(-1)


@api.get("/lights/blink/{color}")
async def Blink_Lights_With_Color(color: str = "red", speed: int = 1) -> dict:
    """
    """
    api.manager.light_blink(-1, color)


@api.get("/lights/blink/{color}/{speed}")
async def Blink_Lights_With_Color_and_Speed(color: str = "red", speed: int = 1) -> dict:
    """
    """
    api.manager.light_blink(-1, color, speed)


@api.get("/light/{light_id}/rainbow")
async def Rainbow_Light(light_id: int) -> dict:
    """
    """
    api.manager.apply_effect_to_light(light_id, rainbow)


@api.get("/lights/rainbow")
async def Rainbow_Lights():
    """
    """
    api.manager.apply_effect_to_light(-1, rainbow)
