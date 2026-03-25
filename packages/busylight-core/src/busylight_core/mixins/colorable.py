"""Color manipulation mixin for Light classes."""


class ColorableMixin:
    """Mixin providing individual RGB color component access and manipulation.

    Extends Light classes with individual red, green, and blue properties
    alongside the standard color tuple property. Use this mixin when you need
    fine-grained control over individual color components or when building
    device state objects that store colors as separate fields.
    """

    red = property(
        lambda self: getattr(self, "_red", 0),
        lambda self, value: setattr(self, "_red", value),
        doc="Red color value.",
    )

    green = property(
        lambda self: getattr(self, "_green", 0),
        lambda self, value: setattr(self, "_green", value),
        doc="Green color value.",
    )

    blue = property(
        lambda self: getattr(self, "_blue", 0),
        lambda self, value: setattr(self, "_blue", value),
        doc="Blue color value.",
    )

    @property
    def color(self) -> tuple[int, int, int]:
        """Get the current RGB color as a tuple.

        Returns the combined RGB color values as a 3-tuple. Use this property
        to read the complete color state when you need all three components
        together, such as for device updates or color comparisons.


        :return: RGB color values as (red, green, blue) tuple with 0-255 range
        """
        return (self.red, self.green, self.blue)

    @color.setter
    def color(self, value: tuple[int, int, int]) -> None:
        """Set the RGB color from a tuple.

        Updates all three color components simultaneously from a single RGB tuple.
        Use this setter when you have a complete color value to apply, such as
        from user input, color calculations, or predefined color constants.


        :param value: RGB intensity values from 0-255 for each color component
        """
        self.red, self.green, self.blue = value
