""" Busylight for Humans™ Web API Testing
"""

import os

import pytest

from busylight.api import busylightapi
from busylight.api import EndPoint
from busylight.api import LightDescription
from busylight.api import LightOperation

from httpx import AsyncClient

# EJO tests marked 'xfail' are expected to fail in situations where no
#     physical lights are attached. We get Xsuccesses when lights are
#     available.


@pytest.fixture(scope="module")
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture(scope="module")
async def client(anyio_backend) -> AsyncClient:
    async with AsyncClient(app=busylightapi, base_url="http://test") as client:
        yield client
        await client.get("/lights/off")


@pytest.mark.anyio
async def test_webapi_root(client) -> None:

    response = await client.get("/")

    assert response.status_code == 200

    content = response.json()

    assert isinstance(content, list)

    for item in content:
        assert isinstance(item, dict)
        endpoint = EndPoint(**item)
        assert endpoint.path


@pytest.mark.anyio
@pytest.mark.parametrize("route", ["/lights", "/lights/status"])
async def test_webapi_lights_status(route, client) -> None:

    response = await client.get(route)

    assert response.status_code == 200

    content = response.json()

    assert isinstance(content, list)

    for item in content:
        assert isinstance(item, dict)
        desc = LightDescription(**item)


@pytest.mark.xfail
@pytest.mark.anyio
@pytest.mark.parametrize("route", ["/light/0", "/light/0/status"])
async def test_webapi_lights_status(route, client) -> None:

    response = await client.get(route)

    assert response.status_code == 200

    content = response.json()

    assert isinstance(content, dict)

    operation = LightDescription(**content)


@pytest.mark.anyio
@pytest.mark.parametrize(
    "route",
    [
        "lights/on",
        "lights/off",
        "lights/blink",
        "lights/fli",
        "lights/pulse",
        "lights/rainbow",
    ],
)
async def test_webapi_lights_simple_operation(route, client) -> None:

    response = await client.get(route)

    assert response.status_code == 200

    content = response.json()

    assert isinstance(content, dict)

    operation = LightOperation(**content)


@pytest.mark.xfail
@pytest.mark.anyio
@pytest.mark.parametrize(
    "route",
    [
        "light/0/on",
        "light/0/off",
        "light/0/blink",
        "light/0/fli",
        "light/0/pulse",
        "light/0/rainbow",
    ],
)
async def test_webapi_light_simple_operation(route, client) -> None:

    response = await client.get(route)

    assert response.status_code == 200

    content = response.json()

    assert isinstance(content, dict)

    operation = LightOperation(**content)


async def test_webapi_authentication(client) -> None:
    os.environ["BUSYLIGHT_API_USER"] = "test_user"
    os.environ["BUSYLIGHT_API_PASS"] = "test_pass"
    async with AsyncClient(app=busylightapi, base_url="http://test") as client:
        response = await client.get("/")
        assert response.status_code == 200
        # os.environ["BUSYLIGHT_API_USER"] = "bad_user"
        # os.environ["BUSYLIGHT_API_PASS"] = "bad_pass"
        # response = await client.get("/")
        # assert response.status_code != 200
