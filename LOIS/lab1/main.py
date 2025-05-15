"""
Лабораторная работа №1 по логическим основам интеллектуальных систем
Тема: Программирование операций обработки и преобразований формул языка логики высказываний
Вариант 2: Проверка является ли формула общезначимой (тавтологией)
Автор: Германенко Владислав Вадимович
Группа: 321701
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


def main():
    """Основная функция программы"""
    print("Лабораторная работа №1")
    print("Проверка является ли формула тавтологией\n")

    while True:
        print("\n" + "=" * 50)
        expression = input("Введите логическое выражение (или 'exit' для выхода):\n"
                           "Допустимые операторы: & (И), | (ИЛИ), ! (НЕ), -> (импликация), ~ (эквивалентность)\n"
                           "Пример: (a -> b) & (!b -> !a)\n> ")

        if expression.lower() == 'exit':
            break

        try:
            analyze_formula(expression)
        except Exception as e:
            print(f"\nОшибка при анализе формулы: {e}")
            print("Проверьте правильность ввода формулы")


if __name__ == "__main__":
    main()