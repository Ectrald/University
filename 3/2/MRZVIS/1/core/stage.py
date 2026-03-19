"""
//////////////////
Лабораторная работа No1 по дисциплине МРЗвИС
Выполнена студентом группы 321701 БГУИР Германенко Владислав Вадимович
Файл: Класс этапа конвейера
!! 18.03.2026
[Основано на лекционном материале, алгоритм умножения с младших разрядов со сдвигом влево]
//////////////////
"""

class Stage:
    def __init__(self, stage_idx, cycles_required):
        self.idx = stage_idx
        self.cycles_required = cycles_required
        self.current_pair = None
        self.cycles_left = 0
        self.p_sum = 0
        self.p_prod = 0
