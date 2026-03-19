# -*- coding: utf-8 -*-
"""
Лабораторная работа 5.2
Реализация алгоритма RSA: генерация ключей, шифрование, электронная цифровая подпись
"""

import random
import math
import os
import shutil
from pathlib import Path

# Конфигурация
RSA_BITS = 1024
TEST_MESSAGES = [
    "Hello RSA encryption test",
    "Secret message 12345",
    "Тестирование RSA на русском",
    "Шифрование и цифровая подпись",
    "Сообщение для проверки ЭЦП",
    "Test message number six",
    "RSA cryptographic operations",
    "Проверка работы алгоритма",
    "Final test message nine",
    "Последнее тестовое сообщение"
]


def clean_workspace():
    """Очистка и создание рабочей директории"""
    workspace = Path("rsa_workspace")
    if workspace.exists():
        shutil.rmtree(workspace)
    workspace.mkdir()
    return workspace


def is_prime(n, k=5):
    """Проверка простоты методом Миллера-Рабина"""
    if n <= 3:
        return n > 1
    if n % 2 == 0:
        return False

    d = n - 1
    s = 0
    while d % 2 == 0:
        d //= 2
        s += 1

    for _ in range(k):
        a = random.randint(2, n - 2)
        x = pow(a, d, n)

        if x in (1, n - 1):
            continue

        for _ in range(s - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False

    return True


def generate_prime(bits):
    """Генерация простого числа заданной битности"""
    while True:
        num = random.getrandbits(bits)
        num |= (1 << bits - 1) | 1
        if is_prime(num):
            return num


def mod_inverse(a, m):
    """Вычисление модульного обратного элемента"""
    g, x, _ = extended_gcd(a, m)
    if g != 1:
        raise ValueError("Обратный элемент не существует")
    return x % m


def extended_gcd(a, b):
    """Расширенный алгоритм Евклида"""
    if a == 0:
        return b, 0, 1
    g, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    return g, x, x1


def generate_rsa_keys(bits):
    """Генерация пары ключей RSA"""
    print("Генерация ключей RSA...")

    p = generate_prime(bits // 2)
    q = generate_prime(bits // 2)
    while p == q:
        q = generate_prime(bits // 2)

    n = p * q
    phi = (p - 1) * (q - 1)

    e = 65537
    while math.gcd(e, phi) != 1:
        e = random.randint(2, phi - 1)

    d = mod_inverse(e, phi)

    print(f"Сгенерированные параметры:")
    print(f"p = {p}")
    print(f"q = {q}")
    print(f"n = p * q = {n}")
    print(f"φ(n) = (p-1)*(q-1) = {phi}")
    print(f"e = {e}")
    print(f"d = e^(-1) mod φ(n) = {d}")
    print("Генерация ключей завершена")

    return (e, n), (d, n)


def rsa_encrypt(message, public_key):
    """Шифрование сообщения открытым ключом"""
    e, n = public_key
    return pow(message, e, n)


def rsa_decrypt(ciphertext, private_key):
    """Дешифрование сообщения закрытым ключом"""
    d, n = private_key
    return pow(ciphertext, d, n)


def rsa_sign(message, private_key):
    """Создание цифровой подписи"""
    d, n = private_key
    return pow(message, d, n)


def rsa_verify(message, signature, public_key):
    """Проверка цифровой подписи"""
    e, n = public_key
    return pow(signature, e, n) == message


def message_to_int(message):
    """Преобразование текста в числовое представление"""
    return int.from_bytes(message.encode('utf-8'), 'big')


def int_to_message(number):
    """Преобразование числа обратно в текст"""
    return number.to_bytes((number.bit_length() + 7) // 8, 'big').decode('utf-8')


def create_test_files(workspace):
    """Создание тестовых сообщений"""
    print("Создание тестовых сообщений...")
    for i, msg in enumerate(TEST_MESSAGES, 1):
        msg_int = message_to_int(msg)
        with open(workspace / f"message_{i}.txt", 'w', encoding='utf-8') as f:
            f.write(f"Сообщение: {msg}\n")
            f.write(f"Числовое представление: {msg_int}")
        print(f"Сообщение {i}: {msg}")


def save_key(key, filename, workspace, description=""):
    """Сохранение ключа в файл"""
    with open(workspace / filename, 'w', encoding='utf-8') as f:
        if description:
            f.write(f"{description}: {key}\n")
        else:
            f.write(str(key))


def load_key(filename, workspace):
    """Загрузка ключа из файла"""
    with open(workspace / filename, 'r', encoding='utf-8') as f:
        content = f.read()
        for line in content.split('\n'):
            if ':' in line:
                return int(line.split(':')[-1].strip())
        return int(content.strip())


def test_rsa(workspace):
    """Полное тестирование RSA"""
    print("Запуск тестирования RSA...")

    # Генерация ключей
    public_key, private_key = generate_rsa_keys(RSA_BITS)

    # Сохранение ключей
    save_key(public_key[0], "public_e.txt", workspace, "Публичная экспонента")
    save_key(public_key[1], "public_n.txt", workspace, "Публичный модуль")
    save_key(private_key[0], "private_d.txt", workspace, "Приватная экспонента")
    save_key(private_key[1], "private_n.txt", workspace, "Приватный модуль")

    success_count = 0
    test_results = []

    for i in range(1, 11):
        print(f"\n--- Тест {i} ---")

        try:
            # Загрузка и преобразование сообщения
            with open(workspace / f"message_{i}.txt", 'r', encoding='utf-8') as f:
                content = f.read()
                msg_line = content.split('\n')[0]
                original_msg = msg_line.split(': ')[1]
                msg_int = message_to_int(original_msg)

            print(f"Исходное сообщение: {original_msg}")
            print(f"Числовое представление: {msg_int}")

            # Шифрование
            encrypted = rsa_encrypt(msg_int, public_key)
            save_key(encrypted, f"encrypted_{i}.txt", workspace, "Зашифрованное сообщение")
            print(f"Зашифрованное сообщение: {encrypted}")

            # Дешифрование
            decrypted = rsa_decrypt(encrypted, private_key)
            decrypted_msg = int_to_message(decrypted)
            print(f"Расшифрованное сообщение: {decrypted_msg}")

            # Проверка шифрования
            encryption_ok = decrypted == msg_int
            print(f"Проверка шифрования: {'УСПЕХ' if encryption_ok else 'ОШИБКА'}")

            # Цифровая подпись
            signature = rsa_sign(msg_int, private_key)
            save_key(signature, f"signature_{i}.txt", workspace, "Цифровая подпись")
            print(f"Цифровая подпись: {signature}")

            # Проверка подписи
            signature_ok = rsa_verify(msg_int, signature, public_key)
            print(f"Проверка подписи: {'ВЕРНА' if signature_ok else 'НЕВЕРНА'}")

            # Сохранение результатов
            if encryption_ok and signature_ok:
                success_count += 1
                test_results.append(f"Тест {i}: УСПЕХ")
            else:
                test_results.append(f"Тест {i}: ОШИБКА")

        except Exception as e:
            print(f"Тест {i}: ОШИБКА - {e}")
            test_results.append(f"Тест {i}: ОШИБКА - {e}")

    # Вывод итоговых результатов
    print("\n" + "=" * 50)
    print("ИТОГИ ТЕСТИРОВАНИЯ")
    print("=" * 50)

    for result in test_results:
        print(result)

    print(f"\nОбщий результат: {success_count}/10 тестов пройдено успешно")

    if success_count == 10:
        print("ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО")
        print("Шифрование и дешифрование работают корректно")
        print("Цифровые подписи создаются и проверяются")
        print("Алгоритм RSA реализован правильно")
    else:
        print("Обнаружены ошибки в реализации")

    return success_count


def main():
    """Основная функция программы"""
    print("Лабораторная работа 5.2")
    print("Реализация алгоритма RSA: генерация ключей, шифрование, ЭЦП")
    print("=" * 60)
    print(f"Длина ключа: {RSA_BITS} бит")
    print("=" * 60)

    # Очистка и создание рабочей директории
    workspace = clean_workspace()
    print(f"Рабочая директория: {workspace}")

    # Создание тестовых сообщений
    create_test_files(workspace)

    # Запуск тестирования
    success_count = test_rsa(workspace)

    print(f"\nВсе файлы сохранены в: {workspace}")
    print("Содержимое рабочей директории:")
    for file in workspace.iterdir():
        print(f"  {file.name}")

    print(f"\nЗавершено с результатом: {success_count}/10 успешных тестов")


if __name__ == "__main__":
    main()