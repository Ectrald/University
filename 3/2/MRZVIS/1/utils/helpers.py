"""
//////////////////
Лабораторная работа No1 по дисциплине МРЗвИС
Выполнена студентом группы 321701 БГУИР Германенко Владислав Вадимович
Файл: Вспомогательные функции (очистка консоли, форматирование двоичных чисел)
!! 18.03.2026
[Основано на лекционном материале, используются встроенные библиотеки Python OS и Math]
//////////////////
"""
import os
import math

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

def format_bin(value, bits_needed):
    """
    Форматирует число в двоичном виде группами по 4 бита,
    разделенными пробелом, согласно ТЗ.
    """
    total_len = math.ceil(bits_needed / 4) * 4
    if total_len == 0: total_len = 4
    s = format(value & ((1 << total_len) - 1), f'0{total_len}b')
    return " ".join(s[i:i + 4] for i in range(0, len(s), 4))
