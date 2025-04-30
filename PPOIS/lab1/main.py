"""
Модель мониторинга финансов 81

Предметная область: отслеживание и анализ финансовых операций.

Важные сущности: банковские счета, транзакции, бюджет, инвестиции, отчеты.

Операции: операция внесения и снятия денег,
операция анализа расходов и доходов,
операция инвестирования и управления портфелем,
операция формирования бюджета,
операция генерации финансовых отчетов.
"""
from typing import Optional
from Save import *
from BankAccount import BankAccount
from Budget import Budget
from Investment import Investment
from Report import Report
from Manager import Manager

def main() -> None:
    manager = load_state()
    while True:
        print("\nФинансовый мониторинг")
        print("1. Управление банковскими счетами")
        print("2. Управление бюджетом")
        print("3. Управление инвестициями")
        print("4. Генерация отчетов")
        print("5. Выход")
        choice = input("Выберите действие: ")

        if choice == "1":
            manage_bank_accounts(manager)
        elif choice == "2":
            manage_budget(manager)
        elif choice == "3":
            manage_investments(manager)
        elif choice == "4":
            generate_reports(manager)
        elif choice == "5":
            save_state(manager)
            break
        else:
            print("Неверный ввод. Попробуйте снова.")

def get_float_input(prompt: str) -> float:
    while True:
        try:
            value = float(input(prompt))
            if value < 0:
                print("Ошибка: Введите неотрицательное значение.")
            else:
                return value
        except ValueError:
            print("Ошибка: Введите числовое значение.")

def get_int_input(prompt: str) -> int:
    while True:
        try:
            value = int(input(prompt))
            if value < 0:
                print("Ошибка: Введите неотрицательное значение.")
            else:
                return value
        except ValueError:
            print("Ошибка: Введите числовое значение.")

def get_non_empty_string_input(prompt: str) -> str:
    while True:
        user_input = input(prompt).strip()
        if not user_input:
            print("Ошибка: Ввод не может быть пустым. Пожалуйста, введите что-нибудь.")
        else:
            return user_input

def choose_bank_account(manager: Manager) -> Optional[BankAccount]:
    if not manager.list_of_bank_accounts:
        print("Нет доступных счетов.")
        return None
    print("\nСписок доступных счетов:")
    for i, acc in enumerate(manager.list_of_bank_accounts, start=1):
        print(f"{i}. ID: {acc.get_id()}, Баланс: {acc.get_balance():.2f}, Статус: {'Активен' if acc.get_state() == 'active' else 'Заморожен'}")
    choice = get_int_input("Выберите номер счета (0 для выхода): ")
    if choice == 0:
        return None
    if 1 <= choice <= len(manager.list_of_bank_accounts):
        return manager.list_of_bank_accounts[choice - 1]
    print("Неверный выбор.")
    return None

def choose_investment(manager: Manager) -> Optional[Investment]:
    if not manager.list_of_investments:
        print("Нет доступных инвестиций.")
        return None
    print("\nСписок доступных инвестиций:")
    for i, inv in enumerate(manager.list_of_investments, start=1):
        print(f"{i}. Тип: {inv.get_type_of_investment()}, Описание: {inv.get_description()}, Кол-во: {inv.get_number_of_units_invested():.2f}, Цена за единицу: {inv.get_unit_price():.2f}")
    choice = get_int_input("Выберите номер инвестиции (0 для выхода): ")
    if choice == 0:
        return None
    if 1 <= choice <= len(manager.list_of_investments):
        return manager.list_of_investments[choice - 1]
    print("Неверный выбор.")
    return None

def manage_bank_accounts(manager: Manager) -> None:
    while True:
        print("\nУправление банковскими счетами")
        print("1. Добавить счет")
        print("2. Пополнить счет")
        print("3. Снять деньги")
        print("4. Просмотреть все счета")
        print("5. Вернуться в главное меню")
        choice = input("Выберите действие: ")

        if choice == "1":
            balance = get_float_input("Введите начальный баланс: ")
            account = BankAccount(balance)
            manager.list_of_bank_accounts.append(account)
            if balance > 0:
                manager.budget.add_income(balance, "Создание нового счета")
            print("Счет добавлен.")
            account.print_details()
        elif choice == "2":
            account = choose_bank_account(manager)
            if account:
                amount = get_float_input("Введите сумму: ")
                account.add_money(amount)
                manager.budget.add_income(amount, "Пополнение счета")
                print("Баланс пополнен и записан в бюджет.")
                account.print_details()
        elif choice == "3":
            account = choose_bank_account(manager)
            if account:
                amount = get_float_input("Введите сумму: ")
                initial_balance = account.get_balance()
                account.withdraw_money(amount)
                if account.get_balance() != initial_balance:  # Withdrawal was successful
                    manager.budget.add_expense(amount, "Снятие денег со счета")
                    print("Деньги сняты и записаны в бюджет.")
                account.print_details()
        elif choice == "4":
            if not manager.list_of_bank_accounts:
                print("Нет доступных счетов.")
            else:
                print("\nВсе банковские счета:")
                for account in manager.list_of_bank_accounts:
                    account.print_details()
                    print("-" * 40)
        elif choice == "5":
            break
        else:
            print("Неверный ввод. Попробуйте снова.")

def manage_budget(manager: Manager) -> None:
    while True:
        print("\nУправление бюджетом")
        print("1. Добавить доход")
        print("2. Добавить расход")
        print("3. Просмотреть бюджет")
        print("4. Вернуться в главное меню")
        choice = input("Выберите действие: ")

        if choice == "1":
            amount = get_float_input("Введите сумму дохода: ")
            description = get_non_empty_string_input("Введите описание: ")
            manager.budget.add_income(amount, description)
            print("Доход добавлен.")
            manager.budget.print_details()
        elif choice == "2":
            amount = get_float_input("Введите сумму расхода: ")
            description = get_non_empty_string_input("Введите описание: ")
            manager.budget.add_expense(amount, description)
            print("Расход добавлен.")
            manager.budget.print_details()
        elif choice == "3":
            manager.budget.print_details()
        elif choice == "4":
            break
        else:
            print("Неверный ввод. Попробуйте снова.")

def manage_investments(manager: Manager) -> None:
    while True:
        print("\nУправление инвестициями")
        print("1. Добавить инвестицию")
        print("2. Продать инвестицию")
        print("3. Просмотреть все инвестиции")
        print("4. Вернуться в главное меню")
        choice = input("Выберите действие: ")

        if choice == "1":
            type_of_investment = get_non_empty_string_input("Введите тип инвестиции: ")
            description = get_non_empty_string_input("Введите описание: ")
            number_of_units = get_float_input("Введите количество единиц: ")
            unit_price = get_float_input("Введите цену за единицу: ")
            account = choose_bank_account(manager)
            if account:
                total_cost = number_of_units * unit_price
                initial_balance = account.get_balance()
                account.withdraw_money(total_cost)
                if account.get_balance() != initial_balance:  # Withdrawal was successful
                    manager.budget.add_expense(total_cost, f"Инвестиция: {description}")
                    investment = Investment(type_of_investment, description, number_of_units, unit_price, account.get_id())
                    manager.list_of_investments.append(investment)
                    print("Инвестиция добавлена и записана в бюджет.")
                    investment.print_details()
                else:
                    print("Недостаточно средств на выбранном счете.")
        elif choice == "2":
            investment = choose_investment(manager)
            if investment:
                max_units = investment.get_number_of_units_invested()
                units_to_sell = get_float_input(f"Введите количество единиц для продажи (макс. {max_units:.2f}): ")
                if units_to_sell > max_units or units_to_sell <= 0:
                    print("Ошибка: Неверное количество единиц.")
                    continue
                # Найти счет по ID
                account = next((acc for acc in manager.list_of_bank_accounts if acc.get_id() == investment.get_account_id()), None)
                if not account:
                    print("Ошибка: Счет, связанный с инвестицией, не найден.")
                    continue
                sale_amount = units_to_sell * investment.get_unit_price()
                account.add_money(sale_amount)
                manager.budget.add_income(sale_amount, f"Продажа инвестиции: {investment.get_description()}")
                if units_to_sell == max_units:
                    manager.list_of_investments.remove(investment)
                    print("Инвестиция полностью продана и удалена.")
                else:
                    investment.set_number_of_units_invested(max_units - units_to_sell)
                    print("Инвестиция частично продана.")
                account.print_details()
        elif choice == "3":
            if not manager.list_of_investments:
                print("Нет доступных инвестиций.")
            else:
                print("\nВсе инвестиции:")
                for investment in manager.list_of_investments:
                    investment.print_details()
                    print("-" * 40)
        elif choice == "4":
            break
        else:
            print("Неверный ввод. Попробуйте снова.")

def generate_reports(manager: Manager) -> None:
    print("\nФинансовые отчёты")
    report = Report(manager.budget)
    report.print_report()

if __name__ == "__main__":
    main()