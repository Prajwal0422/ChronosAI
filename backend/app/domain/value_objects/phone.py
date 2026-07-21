import re


class Phone:
    _pattern = re.compile(r"^\+?[1-9]\d{6,14}$")

    def __init__(self, value: str):
        value = value.strip()
        if not self._pattern.match(value):
            raise ValueError(f"Invalid phone number format: {value}")
        self._value = value

    @property
    def value(self) -> str:
        return self._value

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Phone):
            return NotImplemented
        return self._value == other._value

    def __hash__(self) -> int:
        return hash(self._value)

    def __str__(self) -> str:
        return self._value
