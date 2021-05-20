"""
"""

from typing import Dict, Union

import pytest


@pytest.fixture(scope="session")
def route_variables() -> Dict[str, Union[int, str]]:
    return {
        "light_id": 0,
        "color": "purple",
        "speed": "fast",
    }


def test_route_root(busylight_client) -> None:

    with busylight_client as client:
        response = client.get("/")

    assert response.status_code == 200

    routes = response.json()

    assert isinstance(routes, list)

    for route in routes:
        assert isinstance(route, dict)
        assert "path" in route.keys()
        assert all(isinstance(value, str) for value in route.values())


@pytest.mark.parametrize(
    "route, expected_status_codes",
    [
        ["/light/{light_id}/status", [404]],
        ["/lights/status", [200]],
        ["/light/{light_id}/on", [404]],
        ["/light/{light_id}/on/{color}", [404]],
        ["/lights/on", [200]],
        ["/lights/on/{color}", [200]],
        ["/light/{light_id}/off", [200, 404]],
        ["/lights/off", [200]],
        ["/light/{light_id}/blink", [200, 404]],
        ["/light/{light_id}/blink/{color}", [200, 404]],
        ["/light/{light_id}/blink/{color}/{speed}", [200, 404]],
        ["/lights/blink", [200]],
        ["/lights/blink/{color}", [200]],
        ["/lights/blink/{color}/{speed}", [200]],
        ["/light/{light_id}/rainbow", [200, 404]],
        ["/lights/rainbow", [200]],
        ["/light/{light_id}/fli", [200, 404]],
        ["/lights/fli", [200]],
        ["/light/{light_id}/pulse", [200, 404]],
        ["/light/{light_id}/pulse/{color}", [200, 404]],
        ["/lights/pulse", [200]],
        ["/lights/pulse/{color}", [200]],
    ],
)
def test_all_routes(
    route,
    expected_status_codes,
    busylight_client,
    route_variables,
) -> None:

    with busylight_client as client:
        response = client.get(route.format_map(route_variables))
        assert response.status_code in expected_status_codes


@pytest.mark.parametrize(
    "color, expected_status_code",
    [
        ("red", 200),
        ("#ff0000", 200),
        ("#f00", 200),
        ("0xff0000", 200),
        ("0xf00", 200),
        ("reddish", 404),
    ],
)
def test_route_lights_on_color_validation(
    color,
    expected_status_code,
    busylight_client,
) -> None:

    with busylight_client as client:
        for value in [color.lower(), color.upper(), color.title()]:
            response = client.get(f"/lights/on/{value}")
            assert response.status_code == expected_status_code


@pytest.mark.parametrize(
    "speed, expected_status_code",
    [
        ("slow", 200),
        ("medium", 200),
        ("fast", 200),
        ("slowish", 422),
    ],
)
def test_route_lights_blink_speed_validataion(
    speed, expected_status_code, busylight_client
) -> None:

    with busylight_client as client:
        response = client.get(f"/lights/blink/orange/{speed}")
        assert response.status_code == expected_status_code
