"""
Лабораторная работа №1 по логическим основам интеллектуальных систем
Тема: Программирование операций обработки и преобразований формул языка логики высказываний
Вариант 2: Проверка является ли формула общезначимой (тавтологией)
Автор: Германенко Владислав Вадимович
Группа: 321701
17.05.2025
Использованные источники:
Справочная система по дисциплине ЛОИС
Логические основы интеллектуальных систем. Практикум
"""


def implication(p, q):
    """Реализация логической импликации"""
    return not p or q

def equivalence(p, q):
    """Реализация логической эквивалентности"""
    return p == q


def generate_truth_values(n):
    """Генерация всех возможных комбинаций значений истинности для n переменных"""
    return [[bool(int(x)) for x in bin(i)[2:].zfill(n)] for i in range(2 ** n)]


def precedence(op):
    """Определение приоритета операций для преобразования в постфиксную форму"""
    if op == '!':
        return 3
    if op in ('&', '|'):
        return 2
    if op in ('->', '~'):
        return 1
    return 0


def infix_to_postfix(expression):
    """Преобразование инфиксной записи в постфиксную (обратную польскую)"""
    output = []
    stack = []
    i = 0
    while i < len(expression):
        if expression[i].isalpha():
            output.append(expression[i])
        elif expression[i] in "!&|":
            while stack and precedence(stack[-1]) >= precedence(expression[i]):
                output.append(stack.pop())
            stack.append(expression[i])
        elif expression[i] == '-' and i + 1 < len(expression) and expression[i + 1] == '>':
            while stack and precedence(stack[-1]) >= precedence('->'):
                output.append(stack.pop())
            stack.append("->")
            i += 1
        elif expression[i] == '~':
            while stack and precedence(stack[-1]) >= precedence('~'):
                output.append(stack.pop())
            stack.append("~")
        elif expression[i] == '(':
            stack.append(expression[i])
        elif expression[i] == ')':
            while stack and stack[-1] != '(':
                output.append(stack.pop())
            stack.pop()
        i += 1
    while stack:
        output.append(stack.pop())
    return output


def evaluate_postfix(postfix_tokens, values):
    """Вычисление значения логического выражения в постфиксной форме"""
    stack = []
    operators = {
        "&": lambda a, b: a and b,
        "|": lambda a, b: a or b,
        "!": lambda a: not a,
        "->": implication,
        "~": equivalence
    }

    for token in postfix_tokens:
        if token in values:
            stack.append(values[token])
        elif token in operators:
            if token == "!":
                operand = stack.pop()
                stack.append(operators[token](operand))
            else:
                b = stack.pop()
                a = stack.pop()
                stack.append(operators[token](a, b))
        else:
            raise ValueError(f"Неизвестный токен: {token}")
    return stack.pop()


def is_tautology(expression, variables):
    """Проверка является ли формула тавтологией"""
    postfix_tokens = infix_to_postfix(expression)
    for values in generate_truth_values(len(variables)):
        values_dict = dict(zip(variables, values))
        result = evaluate_postfix(postfix_tokens, values_dict)
        if not result:
            return False
    return True


def analyze_formula(expression):
    """Основная функция анализа формулы"""
    variables = sorted(set(filter(str.isalpha, expression)))

    if not variables:
        print("Ошибка: в формуле отсутствуют переменные")
        return

    print("\nАнализ формулы:", expression)
    print("Используемые переменные:", ", ".join(variables))

    # Проверка на тавтологию
    if is_tautology(expression, variables):
        print("\nРезультат: Формула является ТАВТОЛОГИЕЙ (общезначимой)")
    else:
        print("\nРезультат: Формула НЕ является тавтологией")

    # Построение таблицы истинности
    print("\nТаблица истинности:")
    postfix_tokens = infix_to_postfix(expression)
    header = " | ".join(variables) + " | Result"
    print(header)
    print("-" * len(header))

    for values in generate_truth_values(len(variables)):
        values_dict = dict(zip(variables, values))
        result = evaluate_postfix(postfix_tokens, values_dict)
        row = " | ".join([str(int(val)) for val in values] + [str(int(result))])
        print(row)


def user_test():
    """Режим тестирования знаний пользователя"""
    test_cases = [
        {"formula": "(A->B)", "is_tautology": False},
        {"formula": "((A->B)->(!B->!A))", "is_tautology": True},
        {"formula": "(A|!A)", "is_tautology": True},
        {"formula": "(A&!A)", "is_tautology": False},
        {"formula": "((A->(B->A)))", "is_tautology": True},
        {"formula": "A", "is_tautology": False},
        {"formula": "((A->B)->A)", "is_tautology": False},
        {"formula": "((A~B)->(A->B))", "is_tautology": True},
        {"formula": "(((A|B)&(!A|C))->(B|C))", "is_tautology": True},
        {"formula": "((A&(A->B))->B)", "is_tautology": True},
        {"formula": "((A->B)&(B->C))->(A->C)", "is_tautology": True},
        {"formula": "(!(A&B)~(!A|!B))", "is_tautology": True},
        {"formula": "(!(A|B)~(!A&!B))", "is_tautology": True},
        {"formula": "(A->(B->(A&B)))", "is_tautology": True},
        {"formula": "((A&B)->A)", "is_tautology": True},
    ]

    correct = 0
    print("\nРежим тестирования знаний. Вам будут показаны логические формулы.")
    print("Определите, является ли каждая из них тавтологией (общезначимой формулой).")
    print("Вводите '1' если ДА, '0' если НЕТ.\n")

    for i, test in enumerate(test_cases, 1):
        print(f"\nФормула #{i}: {test['formula']}")

        # Проверяем валидность формулы перед использованием
        is_valid, error = validate_formula(test['formula'])
        if not is_valid:
            print(f"Ошибка в тестовом примере: {error}")
            continue

        answer = input("Это тавтология? (1 - да, 0 - нет): ").strip()

        while answer not in ('0', '1'):
            print("Некорректный ввод. Используйте только '1' или '0'.")
            answer = input("Это тавтология? (1 - да, 0 - нет): ").strip()

        user_answer = (answer == '1')
        if user_answer == test['is_tautology']:
            print("Правильно!")
            correct += 1
        else:
            print("Неправильно.", end=' ')
            print(f"Правильный ответ: {'тавтология' if test['is_tautology'] else 'не тавтология'}")

    print(f"\nВы ответили правильно на {correct} из {len(test_cases)} вопросов.")
    print(f"Ваш результат: {correct / len(test_cases) * 100:.1f}%")


def validate_formula(expression):
    """Проверка корректности ввода формулы"""
    # Проверка на пробелы
    if ' ' in expression:
        return False, "Формула не должна содержать пробелы"

    # Проверка на заглавные буквы
    variables = sorted(set(filter(str.isalpha, expression)))
    if not all(v.isupper() for v in variables):
        return False, "Используйте только заглавные буквы латинского алфавита"

    # Проверка на допустимые символы
    allowed_chars = set('ABCDEFGHIJKLMNOPQRSTUVWXYZ&|!()->~')
    if not all(c in allowed_chars for c in expression):
        return False, "Используйте только допустимые символы: A-Z, &, |, !, (, ), ->, ~"

    # Если формула - одна переменная
    if len(expression) == 1 and expression.isalpha():
        return True, ""

    # Проверка, что выражение в скобках
    if not (expression.startswith('(') and expression.endswith(')')):
        return False, "Выражение должно быть в скобках (кроме случая с одной переменной)"

    # Проверка парности скобок
    balance = 0
    for c in expression:
        if c == '(': balance += 1
        if c == ')': balance -= 1
        if balance < 0: return False, "Неправильная расстановка скобок"
    if balance != 0: return False, "Неправильная расстановка скобок"

    # Проверка структуры выражения
    try:
        # Удаляем внешние скобки для анализа
        inner = expression[1:-1]
        if not inner:
            return False, "Пустое выражение в скобках"

        # Проверяем, что есть оператор между переменными
        if inner[0].isalpha() and inner[1].isalpha():
            return False, "Две переменные должны быть разделены оператором"

        # Проверяем корректность вложенных выражений
        if inner.startswith('(') or inner.startswith('!('):
            # Проверяем, что вложенное выражение содержит оператор
            operators = {'&', '|', '->', '~'}
            has_operator = any(op in inner for op in operators)
            if not has_operator:
                return False, "Выражение должно содержать логический оператор"
    except:
        return False, "Некорректная структура формулы"

    return True, ""

def main():
    """Основная функция программы"""
    print("Лабораторная работа №1")
    print("Проверка является ли формула тавтологией\n")

    while True:
        print("\n" + "=" * 50)
        print("Выберите режим работы:")
        print("1 - Анализ формулы")
        print("2 - Тестирование знаний (определение тавтологий)")
        print("3 - Выход")
        choice = input("> ").strip()

        if choice == '1':
            print("\n" + "=" * 50)
            expression = input("Введите логическое выражение (или 'exit' для выхода):\n"
                               "Допустимые операторы: & (И), | (ИЛИ), ! (НЕ), -> (импликация), ~ (эквивалентность)\n"
                               "> ")

            if expression.lower() == 'exit':
                break

            is_valid, error_message = validate_formula(expression)
            if not is_valid:
                print(f"\nОшибка: {error_message}")
                continue

            analyze_formula(expression)
        elif choice == '2':
            user_test()
        elif choice == '3':
            break
        else:
            print("Некорректный выбор. Пожалуйста, введите 1, 2 или 3.")

if __name__ == "__main__":
    main()


