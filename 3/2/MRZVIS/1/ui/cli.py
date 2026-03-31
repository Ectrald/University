"""
//////////////////
Лабораторная работа No1 по дисциплине МРЗвИС
Выполнена студентом группы 321701 БГУИР Германенко Владислав Вадимович
Файл: Консольный пользовательский интерфейс (CLI)
!! 18.03.2026
[Основано на лекционном материале, алгоритм умножения с младших разрядов со сдвигом влево]
//////////////////
"""
import sys
import random
from utils.helpers import clear_console, format_bin
from ui.metrics import plot_metrics
from core.pipeline import Simulation

class CLI:
    def __init__(self):
        self.n = 0
        self.p = 0
        self.m = 0
        self.times = []
        self.queue = []
        self.sim = None

    def display_simulation(self):
        clear_console()
        print("\033[96m" + "=" * 60 + "\033[0m")
        print("\033[1;93mПример работы арифметического конвейера\033[0m")
        print("\033[96m" + "=" * 60 + "\033[0m")
        print(f"\033[1;92mТекущий такт:\033[0m {self.sim.tact}")
        
        print("\n\033[1;94m[ Входная очередь ]\033[0m")
        if not self.sim.queue:
            print("  (пусто)")
        else:
            for p_item in self.sim.queue[:3]:
                print(f"  Пара #{p_item['id']}: A {p_item['a']}={format_bin(p_item['a'], self.sim.p)} | B {p_item['b']}={format_bin(p_item['b'], self.sim.p)}")
            if len(self.sim.queue) > 3:
                print(f"  ... и еще {len(self.sim.queue) - 3} пар(-ы)")

        print("\n\033[96m" + "-" * 60 + "\033[0m")
        for i, s in enumerate(self.sim.stages):
            print(f"\033[1;95mЭтап {i + 1}\033[0m")
            if s.current_pair:
                print(f"  Номер пары: #{s.current_pair['id']}")
                bits_per_stage = (self.sim.p + self.sim.n - 1) // self.sim.n
                start_bit = s.current_bit_idx - (bits_per_stage if s.current_bit_idx > 0 else 0)
                end_bit = s.current_bit_idx
                print(f"  Обработано бит: {start_bit}-{end_bit} из {self.sim.p}")
                print(f"  Частичная сумма:        \033[92m{format_bin(s.partial_result, 2 * self.sim.p)}\033[0m")
            else:
                print("  Номер пары: (ожидание)")
                print("  Обработано бит: -")
                print("  Частичная сумма:        -")
            print("\033[90m" + "." * 60 + "\033[0m")
            
        print("\n\033[1;94m[ Результат (выход) ]\033[0m")
        if not self.sim.results:
            print("  (пусто)")
        else:
            # ТЗ пункт 5: после последнего этапа отображаются элементы (не менее 3-х).
            for res in self.sim.results[-3:]:
                print(f"  Пара #{res['id']}: C = {res['result']} (\033[92m{format_bin(res['result'], 2 * self.sim.p)}\033[0m), завершено на такте {res['completed_tact']}")
            if len(self.sim.results) > 3:
                print(f"  (всего готово: {len(self.sim.results)})")
        
        print("\n\033[1m1)\033[0m Дальше   \033[1m2)\033[0m Назад   \033[1m3)\033[0m Завершить до конца и выйти")

    def run(self):
        try:
            print("\033[1;96mНастройка модели арифметического конвейера\033[0m")
            self.p = int(input("Введите разрядность p (количество бит): "))
            self.n = int(input("Введите количество этапов n конвейера: "))
            self.m = int(input("Введите количество пар m (например, 5): "))
            
            self.times = []
            print("Настройка времени выполнения (в тактах) для каждого этапа:")
            for i in range(self.n):
                t = int(input(f"  Время для этапа {i + 1}: "))
                self.times.append(t)
        except ValueError:
            print("\033[91mОшибка ввода: Ожидается целое число.\033[0m")
            sys.exit(1)

        input_mode = input("Ввод чисел: (r) случайные или (m) ручной ввод? (r/m): ").strip().lower()
        if input_mode == 'm':
            for i in range(self.m):
                try:
                    a = int(input(f"  Введите A для пары #{i + 1}: "))
                    b = int(input(f"  Введите B для пары #{i + 1}: "))
                    self.queue.append({'id': i + 1, 'a': a, 'b': b})
                except ValueError:
                    print("\033[91mОшибка ввода: Ожидается целое число.\033[0m")
                    sys.exit(1)
        elif input_mode in ('r', ''):
            # random positive integers of bit depth p
            self.queue = [{'id': i + 1, 'a': random.randint(1, 2 ** self.p - 1), 'b': random.randint(1, 2 ** self.p - 1)} for i in range(self.m)]
        else:
            print("\033[91mНеправильный выбор режима.\033[0m")
            sys.exit(1)

        self.sim = Simulation(self.p, self.n, self.queue, self.times)

        while True:
            self.display_simulation()
            choice = input("\n>> ").strip()
            
            if choice == '1':
                if not self.sim.queue and not any(s.current_pair for s in self.sim.stages):
                    self.sim.calculate_metrics()
                    print("\n\033[92mВсе пары успешно обработаны!\033[0m")
                    break
                self.sim.next_tact()
            elif choice == '2':
                self.sim.load_state()
            elif choice == '3':
                # Быстро завершаем до конца
                while self.sim.queue or any(s.current_pair for s in self.sim.stages):
                    self.sim.next_tact()
                self.sim.calculate_metrics()
                self.display_simulation()
                print("\n\033[92mСимуляция автоматически завершена!\033[0m")
                break
            else:
                print("\033[93mНеверная команда, попробуйте снова.\033[0m")

        if self.sim.ky > 0:
            print(f"\n\033[1;94mМетрики:\033[0m")
            print(f"  Коэффициент ускорения (Ky): \033[93m{self.sim.ky:.2f}\033[0m")
            print(f"  Эффективность (Eff):        \033[93m{self.sim.eff:.2f}\033[0m")
            
            plot_choice = input("\nПостроить графики? (y/n): ").strip().lower()
            if plot_choice in ('y', 'yes', 'д', 'да'):
                max_m_input = input("Введите максимальное количество пар для графиков (по умолчанию 20): ").strip()
                try:
                    max_m = int(max_m_input) if max_m_input else 20
                except ValueError:
                    max_m = 20
                
                print("\033[96mПостроение графиков...\033[0m")
                plot_metrics(self.p, self.n, self.times, max_m)
