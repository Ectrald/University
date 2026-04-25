"""Построение семейств графиков коэффициента ускорения S и эффективности E
для арифметического конвейера.

Формулы (сбалансированный r-этапный конвейер с временем счёта t_i = const):
    T_1 = n * r * t_i               – последовательное выполнение
    T_k = (r + n - 1) * t_i         – конвейерное выполнение
    S   = T_1 / T_k = (n * r) / (r + n - 1)
    E   = S / r      = n / (r + n - 1)
"""

from __future__ import annotations

import os
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


OUT_DIR = Path(__file__).resolve().parent.parent / "report"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def speedup(n: int, r: int) -> float:
    return (n * r) / (r + n - 1)


def efficiency(n: int, r: int) -> float:
    return n / (r + n - 1)


# ------------------------------------------------------------------ S(n), E(n)
def plot_family_fix_r():
    n_values = list(range(1, 51))
    r_values = [2, 4, 8, 16]

    # Ускорение
    plt.figure(figsize=(8.5, 5.0))
    for r in r_values:
        plt.plot(n_values, [speedup(n, r) for n in n_values], marker="o", markersize=3, label=f"r = {r}")
    plt.axhline(y=max(r_values), color="gray", linestyle=":", linewidth=0.8)
    plt.xlabel("n — число обрабатываемых пар")
    plt.ylabel("S — коэффициент ускорения")
    plt.title("Зависимость S от n при фиксированных r", fontsize=12)
    plt.grid(True, alpha=0.4)
    plt.legend()
    plt.tight_layout()
    plt.savefig(OUT_DIR / "speedup_vs_n.png", dpi=160)
    plt.close()

    # Эффективность
    plt.figure(figsize=(8.5, 5.0))
    for r in r_values:
        plt.plot(n_values, [efficiency(n, r) for n in n_values], marker="s", markersize=3, label=f"r = {r}")
    plt.axhline(y=1.0, color="gray", linestyle=":", linewidth=0.8)
    plt.xlabel("n — число обрабатываемых пар")
    plt.ylabel("E — коэффициент эффективности")
    plt.title("Зависимость E от n при фиксированных r", fontsize=12)
    plt.grid(True, alpha=0.4)
    plt.legend()
    plt.tight_layout()
    plt.savefig(OUT_DIR / "efficiency_vs_n.png", dpi=160)
    plt.close()


# ------------------------------------------------------------------ S(r), E(r)
def plot_family_fix_n():
    r_values = list(range(2, 33))
    n_values = [4, 10, 25, 100]

    plt.figure(figsize=(8.5, 5.0))
    for n in n_values:
        plt.plot(r_values, [speedup(n, r) for r in r_values], marker="o", markersize=3, label=f"n = {n}")
    plt.xlabel("r — число разрядов (этапов конвейера)")
    plt.ylabel("S — коэффициент ускорения")
    plt.title("Зависимость S от r при фиксированных n", fontsize=12)
    plt.grid(True, alpha=0.4)
    plt.legend()
    plt.tight_layout()
    plt.savefig(OUT_DIR / "speedup_vs_r.png", dpi=160)
    plt.close()

    plt.figure(figsize=(8.5, 5.0))
    for n in n_values:
        plt.plot(r_values, [efficiency(n, r) for r in r_values], marker="s", markersize=3, label=f"n = {n}")
    plt.xlabel("r — число разрядов (этапов конвейера)")
    plt.ylabel("E — коэффициент эффективности")
    plt.title("Зависимость E от r при фиксированных n", fontsize=12)
    plt.grid(True, alpha=0.4)
    plt.legend()
    plt.tight_layout()
    plt.savefig(OUT_DIR / "efficiency_vs_r.png", dpi=160)
    plt.close()


def main():
    plot_family_fix_r()
    plot_family_fix_n()
    print("Графики сохранены в", OUT_DIR)


if __name__ == "__main__":
    main()
