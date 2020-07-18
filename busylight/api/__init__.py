"""BusyLight API
"""

import asyncio

from fastapi import FastAPI, BackgroundTasks

from ..effects import rainbow, throbber, flash_lights_impressively
from ..lights.manager import LightManager

app = FastAPI()

manager = LightManager()

manager.light_off()


@app.get("/supported")
async def Supported_Lights():
    """
    """
    return {"supported": manager.supported}


@app.get("/available")
async def Available_Lights():
    """
    """
    return manager.available


@app.get("/helpers")
async def Helper_Threads():
    """
    """
    helpers = {}
    for key, value in manager.helpers.items():
        helpers.setdefault(key, value.is_alive())

    return helpers


@app.get("/light/{light_id}/on")
async def Turn_On_Light(light_id: int):
    """
    """
    manager.light_on(light_id)


@app.get("/light/{light_id}/on/{color}")
async def Turn_On_Light_With_Color(light_id: int, color: str = "green"):
    """
    """
    manager.light_on(light_id, color)


@app.get("/lights/on")
async def Turn_On_Lights():
    """
    """
    manager.light_on(-1)


@app.get("/lights/on/{color}")
async def Turn_On_Lights_With_Color(color: str = "green") -> dict:
    """
    """
    manager.light_on(-1, color)


@app.get("/light/{light_id}/off")
async def Turn_Off_Light(light_id: int) -> dict:
    """
    """
    manager.light_off(light_id)


@app.get("/lights/off")
async def Turn_Off_Lights() -> dict:
    """
    """
    manager.light_off(-1)


@app.get("/light/{light_id}/blink")
async def Blink_Light(light_id: int) -> dict:
    """
    """
    manager.light_blink(light_id)


@app.get("/light/{light_id}/blink/{color}")
async def Blink_Light_With_Color(light_id: int, color: str = "red") -> dict:
    """
    """
    manager.blink_light(light_id, color)


@app.get("/light/{light_id}/blink/{color}/{speed}")
async def Blink_Light_With_Color_and_Speed(
    light_id: int, color: str = "red", speed: int = 1
) -> dict:
    """
    """
    manaber.light_blink(light_id, color, speed)


@app.get("/lights/blink")
async def Blink_Lights() -> dict:
    """
    """
    manager.light_blink(-1)


@app.get("/lights/blink/{color}")
async def Blink_Lights_With_Color(color: str = "red", speed: int = 1) -> dict:
    """
    """
    manager.light_blink(-1, color)


@app.get("/lights/blink/{color}/{speed}")
async def Blink_Lights_With_Color_and_Speed(color: str = "red", speed: int = 1) -> dict:
    """
    """
    manager.light_blink(-1, color, speed)


@app.get("/light/{light_id}/rainbow")
async def Rainbow_Light(light_id: int) -> dict:
    """
    """
    manager.apply_effect_to_light(light_id, rainbow)
