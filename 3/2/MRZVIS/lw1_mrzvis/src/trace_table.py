"""Генерация текстовой трассы конвейера, удобной для вставки в LaTeX.
Печатает таблицу «Этап × Такт» с данными каждой тройки."""

from __future__ import annotations

import json

from binary_number import BinaryNumber
from pipeline import ArithmeticPipeline, MultiplicationTriple


def main():
    pairs = [(15, 15), (1, 7), (9, 11)]
    r = 4
    triples = [
        MultiplicationTriple(
            index=i + 1,
            multiplicand=BinaryNumber.from_int(2 * r, a),
            factor=BinaryNumber.from_int(r, b),
            partial_sum=BinaryNumber.from_int(2 * r, 0),
        )
        for i, (a, b) in enumerate(pairs)
    ]
    p = ArithmeticPipeline(n_stages=r, stage_time=1)
    p.run(list(triples))

    # печатаем в JSON — удобно читать
    data = {"ticks": p.tick, "r": r, "pairs": pairs, "history": []}
    for k, snap in enumerate(p.history):
        row = {"tick": k + 1, "time": p.time_history[k], "stages": []}
        for st_idx, triple in enumerate(snap):
            if triple is None:
                row["stages"].append(None)
            else:
                row["stages"].append(
                    {
                        "i": triple.index,
                        "M": triple.multiplicand.to_binary_string(),
                        "Mv": triple.multiplicand.to_int(),
                        "F": triple.factor.to_binary_string(),
                        "Fv": triple.factor.to_int(),
                        "PS": triple.partial_sum.to_binary_string(),
                        "PSv": triple.partial_sum.to_int(),
                    }
                )
        data["history"].append(row)
    data["results"] = [
        {"i": i, "C": tr.partial_sum.to_binary_string(), "Cv": tr.partial_sum.to_int(), "t": t}
        for (i, tr, t) in p.results
    ]
    print(json.dumps(data, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
