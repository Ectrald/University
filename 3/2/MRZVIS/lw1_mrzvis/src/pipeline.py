"""
Лабораторная работа №1 по дисциплине
"Методы решения задач в интеллектуальных системах" (МРЗвИС).

Модуль: арифметический сбалансированный конвейер.

Вариант:
    алгоритм вычисления произведения пары 4-разрядных чисел
    умножением с младших разрядов со сдвигом множимого влево.

На каждом из r (=4) этапов конвейера выполняется один шаг алгоритма:
    if factor.lsb:  partial_sum += multiplicand
    multiplicand <<= 1
    factor     >>= 1
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import List, Optional

from binary_number import BinaryNumber


# --------------------------------------------------------------------------- #
#                       Триплет данных, курсирующий по конвейеру               #
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class MultiplicationTriple:
    index: int                 # индекс исходной пары
    multiplicand: BinaryNumber # M (8-разрядное хранилище, т. к. сдвигается влево)
    factor: BinaryNumber       # F (4-разрядное) – сдвигается вправо
    partial_sum: BinaryNumber  # PS (8-разрядное)


# --------------------------------------------------------------------------- #
#                                 Этап конвейера                               #
# --------------------------------------------------------------------------- #
@dataclass
class PipelineStage:
    """Один этап сбалансированного конвейера.

    ``content`` – текущая обрабатываемая тройка данных
    (либо None, если этап свободен).
    """

    stage_time: int = 1                        # длительность счёта на этапе t_i
    content: Optional[MultiplicationTriple] = None
    input_snapshot: Optional[MultiplicationTriple] = None
    output_snapshot: Optional[MultiplicationTriple] = None

    def do_work(self) -> None:
        if self.content is None:
            self.output_snapshot = None
            return
        t = self.content
        # шаг алгоритма «с младших разрядов, сдвиг множимого влево»
        if t.factor.bit_lsb(0):
            new_ps = t.partial_sum + t.multiplicand
        else:
            new_ps = t.partial_sum
        new_m = t.multiplicand.shl(1)
        new_f = t.factor.shr(1)
        out = MultiplicationTriple(
            index=t.index,
            multiplicand=new_m,
            factor=new_f,
            partial_sum=new_ps,
        )
        self.content = out
        self.output_snapshot = out


# --------------------------------------------------------------------------- #
#                            Арифметический конвейер                           #
# --------------------------------------------------------------------------- #
@dataclass
class ArithmeticPipeline:
    n_stages: int                              # r – число разрядов множителя = число этапов
    stage_time: int = 1                        # t_i – время счёта на этапе (в тактах)
    stages: List[PipelineStage] = field(default_factory=list)

    tick: int = 0
    history: List[List[Optional[MultiplicationTriple]]] = field(default_factory=list)
    time_history: List[int] = field(default_factory=list)
    results: List[tuple] = field(default_factory=list)  # (index, result, time)

    def __post_init__(self) -> None:
        self.stages = [PipelineStage(stage_time=self.stage_time) for _ in range(self.n_stages)]

    # ---------------------------------------------------------------- run --- #
    def run(self, inputs: List[MultiplicationTriple]) -> List[MultiplicationTriple]:
        """Прогоняет все входные тройки через конвейер."""
        queue = list(inputs)
        total_needed = len(queue)
        output: List[MultiplicationTriple] = []

        # выполняем такты пока не получим все результаты
        while len(output) < total_needed:
            self._do_tick(queue, output)

        return output

    # -------------------------------------------------------------- _tick --- #
    def _do_tick(
        self,
        queue: List[MultiplicationTriple],
        output: List[MultiplicationTriple],
    ) -> None:
        self.tick += 1

        # 1) сдвиг содержимого по этапам вперёд
        for i in range(len(self.stages) - 1, 0, -1):
            self.stages[i].content = self.stages[i - 1].content
        self.stages[0].content = None

        # 2) загрузка новой пары в первый этап
        if queue:
            self.stages[0].content = queue.pop(0)

        # 3) входные снимки
        for st in self.stages:
            st.input_snapshot = st.content

        # 4) обработка
        for st in self.stages:
            st.do_work()

        # 5) сохраняем историю (после обработки – выходы этапов)
        snap = [st.output_snapshot for st in self.stages]
        self.history.append(snap)
        # учтём длительность этапа (t_i) в общем времени
        cur_time = self.tick * self.stage_time
        self.time_history.append(cur_time)

        # 6) выходной результат: тройка «упала» с последнего этапа
        last = self.stages[-1].content
        if last is not None:
            output.append(last)
            self.results.append((last.index, last, cur_time))
            # освобождаем последний этап
            self.stages[-1].content = None
