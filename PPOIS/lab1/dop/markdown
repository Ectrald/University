# Документация программной системы для мониторинга финансов

## Описание системы

Программная система предназначена для отслеживания и анализа финансовых операций. Она включает управление банковскими счетами, бюджетирование, инвестиции и генерацию финансовых отчетов.

## Основные сущности

1. **BankAccount** - представляет банковский счет с возможностью пополнения и снятия средств.
2. **Budget** - управляет доходами и расходами, а также анализирует финансовое состояние.
3. **Investment** - описывает инвестиции, такие как акции, криптовалюта или ценные металлы.
4. **Transaction** - представляет финансовую операцию (доход или расход).
5. **Report** - генерирует отчеты о доходах, расходах и чистой прибыли.
6. **Manager** - центральный класс, управляющий всеми компонентами системы.

## Диаграмма классов

```plantuml
@startuml
' Настройки отображения
hide empty members
skinparam classAttributeIconSize 0

' Классы и их атрибуты/методы
class BankAccount {
  - __id: str
  - _balance: float
  - state: str
  + is_negative_balance(): bool
  + is_positive_balance(): bool
  + add_money(money: float): void
  + withdraw_money(money: float): void
  + get_id(): str
  + get_balance(): float
  + get_state(): str
}

class Budget {
  - _income: float
  - _expenses: float
  - transactions: List<Transaction>
  - state: str
  + add_income(amount: float, description: str): void
  + add_expense(amount: float, description: str): void
  + get_income(): float
  + get_expenses(): float
  + get_transactions(): List<Transaction>
  + is_deficit(): bool
  + is_balanced(): bool
}

class Transaction {
  - _status: str
  - _amount: float
  - _description: str
  + get_status(): str
  + get_amount(): float
  + get_description(): str
}

class Investment {
  - _type_of_investment: str
  - _unit_price: float
  - _number_of_units_invested: float
  - _description: str
  - _account_id: str
  + get_type_of_investment(): str
  + get_description(): str
  + get_number_of_units_invested(): float
  + set_number_of_units_invested(number: float): void
  + get_unit_price(): float
  + get_account_id(): str
}

class Report {
  - budget: Budget
  + generate_income_report(): str
  + generate_expense_report(): str
  + generate_net_profit_report(): str
  + print_report(): void
}

class Manager {
  - list_of_investments: List<Investment>
  - list_of_bank_accounts: List<BankAccount>
  - budget: Budget
  - list_of_reports: List<Report>
}

' Связи между классами
Manager "1" *-- "0..*" BankAccount
Manager "1" *-- "1" Budget
Manager "1" *-- "0..*" Investment
Manager "1" *-- "0..*" Report

Budget "1" *-- "0..*" Transaction
Report "1" --> "1" Budget
Investment "1" --> "1" BankAccount

' Наследование (если есть)
' MachineState <|-- BankAccount
' MachineState <|-- Budget

@enduml
```
## Диаграмма состояний
```plantuml
@startuml

[*] --> BankAccount
state BankAccount {
  [*] --> active: balance >= 0
  [*] --> frozen: balance < 0

  active --> frozen: check_balance\n[is_negative_balance()]
  frozen --> active: check_balance\n[is_positive_balance()]
}

[*] --> Budget
state Budget {
  [*] --> BALANCED: income >= expenses
  [*] --> DEFICIT: expenses > income

  BALANCED --> DEFICIT: update\n[is_deficit()]
  DEFICIT --> BALANCED: update\n[is_balanced()]
}

@enduml
```

## Основные функции системы

### Управление банковскими счетами
- **Добавление счета**: Создание нового банковского счета с начальным балансом.
- **Пополнение счета**: Добавление средств на выбранный счет.
- **Снятие средств**: Снятие денег с выбранного счета.

### Управление бюджетом
- **Добавление дохода**: Регистрация дохода с указанием суммы и описания.
- **Добавление расхода**: Регистрация расхода с указанием суммы и описания.
- **Анализ бюджета**: Расчет чистой прибыли (доходы минус расходы).

### Управление инвестициями
- **Добавление инвестиции**: Регистрация новой инвестиции с указанием типа, количества единиц и цены за единицу.
- **Списание средств**: Автоматическое списание средств с выбранного счета при добавлении инвестиции.

### Генерация отчетов
- **Отчет о доходах**: Список всех доходов с указанием суммы и описания.
- **Отчет о расходах**: Список всех расходов с указанием суммы и описания.
- **Отчет о чистой прибыли**: Расчет и отображение чистой прибыли.
