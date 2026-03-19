from collections import Counter
import math
import random
import matplotlib.pyplot as plt
def analyze_string(generated_string):
    """Анализирует строку и возвращает параметры для оценки сложности подбора"""
    # Подсчет уникальных символов
    unique_chars = len(set(generated_string))

    # Подсчет частот символов для проверки равномерности
    char_counts = Counter(generated_string)
    total_chars = len(generated_string)

    # Расчет энтропии на символ (мера неопределенности)
    entropy_per_char = 0
    for count in char_counts.values():
        probability = count / total_chars
        entropy_per_char -= probability * math.log2(probability)

    return unique_chars, entropy_per_char


def calculate_password_strength(unique_chars, entropy_per_char, password_length):
    """Рассчитывает сложность подбора пароля"""
    # Максимально возможная сложность (равномерное распределение)
    max_possible_combinations = unique_chars ** password_length

    # Реальная сложность с учетом энтропии
    effective_combinations = 2 ** (entropy_per_char * password_length)

    # Среднее количество попыток для подбора (50% от общего числа)
    avg_attempts_needed = effective_combinations / 2

    return max_possible_combinations, effective_combinations, avg_attempts_needed


def calculate_cracking_time(attempts_needed, attempts_per_second):
    """Рассчитывает время подбора пароля"""
    seconds = attempts_needed / attempts_per_second

    time_units = [
        (seconds, "секунд"),
        (seconds / 60, "минут"),
        (seconds / 3600, "часов"),
        (seconds / (3600 * 24), "дней"),
        (seconds / (3600 * 24 * 365), "лет")
    ]

    return time_units

def plot_cracking_time_analysis(max_comb, eff_comb, avg_attempts, time_units):
    """Визуализирует анализ времени подбора"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))

    # График 1
    labels = ['Максимально возможные', 'Эффективные (с учетом энтропии)']
    values = [max_comb, eff_comb]

    ax1.bar(labels, values, color=['lightblue', 'lightcoral'])
    ax1.set_yscale('log')
    ax1.set_ylabel('Количество комбинаций (лог. шкала)')
    ax1.set_title('Сравнение сложности подбора пароля')

    # График 2
    times, units = zip(*time_units)
    ax2.bar(units, times, color='lightgreen')
    ax2.set_yscale('log')
    ax2.set_ylabel('Время (лог. шкала)')
    ax2.set_title('Среднее время подбора пароля')
    ax2.tick_params(axis='x', rotation=45)

    plt.tight_layout()
    plt.show()


def evaluate_password_cracking_time(generated_string, password_length=8, attempts_per_second=1000000):
    """Полная оценка времени подбора пароля"""

    # Анализ
    unique_chars, entropy_per_char = analyze_string(generated_string)
    print(f"Длина строки: {len(generated_string)} символов")
    print(f"Уникальные символы: {unique_chars}")
    print(f"Энтропия на символ: {entropy_per_char:.2f} бит")

    # Расчет сложности
    max_comb, eff_comb, avg_attempts = calculate_password_strength(
        unique_chars, entropy_per_char, password_length
    )

    print(f"\nДля пароля длиной {password_length} символов:")
    print(f"Максимально возможных комбинаций: {max_comb:.2e}")
    print(f"Эффективных комбинаций (с учетом энтропии): {eff_comb:.2e}")
    print(f"Среднее количество попыток для подбора: {avg_attempts:.2e}")

    # Расчет времени
    time_units = calculate_cracking_time(avg_attempts, attempts_per_second)

    print(f"\nПри скорости {attempts_per_second:,} попыток в секунду:")
    for time_value, unit in time_units:
        if time_value > 1:
            print(f"- {time_value:.2e} {unit}")

    # Визуализация
    plot_cracking_time_analysis(max_comb, eff_comb, avg_attempts, time_units)

    return avg_attempts, time_units

cyrillic_lower_letters = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'
cyrillic_letters = cyrillic_lower_letters + cyrillic_lower_letters.upper()
def calc_time_graph():
    line_length: int = int(input("Длина строки: "))

    random_line = "".join(random.choices(cyrillic_letters, k=line_length))

    # Подсчёт и график
    counts = Counter(random_line)

    labels = sorted(cyrillic_letters)
    values = [counts.get(char, 0) for char in labels]

    plt.figure(figsize=(16, 6))

    bars = plt.bar(labels, values, color='skyblue')

    expected_frequency = line_length / len(cyrillic_letters)
    plt.axhline(y=expected_frequency, color='r', linestyle='--', label=f'Ожидаемая частота (~{expected_frequency:.0f})')
    plt.legend()

    plt.xlabel('Символы')
    plt.ylabel('Частота появления')
    plt.title('Проверка равномерности распределения символов')
    plt.xticks(rotation=45)

    plt.tight_layout()
    plt.show()

    # Расчет времени подбора пароля
    avg_attempts, cracking_times = evaluate_password_cracking_time(random_line, len(random_line), 1000000)

def calc_crack_time(line_length, attempts_per_second = 1000000):
    random_line = "".join(random.choices(cyrillic_letters, k=line_length))

    # Анализ
    unique_chars, entropy_per_char = analyze_string(random_line)

    # Расчет сложности
    max_comb, eff_comb, avg_attempts = calculate_password_strength(
        unique_chars, entropy_per_char, line_length
    )

    # Расчет времени
    time_units = calculate_cracking_time(avg_attempts, attempts_per_second)

    return time_units
def graph_of_avg_cracking_time():
    list_of_length = [8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18]
    list_of_cracking_times = []
    for length in list_of_length:
        list_of_cracking_times.append(calc_crack_time(length))

    avg_cracking_time = {key : value for key, value in zip(list_of_length, list_of_cracking_times)}

    # Извлекаем данные из словаря
    lengths = list(avg_cracking_time.keys())

    # Преобразуем время - берем только секунды (первый элемент каждого кортежа)
    times_seconds = []
    for time_data in avg_cracking_time.values():
        if isinstance(time_data, (list, tuple)) and len(time_data) > 0:
            # Берем время в секундах (первый элемент первого кортежа)
            seconds = time_data[0][0] if isinstance(time_data[0], (list, tuple)) else time_data[0]
            times_seconds.append(seconds)
        else:
            times_seconds.append(time_data)  # Если это уже число

    # Функция для форматирования времени
    def time_formatter(x, pos):
        if x < 60:  # секунды
            return f'{x:.1f}s'
        elif x < 3600:  # минуты
            return f'{x / 60:.1f}m'
        elif x < 86400:  # часы
            return f'{x / 3600:.1f}h'
        elif x < 31536000:  # дни
            return f'{x / 86400:.1f}d'
        else:  # годы
            return f'{x / 31536000:.1f}y'

    # Создаем график
    plt.figure(figsize=(14, 8))

    # Используем столбчатую диаграмму
    bars = plt.bar(lengths, times_seconds, color='skyblue', edgecolor='navy', alpha=0.7)

    plt.xlabel('Длина пароля', fontsize=12)
    plt.ylabel('Время взлома (в секундах)', fontsize=12)
    plt.title('Зависимость времени взлома от длины пароля', fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3, axis='y')
    plt.xticks(lengths)

    # Применяем форматирование времени к оси Y
    plt.gca().yaxis.set_major_formatter(time_formatter)

    # Добавляем значения на столбцы
    for i, (length, time_val) in enumerate(zip(lengths, times_seconds)):
        plt.text(length, time_val, time_formatter(time_val, None),
                 ha='center', va='bottom', fontweight='bold', fontsize=9)

    # Добавляем сетку
    plt.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()

    return avg_cracking_time

def recommendation():
    print("Исходя из графика, если ваш пароль состоит исключительно из букв русского алфавита, вам нужно составлять"
          " пароль длинной не менее 13 символов.")