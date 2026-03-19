"""
//////////////////
Лабораторная работа No1 по дисциплине МРЗвИС
Выполнена студентом группы 321701 БГУИР Германенко Владислав Вадимович
Файл: Построение графиков характеристик (Ky, Эффективность)
!! 18.03.2026
[Основано на лекционном материале, используются встроенные библиотеки Python и matplotlib для графиков]
//////////////////
"""
import random
import matplotlib.pyplot as plt
from core.pipeline import Simulation

def run_full_simulation(p, queue, times):
    sim = Simulation(p, queue, times)
    while sim.queue or any(s.current_pair for s in sim.stages):
        sim.next_tact()
    sim.calculate_metrics()
    return sim

def plot_metrics(p, times, max_m=20):
    ms = list(range(1, max_m + 1))
    kys = []
    effs = []
    
    for m in ms:
        queue = [{'id': i + 1, 'a': random.randint(1, 2 ** p - 1), 'b': random.randint(1, 2 ** p - 1)} for i in range(m)]
        sim = run_full_simulation(p, queue, times)
        kys.append(sim.ky)
        effs.append(sim.eff)
        
    plt.figure(figsize=(10, 8))
    plt.subplot(2, 1, 1)
    plt.plot(ms, kys, label='Коэффициент ускорения (Ky)', marker='o')
    plt.xlabel('Количество пар (m)')
    plt.ylabel('Ky')
    plt.title('Зависимость коэффициента ускорения от количества пар')
    plt.legend()
    plt.grid(True)

    plt.subplot(2, 1, 2)
    plt.plot(ms, effs, label='Эффективность (Eff)', marker='s', color='orange')
    plt.xlabel('Количество пар (m)')
    plt.ylabel('Eff')
    plt.title('Зависимость эффективности от количества пар')
    plt.legend()
    plt.grid(True)

    plt.tight_layout()
    plt.show()
