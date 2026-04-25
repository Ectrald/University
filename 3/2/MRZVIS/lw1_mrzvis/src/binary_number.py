"""
Лабораторная работа №1 по дисциплине
"Методы решения задач в интеллектуальных системах" (МРЗвИС).

Модуль: представление двоичных чисел фиксированной разрядности.

Вариант:
    алгоритм вычисления произведения пары 4-разрядных чисел
    умножением с младших разрядов со сдвигом множимого влево.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class BinaryNumber:
    """Двоичное число фиксированной разрядности.

    Биты хранятся в списке ``bits`` от старшего к младшему
    (bits[0] – старший, bits[-1] – младший).
    """

    width: int
    bits: List[bool]

    # --------------------------- Конструкторы --------------------------- #
    @classmethod
    def from_int(cls, width: int, value: int) -> "BinaryNumber":
        mask = (1 << width) - 1
        value &= mask
        bits = [(value >> (width - 1 - i)) & 1 == 1 for i in range(width)]
        return cls(width=width, bits=bits)

    @classmethod
    def from_str(cls, s: str) -> "BinaryNumber":
        s = s.replace(" ", "").replace(".", "").replace("-", "")
        if any(c not in "01" for c in s):
            raise ValueError("Входные числа должны быть двоичными")
        return cls(width=len(s), bits=[c == "1" for c in s])

    # ---------------------------- Операции ------------------------------ #
    def to_int(self) -> int:
        value = 0
        for b in self.bits:
            value = (value << 1) | (1 if b else 0)
        return value

    def bit_lsb(self, i: int) -> bool:
        """Получить i-й бит, считая от младшего (LSB = 0)."""
        return self.bits[self.width - 1 - i]

    def shl(self, places: int = 1) -> "BinaryNumber":
        new_bits = self.bits[places:] + [False] * places
        # ограничим разрядностью
        new_bits = new_bits[: self.width]
        return BinaryNumber(width=self.width, bits=new_bits)

    def shr(self, places: int = 1) -> "BinaryNumber":
        new_bits = [False] * places + self.bits[:-places] if places > 0 else list(self.bits)
        new_bits = new_bits[: self.width]
        return BinaryNumber(width=self.width, bits=new_bits)

    def __add__(self, other: "BinaryNumber") -> "BinaryNumber":
        width = max(self.width, other.width)
        a = BinaryNumber.from_int(width, self.to_int())
        b = BinaryNumber.from_int(width, other.to_int())
        result = [False] * width
        carry = False
        for i in range(width):
            bit_a = a.bit_lsb(i)
            bit_b = b.bit_lsb(i)
            s = bit_a ^ bit_b ^ carry
            carry = (bit_a and bit_b) or (bit_a and carry) or (bit_b and carry)
            result[width - 1 - i] = s
        return BinaryNumber(width=width, bits=result)

    # ----------------------------- Вывод -------------------------------- #
    def to_binary_string(self, group: int = 4, sep: str = " ") -> str:
        raw = "".join("1" if b else "0" for b in self.bits)
        # группируем с конца
        rev = raw[::-1]
        chunks = [rev[i : i + group][::-1] for i in range(0, len(rev), group)]
        return sep.join(reversed(chunks))

    def __repr__(self) -> str:  # pragma: no cover
        return f"BinaryNumber({self.width}, {self.to_binary_string()} = {self.to_int()})"
