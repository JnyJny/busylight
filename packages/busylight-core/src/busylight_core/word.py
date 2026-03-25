"""Bitwise operations on a word of bits."""

import array


class Word:
    """Binary data structure for device state management with BitField support.

    Provides bit-level manipulation of binary data with named field access
    through BitField descriptors. Use this as a base class for device state
    objects that need to pack/unpack complex binary protocols into structured,
    named fields.
    """

    def __init__(self, value: int = 0, length: int = 8) -> None:
        """Create a Word instance for binary data manipulation.

        Initializes a binary word with the specified bit length and initial value.
        The length must be a multiple of 8 to align with byte boundaries. Use this
        to create state objects for devices that use binary communication protocols.


        :param value: Initial integer value to store in the word
        :param length: Total bit length, must be multiple of 8
        :raises ValueError: If length is not a positive multiple of 8
        """
        if length <= 0 or length % 8 != 0:
            msg = "length must be a multiple of 8"
            raise ValueError(msg)

        self.initial_value = value
        self.length = length
        self.bits = array.array("B", [(value >> n) & 1 for n in self.range])

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(value={self.hex})"

    def __str__(self) -> str:
        """Return a human-readable representation showing field breakdown."""
        # Start with basic info
        lines = [f"{self.__class__.__name__}(length={self.length}, value={self.hex})"]

        # Use introspection to find BitFields on this instance's class
        bitfields = []
        for attr_name in dir(self.__class__):
            attr = getattr(self.__class__, attr_name)
            if isinstance(attr, (BitField, ReadOnlyBitField)):
                bitfields.append((attr_name, attr.offset, attr.width))

        if bitfields:
            lines.append("Fields:")
            template = "  {n}: bits[{o}:{r}] = {v} {v:#08x}"
            # Sort by offset for logical display
            for name, offset, width in sorted(bitfields, key=lambda x: x[1]):
                value = self[slice(offset, offset + width)]
                lines.append(
                    template.format(
                        n=name,
                        o=offset,
                        w=width,
                        r=offset + width,
                        v=value,
                    )
                )

        return "\n".join(lines)

    @property
    def value(self) -> int:
        """Return the integer value of the word."""
        return sum([b << n for n, b in enumerate(self.bits)])

    @property
    def range(self) -> range:
        """Return the range of bit offsets for this word."""
        return range(self.length)

    @property
    def hex(self) -> str:
        """Return a string hexadecimal representation of the word."""
        return f"{self.value:#0{self.length // 4}x}"

    @property
    def bin(self) -> str:
        """Return a string binary representation of the word."""
        return "0b" + bin(self.value)[2:].zfill(self.length)

    def clear(self) -> None:
        """Clear all bits in the word."""
        self.bits = array.array("B", [0] * self.length)

    def __bytes__(self) -> bytes:
        return self.value.to_bytes(self.length // 8, byteorder="big")

    def __getitem__(self, key: int | slice) -> int:
        if isinstance(key, int):
            if key not in self.range:
                msg = f"Index out of range: {key}"
                raise IndexError(msg)
            return self.bits[key]
        return sum([b << n for n, b in enumerate(self.bits[key])])

    def __setitem__(self, key: int | slice, value: bool | int) -> None:
        if isinstance(key, int):
            if key not in self.range:
                msg = f"Index out of range: {key}"
                raise IndexError(msg)
            self.bits[key] = value & 1
            return
        length = len(self.bits[key])
        new_bits = array.array("B", [value >> n & 1 for n in range(length)])
        self.bits[key] = new_bits


class ReadOnlyBitField:
    """Descriptor for read-only named bit fields within Word instances.

    Creates a named field that provides read-only access to specific bit ranges
    within a Word. Use this for device state fields that should not be modified
    by user code, such as status indicators or hardware-controlled values.
    """

    def __init__(self, offset: int, width: int = 1) -> None:
        """Create a read-only bit field descriptor.

        Defines a named field that maps to specific bit positions within a Word.
        The field will be accessible as a regular attribute on Word instances
        but will raise AttributeError on assignment attempts.


        :param offset: Starting bit position within the word (0-based from LSB)
        :param width: Number of consecutive bits to include in the field
        """
        self.field = slice(offset, offset + width)
        self.offset = offset  # Store for introspection
        self.width = width  # Store for introspection

    def __get__(self, instance: Word, owner: type | None = None) -> int:
        if instance is None:
            return self
        return instance[self.field]

    def __set_name__(self, owner: type, name: str) -> None:
        self.name = name

    def __set__(self, instance: Word, value: int) -> None:
        msg = f"{self.name} attribute is read only"
        raise AttributeError(msg)


class BitField(ReadOnlyBitField):
    """Descriptor for mutable named bit fields within Word instances.

    Creates a named field that provides read/write access to specific bit ranges
    within a Word. Use this for device control fields that can be modified by
    user code, such as color values, effect settings, or device configuration.
    """

    def __set__(self, instance: Word, value: int) -> None:
        instance[self.field] = value
