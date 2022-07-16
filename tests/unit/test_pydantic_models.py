"""
"""

import pytest

from busylight.api.models import EndPoint, LightDescription, LightOperation

from pydantic import ValidationError


@pytest.mark.parametrize(
    "path,expected_exception",
    [
        ("foo", None),
        (1, None),
        (3.145, None),
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
    "light_id,name,hidinfo,is_on,color,rgb",
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
def test_model_lightdescription(light_id, name, hidinfo, is_on, color, rgb) -> None:
    light_description = LightDescription(
        light_id=light_id, name=name, hidinfo=hidinfo, is_on=is_on, color=color, rgb=rgb
    )

    assert light_description.light_id == light_id
    assert light_description.name == name
    assert isinstance(light_description.hidinfo, dict)
    for key, value in hidinfo.items():
        assert light_description.hidinfo[key] == value
    assert light_description.is_on == is_on
    assert light_description.color == color
    assert light_description.rgb == rgb


@pytest.mark.parametrize(
    "light_id,action,color,rgb,speed,name,dim",
    [
        (0, "on", "green", (0, 0x80, 0), "insane", "foo", False),
    ],
)
def test_model_lightoperation(light_id, action, color, rgb, speed, name, dim) -> None:
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
