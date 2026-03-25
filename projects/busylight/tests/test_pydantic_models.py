""" """

from typing import Any, Dict, List, Tuple, Union

import pytest
from busylight.api.models import EndPoint, LightDescription, LightOperation
from pydantic import ValidationError


@pytest.mark.parametrize(
    "path,expected_exception",
    [
        ("foo", None),
        (1, ValidationError),
        (3.145, ValidationError),
        ({"foo": 1}, ValidationError),
        (None, ValidationError),
        ([], ValidationError),
        (set(), ValidationError),
        (tuple(), ValidationError),
    ],
)
def test_model_endpoint(path, expected_exception) -> None:
    if expected_exception:
        with pytest.raises(expected_exception):
            endpoint = EndPoint(path=path)
        return

    endpoint = EndPoint(path=path)
    assert endpoint.path == str(path)


@pytest.mark.parametrize(
    "light_id,name,info,is_on,color,rgb",
    [
        (
            0,
            "bogolight",
            {"foo": 1, "bar": "bar"},
            False,
            "black",
            (0, 0, 0),
        ),
    ],
)
def test_model_lightdescription(
    light_id: int,
    name: str,
    info: Dict[str, Any],
    is_on: bool,
    color: str,
    rgb: Tuple[int, int, int],
) -> None:
    light_description = LightDescription(
        light_id=light_id, name=name, info=info, is_on=is_on, color=color, rgb=rgb
    )

    assert light_description.light_id == light_id
    assert light_description.name == name
    assert isinstance(light_description.info, dict)
    for key, value in info.items():
        assert light_description.info[key] == value
    assert light_description.is_on == is_on
    assert light_description.color == color
    assert light_description.rgb == rgb


@pytest.mark.parametrize(
    "light_id,action,color,rgb,speed,name,dim",
    [
        (0, "on", "green", (0, 0x80, 0), "insane", "foo", False),
    ],
)
def test_model_lightoperation(
    light_id: int,
    action: str,
    color: str,
    rgb: Tuple[int, int, int],
    speed: str,
    name: str,
    dim: bool,
) -> None:
    light_operation = LightOperation(
        light_id=light_id,
        action=action,
        color=color,
        rgb=rgb,
        speed=speed,
        name=name,
        dim=dim,
    )

    assert light_operation.light_id == light_id
    assert light_operation.action == action
    assert light_operation.color == color
    assert light_operation.rgb == rgb
    assert light_operation.speed == speed
    assert light_operation.name == name
    assert light_operation.dim == dim
