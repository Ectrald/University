"""Построение HTML-отчёта о работе конвейера (аналогично варианту коллеги,
адаптировано под умножение с младших разрядов со сдвигом множимого влево)."""

from __future__ import annotations

from typing import List

from binary_number import BinaryNumber
from pipeline import ArithmeticPipeline, MultiplicationTriple


def _fmt(num: BinaryNumber) -> str:
    return f"{num.to_binary_string()} ({num.to_int()})"


def build_html_report(
    pipeline: ArithmeticPipeline,
    inputs: List[MultiplicationTriple],
    stage_time: int,
) -> str:
    ticks = len(pipeline.history)
    stages = len(pipeline.stages)

    css = """
    <style>
      body  { font-family: "Cascadia Code", "Consolas", monospace; font-size: 14px; }
      h2    { font-family: Arial, sans-serif; }
      table { border-collapse: collapse; margin-bottom: 24px; }
      th,td { border: 1px solid #444; padding: 6px 8px; vertical-align: top; }
      th    { background: #eef; }
      .empty{ background: #f7f7f7; color: #999; text-align: center; }
      .in   { background: #fefaf0; }
      .out  { background: #f0faff; }
    </style>
    """

    out = ["<html><head><meta charset='utf-8'>", css, "</head><body>"]
    out.append("<h2>Исходные пары (не менее трёх)</h2>")
    out.append("<table><tr><th>i</th><th>A (множимое)</th><th>B (множитель)</th></tr>")
    for t in inputs:
        out.append(
            f"<tr><td>{t.index}</td>"
            f"<td>{t.multiplicand.to_int()} = {t.multiplicand.to_binary_string()}</td>"
            f"<td>{t.factor.to_int()} = {t.factor.to_binary_string()}</td></tr>"
        )
    out.append("</table>")

    out.append("<h2>Пошаговая работа конвейера</h2>")
    out.append("<table><tr><th>Этап \\ Такт</th>")
    for k in range(ticks):
        time_u = pipeline.time_history[k]
        out.append(f"<th>Такт {k + 1}<br>t = {time_u} у.в.е.</th>")
    out.append("</tr>")

    for s in range(stages):
        out.append(f"<tr><td><b>Этап {s + 1}</b></td>")
        for k in range(ticks):
            triple = pipeline.history[k][s]
            if triple is None:
                out.append("<td class='empty'>—</td>")
            else:
                out.append(
                    "<td class='out'>"
                    f"<small>i = {triple.index}</small><br>"
                    f"M&nbsp;=&nbsp;{_fmt(triple.multiplicand)}<br>"
                    f"F&nbsp;=&nbsp;{_fmt(triple.factor)}<br>"
                    f"PS=&nbsp;{_fmt(triple.partial_sum)}"
                    "</td>"
                )
        out.append("</tr>")
    out.append("</table>")

    out.append("<h2>Результирующий вектор C (не менее трёх элементов)</h2>")
    out.append("<table><tr><th>i</th><th>C = A·B (двоичное)</th><th>C (десятичное)</th><th>t, у.в.е.</th></tr>")
    for idx, tr, t in pipeline.results:
        out.append(
            f"<tr><td>{idx}</td>"
            f"<td>{tr.partial_sum.to_binary_string()}</td>"
            f"<td>{tr.partial_sum.to_int()}</td>"
            f"<td>{t}</td></tr>"
        )
    out.append("</table>")

    out.append(f"<p>Время счёта на этапе: t<sub>i</sub> = {stage_time} у.в.е.</p>")
    out.append("</body></html>")
    return "\n".join(out)
