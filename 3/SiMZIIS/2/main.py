# -*- coding: utf-8 -*-
import math
import itertools



def encrypt(plaintext: str, key: list[int]) -> str:
    """
    Выполняет шифрование текста методом простой табличной перестановки.

    :param plaintext: Исходный текст для шифрования.
    :param key: Ключ, представляющий собой перестановку чисел от 1 до N.
    :return: Зашифрованный текст.
    """
    key_len = len(key)
    num_rows = math.ceil(len(plaintext) / key_len)
    padded_text = plaintext.ljust(num_rows * key_len)

    # Заполнение таблицы исходным текстом по строкам
    table = [list(padded_text[i:i + key_len]) for i in range(0, len(padded_text), key_len)]

    # Считывание столбцов в порядке, определенном ключом
    ciphertext = ''
    sorted_key_indices = sorted(range(len(key)), key=lambda k: key[k])

    for col_index in sorted_key_indices:
        for r in range(num_rows):
            ciphertext += table[r][col_index]

    return ciphertext


def decrypt(ciphertext: str, key: list[int]) -> str:
    """
    Выполняет расшифрование текста, зашифрованного методом табличной перестановки.

    :param ciphertext: Зашифрованный текст.
    :param key: Ключ, использованный для шифрования.
    :return: Исходный текст.
    """
    key_len = len(key)
    text_len = len(ciphertext)
    num_rows = math.ceil(text_len / key_len)

    table = [['' for _ in range(key_len)] for _ in range(num_rows)]

    # Вычисление количества неполных столбцов
    num_short_cols = key_len - (text_len % key_len) if text_len % key_len != 0 else 0
    sorted_key_indices = sorted(range(len(key)), key=lambda k: key[k])

    # Восстановление таблицы путем заполнения столбцов в порядке ключа
    text_index = 0
    for col_index in sorted_key_indices:
        rows_in_this_col = num_rows
        if key[col_index] > key_len - num_short_cols:
            rows_in_this_col = num_rows - 1

        for r in range(rows_in_this_col):
            table[r][col_index] = ciphertext[text_index]
            text_index += 1

    # Считывание исходного текста из таблицы по строкам
    plaintext = "".join("".join(row) for row in table)

    return plaintext.strip()

def brute_force_attack(ciphertext: str, key_length: int, original_text: str = None) -> list[int] or None:
    """
    Реализует атаку полным перебором для определения ключа шифрования.

    Метод генерирует все возможные перестановки ключа заданной длины и
    применяет их для расшифрования. Результат верифицируется либо
    автоматически (сравнением с `original_text`), либо визуально.

    :param ciphertext: Зашифрованный текст.
    :param key_length: Предполагаемая длина ключа.
    :param original_text: (Опционально) Исходный текст для автоматической верификации.
    :return: Найденный ключ в виде списка или None, если ключ не найден.
    """
    print(f"\n--- Начало атаки полным перебором (длина ключа: {key_length}) ---")

    base_key = list(range(1, key_length + 1))
    possible_keys = list(itertools.permutations(base_key))

    print(f"Общее количество комбинаций ключей для проверки: {len(possible_keys)}")

    for i, key_tuple in enumerate(possible_keys):
        key = list(key_tuple)
        decrypted_attempt = decrypt(ciphertext, key)

        if original_text and decrypted_attempt == original_text:
            print(f"\n[УСПЕХ] Ключ найден автоматически на итерации {i + 1}.")
            print(f"  > Ключ: {key}")
            print(f"  > Расшифрованный текст: '{decrypted_attempt}'")
            return key

    print("\n[ПРЕДУПРЕЖДЕНИЕ] Автоматический поиск не дал результатов.")
    print("Для визуального анализа требуется раскомментировать соответствующий блок в коде.")
    # Блок для визуального анализа:
    # print("\n--- Варианты для визуального анализа ---")
    # for key_tuple in possible_keys:
    #     key = list(key_tuple)
    #     print(f"  Ключ {key}: '{decrypt(ciphertext, key)}'")

    return None

"""
Криптографическая стойкость данного шифра определяется размером ключевого
пространства, которое для ключа длиной N равно N! (N факториал).

- **Ключевое пространство**: Количество ключей растет факториально, однако
  остается недостаточным для защиты от современных вычислительных систем.
  -   N = 8:   8! = 40 320 (перебор мгновенен)
  -   N = 12:  12! = 479 001 600 (перебор занимает секунды)
  -   N = 15:  15! ≈ 1.3 * 10^12 (перебор возможен)

- **Основная уязвимость**: Шифр не изменяет символы сообщения, а лишь
  переставляет их. Это полностью сохраняет частотные характеристики исходного
  языка, что делает его уязвимым для частотного анализа, особенно при обработке
  длинных текстов.

**Заключение**: Шифр является нестойким и представляет исключительно
академический интерес.
"""

"""
### Модификация 1: Двойная перестановка

Применение шифра перестановки дважды с использованием двух разных ключей (K1, K2).
Это создает более сложную перестановку и экспоненциально увеличивает ключевое
пространство до N! * M!, где N и M — длины соответствующих ключей.

- **Алгоритм шифрования**: C = Encrypt(Encrypt(P, K1), K2)
- **Алгоритм расшифрования**: P = Decrypt(Decrypt(C, K2), K1)

### Модификация 2: Построение продуктового шифра

Комбинация шифра перестановки (обеспечивающего рассеивание) с шифром замены,
например, шифром Цезаря (обеспечивающим перемешивание).

- **Алгоритм шифрования**:
  1. Применить шифр замены к исходному тексту P, получив P'.
  2. Применить шифр перестановки к P', получив шифртекст C.

- **Алгоритм расшифрования**:
  1. Применить обратную перестановку к C, получив P'.
  2. Применить обратную замену к P', получив исходный текст P.

Данный подход нарушает статистические свойства языка в шифртексте, что значительно
повышает стойкость к частотному анализу и является базовым принципом
построения современных блочных шифров.
"""

if __name__ == "__main__":

    message = "ПРИМЕР ШИФРОВАНИЯ ПРОСТОЙ ПЕРЕСТАНОВКОЙ"
    key = [4, 1, 3, 2, 5]

    print(f"Исходное сообщение: '{message}'")
    print(f"Ключ: {key}")

    encrypted_message = encrypt(message, key)
    print(f"Зашифрованное сообщение: '{encrypted_message}'")

    decrypted_message = decrypt(encrypted_message, key)
    print(f"Расшифрованное сообщение: '{decrypted_message}'")

    if message == decrypted_message:
        print("\nСтатус: Верификация пройдена успешно.")
    else:
        print("\nСтатус: Ошибка верификации.")

    # --- Демонстрация атаки ---
    print("\n" + "=" * 60)
    print("Атака")
    print("=" * 60)

    # Имитация атаки на перехваченное сообщение с известной длиной ключа
    brute_force_attack(
        ciphertext=encrypted_message,
        key_length=len(key),
        original_text=message
    )

    print("\n" + "=" * 60)
    print("Разделы 3 и 4: Теоретический анализ")
    print("=" * 60)
    print("Анализ стойкости и предложения по модификации приведены в docstring-комментариях к коду.")
    print("\nДемонстрация завершена.")