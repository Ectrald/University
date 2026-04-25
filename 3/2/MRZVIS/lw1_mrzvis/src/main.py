"""
Лабораторная работа №1. МРЗвИС. Вариант:
    алгоритм вычисления произведения пары 4-разрядных чисел
    умножением с младших разрядов со сдвигом множимого влево.

Запуск:
    python main.py [--input input.json] [--t 1] [--n 10] [--open]

Параметры:
    --input  путь к JSON-файлу с парами чисел (по умолчанию input.json)
    --t      время счёта на этапе (t_i), у.в.е. (условных временных единиц)
    --n      параметр n – число обрабатываемых пар (если больше длины файла,
             данные дополняются случайно)
    --r      разрядность чисел (по умолчанию 4)
    --open   открыть HTML-отчёт в браузере
"""

from __future__ import annotations

import argparse
import json
import os
import random
import sys
import webbrowser
from pathlib import Path

from binary_number import BinaryNumber
from pipeline import ArithmeticPipeline, MultiplicationTriple
from report_html import build_html_report


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="LW1 MRZvIS — 4-bit pipelined multiplier")
    p.add_argument("--input", default="input.json")
    p.add_argument("--t", type=int, default=1, help="время счёта на этапе (t_i)")
    p.add_argument("--n", type=int, default=10, help="число пар (параметр n)")
    p.add_argument("--r", type=int, default=4, help="разрядность множителя/множимого")
    p.add_argument("--open", action="store_true", help="открыть HTML-отчёт")
    p.add_argument("--out", default="report.html", help="путь к HTML-отчёту")
    return p.parse_args()


def _load_pairs(path: str, r: int, n: int):
    pairs = []
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as fh:
            pairs = json.load(fh)
    max_v = (1 << r) - 1
    # проверка разрядности
    for a, b in pairs:
        if a > max_v or b > max_v:
            raise SystemExit(f"Числа должны помещаться в {r} бит (макс. {max_v}).")
    # дополнение до n пар
    rnd = random.Random(42)
    while len(pairs) < n:
        pairs.append([rnd.randint(0, max_v), rnd.randint(0, max_v)])
    return pairs[:n]


def build_inputs(pairs, r: int):
    """Создаёт список троек данных для конвейера.
    M (множимое)  хранится в 2r битах (сдвигается влево),
    F (множитель) хранится в r битах,
    PS (частичная сумма) — 2r битов.
    """
    triples = []
    for i, (a, b) in enumerate(pairs):
        triples.append(
            MultiplicationTriple(
                index=i + 1,
                multiplicand=BinaryNumber.from_int(2 * r, a),
                factor=BinaryNumber.from_int(r, b),
                partial_sum=BinaryNumber.from_int(2 * r, 0),
            )
        )
    return triples


def main() -> None:
    args = _parse_args()

    pairs = _load_pairs(args.input, args.r, args.n)
    triples = build_inputs(pairs, args.r)

    pipeline = ArithmeticPipeline(n_stages=args.r, stage_time=args.t)
    pipeline.run(list(triples))

    # --- проверка корректности
    errors = 0
    for (idx, tr, _), (a, b) in zip(pipeline.results, pairs):
        if tr.partial_sum.to_int() != a * b:
            errors += 1
    print(
        f"Готово. Обработано пар: {len(pairs)}, тактов: {pipeline.tick}, "
        f"время: {pipeline.time_history[-1]} у.в.е., ошибок: {errors}."
    )

    html = build_html_report(pipeline, triples, args.t)
    out_path = Path(args.out).absolute()
    out_path.write_text(html, encoding="utf-8")
    print(f"HTML-отчёт: {out_path}")

    if args.open:
        webbrowser.open(out_path.as_uri())


if __name__ == "__main__":
    try:
        main()
    except Exception as e:  # noqa
        print(f"Ошибка: {e}", file=sys.stderr)
        raise
