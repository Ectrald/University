# -*- coding: utf-8 -*-

def power(base, exp, mod):
    res = 1
    base %= mod
    while exp > 0:
        # Если текущий бит показателя степени равен 1
        if exp % 2 == 1:
            res = (res * base) % mod
        # Возводим основание в квадрат для следующего бита
        base = (base * base) % mod
        # Переходим к следующему биту
        exp //= 2
    return res


def is_primitive_root(g, p):
    if g <= 0 or g >= p:
        return False

    # Множество для хранения сгенерированных значений
    generated_values = set()

    # Проверяем все степени от 1 до p-1
    for i in range(1, p):
        val = power(g, i, p)
        if val in generated_values:
            # Если значение повторилось, g - не первообразный корень
            return False
        generated_values.add(val)

    # Если все p-1 значений уникальны, то g - первообразный корень
    return len(generated_values) == p - 1


def find_first_primitive_root(p):
    print(f"Поиск первого первообразного корня для P = {p}...")
    # Перебираем g, начиная с 2
    for g in range(2, p):
        if is_primitive_root(g, p):
            print(f"Найден первообразный корень: g = {g}")
            return g
    return None


def diffie_hellman_protocol(p, g, a, b):
    print("\n--- Шаги протокола Диффи-Хеллмана ---")

    # Шаг 1: Алиса вычисляет A и отправляет Бобу
    A = power(g, a, p)
    print(f"Алиса выбрала секретное число a = {a}")
    print(f"Алиса вычисляет A = g^a mod P = {g}^{a} mod {p} = {A}")
    print(f"Алиса отправляет Бобу открытое значение A = {A}\n")

    # Шаг 2: Боб вычисляет B и отправляет Алисе
    B = power(g, b, p)
    print(f"Боб выбрал секретное число b = {b}")
    print(f"Боб вычисляет B = g^b mod P = {g}^{b} mod {p} = {B}")
    print(f"Боб отправляет Алисе открытое значение B = {B}\n")

    # Шаг 3: Алиса вычисляет общий секрет
    secret_A = power(B, a, p)
    print(f"Алиса получила B = {B} и вычисляет общий секрет K_A = B^a mod P = {B}^{a} mod {p} = {secret_A}")

    # Шаг 4: Боб вычисляет общий секрет
    secret_B = power(A, b, p)
    print(f"Боб получил A = {A} и вычисляет общий секрет K_B = A^b mod P = {A}^{b} mod {p} = {secret_B}\n")

    # Проверка
    if secret_A == secret_B:
        print(f"Общий секрет K = {secret_A} успешно сгенерирован обеими сторонами.")
    else:
        print("Секреты не совпадают.")


# --- Основная часть ---
if __name__ == "__main__":
    P = 3917

    g = find_first_primitive_root(P)

    if g:
        a_secret = 101
        b_secret = 257

        diffie_hellman_protocol(P, g, a_secret, b_secret)