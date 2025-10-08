import numpy as np
import matplotlib.pyplot as plt
import time

# (Рекурсивный алгоритм Кули-Тьюки)

def my_fft(x):
    """
    Рекурсивная реализация БПФ "с нуля".
    На вход принимает одномерный массив numpy, размер которого должен быть степенью двойки.
    """
    N = len(x)

    # Базовый случай рекурсии: если в массиве 1 элемент, его БПФ - он сам
    if N == 1:
        return x

    # Проверка, является ли N степенью двойки (упрощённая)
    if N % 2 > 0:
        raise ValueError("Размер входного массива должен быть степенью двойки")

    # Рекурсивный шаг: делим массив на четные и нечетные элементы
    even_part = my_fft(x[::2])
    odd_part = my_fft(x[1::2])

    # Вычисляем "поворачивающие множители"
    # T = [exp(-2j*pi*k/N) for k in range(N//2)]
    factors = np.exp(-2j * np.pi * np.arange(N) / N)

    # Объединяем результаты
    # Формула объединения: X_k = E_k + T_k * O_k
    #                     X_{k+N/2} = E_k - T_k * O_k
    # где E - БПФ от четной части, O - от нечетной
    result = np.concatenate([even_part + factors[:N//2] * odd_part,
                             even_part + factors[N//2:] * odd_part])
    return result


# --- Шаг 2: Создание входного сигнала ---

# Параметры сигнала
N = 512              # Количество точек. ОБЯЗАТЕЛЬНО СТЕПЕНЬ ДВОЙКИ для нашей реализации!
FREQUENCY = 15       # Частота синусоиды в Гц
SAMPLING_RATE = 200  # Частота дискретизации в Гц

# Создаем временную шкалу и сам сигнал (синусоиду)
x_time = np.linspace(0.0, N / SAMPLING_RATE, N, endpoint=False)
y_signal = np.sin(2 * np.pi * FREQUENCY * x_time)


# --- Шаг 3: Выполнение и сравнение ---

# 3.1. Используем нашу реализацию и замеряем время
start_time_my_fft = time.time()
my_yf = my_fft(y_signal)
end_time_my_fft = time.time()
my_fft_time = end_time_my_fft - start_time_my_fft

# 3.2. Используем библиотечную реализацию NumPy и замеряем время
start_time_np_fft = time.time()
np_yf = np.fft.fft(y_signal)
end_time_np_fft = time.time()
np_fft_time = end_time_np_fft - start_time_np_fft


# --- Шаг 4: Обработка результатов для построения графиков ---

# Создаем шкалу частот для оси X
xf = np.fft.fftfreq(N, 1 / SAMPLING_RATE)[:N//2]

# Считаем амплитудные спектры
my_amplitude_spectrum = 2.0/N * np.abs(my_yf[0:N//2])
np_amplitude_spectrum = 2.0/N * np.abs(np_yf[0:N//2])


# --- Шаг 5: Визуализация и вывод результатов ---

print(f"Время выполнения реализации БПФ: {my_fft_time:.6f} секунд")
print(f"Время выполнения NumPy БПФ:          {np_fft_time:.6f} секунд")
print("-" * 30)
if np_fft_time > 0:
    print(f"Реализация NumPy быстрее примерно в {my_fft_time / np_fft_time:.2f} раз.")

# Сравним, совпадают ли результаты (с небольшой погрешностью)
is_close = np.allclose(my_amplitude_spectrum, np_amplitude_spectrum)
print(f"Результаты совпадают: {'Да!' if is_close else 'Нет!'}")


# Строим графики для визуального сравнения
plt.figure(figsize=(12, 8))

# График исходного сигнала
plt.subplot(2, 1, 1)
plt.plot(x_time, y_signal)
plt.title('Исходный сигнал: sin(x)')
plt.xlabel('Время (с)')
plt.ylabel('Амплитуда')
plt.grid()

# Графики спектров от обеих реализаций
plt.subplot(2, 1, 2)
plt.plot(xf, my_amplitude_spectrum, label='Реализация БПФ', linestyle='--')
plt.plot(xf, np_amplitude_spectrum, label='Библиотечная NumPy БПФ', alpha=0.7)
plt.title('Сравнение амплитудных спектров')
plt.xlabel('Частота (Гц)')
plt.ylabel('Амплитуда')
plt.legend()
plt.grid()

plt.tight_layout()
plt.show()