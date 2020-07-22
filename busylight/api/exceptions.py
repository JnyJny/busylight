"""BusyLight API Exceptions

"""


class LightIdRangeError(Exception):
    def __init__(self, light_id: int):
        self.light_id = light_id


class ColorLookupError(Exception):
    def __init__(self, color: str):
        self.color = color

    def __str__(self):
        return f"Unable to decode color for string '{self.color}'"
