import math


def prepare_text(text, lang='ru'):
    """Подготовка текста: удаление пробелов и приведение к верхнему регистру"""
    text = text.upper()
    if lang == 'ru':
        cleaned = ''.join(c for c in text if c in 'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ')
    else:
        cleaned = ''.join(c for c in text if c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ')
    return cleaned


def encrypt(text, rows, cols):
    """Шифрование текста с использованием таблицы заданного размера"""
    block_size = rows * cols
    # Добавляем padding только до ближайшего кратного
    padding = (block_size - len(text) % block_size) % block_size
    if padding != 0:
        text += 'X' * padding

    encrypted = []
    for i in range(0, len(text), block_size):
        block = text[i:i + block_size]
        table = [list(block[j:j + cols]) for j in range(0, len(block), cols)]
        # Чтение по столбцам
        for col in range(cols):
            for row in range(rows):
                encrypted.append(table[row][col])
    return ''.join(encrypted)


def decrypt(text, rows, cols):
    """Дешифрование текста с использованием таблицы заданного размера"""
    decrypted = []
    block_size = rows * cols

    for i in range(0, len(text), block_size):
        block = text[i:i + block_size]
        table = [[''] * cols for _ in range(rows)]
        # Заполнение таблицы по столбцам
        idx = 0
        for col in range(cols):
            for row in range(rows):
                if idx < len(block):
                    table[row][col] = block[idx]
                    idx += 1
        # Чтение по строкам
        for row in range(rows):
            for col in range(cols):
                decrypted.append(table[row][col])

    result = ''.join(decrypted)
    # Убираем padding при выводе
    return result.rstrip('X')


def brute_force_attack(ciphertext, known_plaintext=None, max_size=20):
    """Атака полным перебором возможных размеров таблицы"""
    possible_solutions = []
    length = len(ciphertext)

    for rows in range(2, min(max_size, length // 2 + 1)):
        for cols in range(2, min(max_size, length // 2 + 1)):
            if rows * cols < length:
                continue

            try:
                decrypted = decrypt(ciphertext, rows, cols)

                if known_plaintext:
                    # Ищем вхождение известного текста
                    if known_plaintext in decrypted:
                        possible_solutions.append((rows, cols, decrypted))
                else:
                    # Визуальная оценка
                    print(f"Размер {rows}x{cols}: {decrypted[:50]}...")
            except:
                continue

    return possible_solutions


# Пример использования
if __name__ == "__main__":
    # Исходный текст
    plaintext = "Пример текста для шифрования"
    rows, cols = 4, 7  # 4×7 = 28 (ближайшее кратное для 25 символов)

    # Подготовка текста
    prepared_text = prepare_text(plaintext, 'ru')
    print(f"Исходный текст: {prepared_text}")
    print(f"Длина текста: {len(prepared_text)} символов")

    # Шифрование
    encrypted = encrypt(prepared_text, rows, cols)
    print(f"Зашифрованный текст: {encrypted}")

    # Дешифрование
    decrypted = decrypt(encrypted, rows, cols)
    print(f"Дешифрованный текст: {decrypted}")

    # Атака полным перебором
    print("\nАтака полным перебором:")
    solutions = brute_force_attack(encrypted, prepared_text)
    if solutions:
        print("Найдены возможные решения:")
        for rows, cols, text in solutions:
            print(f"Размер таблицы: {rows}x{cols}, Текст: {text}")
    else:
        print("Решения не найдены")