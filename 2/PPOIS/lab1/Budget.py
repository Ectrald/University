from Transaction import Transaction
from transitions import Machine
class Budget:

    states = ['BALANCED', 'DEFICIT']

    def __init__(self)-> None:
        self._income = 0.0
        self._expenses = 0.0
        self.transactions = []

        self.machine = Machine(
            model=self,
            states=Budget.states,
            initial='BALANCED'
        )

        self.machine.add_transition(
            'update',
            'BALANCED',
            'DEFICIT',
            conditions=['is_deficit']
        )

        self.machine.add_transition(
            'update',
            'DEFICIT',
            'BALANCED',
            conditions=['is_balanced']
        )

    def is_deficit(self) -> bool:
        return self._expenses > self._income

    def is_balanced(self) -> bool:
        return self._income >= self._expenses

    def add_income(self, amount: float, description: str = "")-> None:
        if amount < 0:
            raise ValueError("Сумма дохода должна быть положительной.")
        self._income += amount
        self.transactions.append(Transaction('income', amount, description))
        self.update()

    def add_expense(self, amount: float, description: str = "")-> None:
        if amount < 0:
            raise ValueError("Сумма расхода должна быть положительной.")
        self._expenses += amount
        self.transactions.append(Transaction('expense', amount, description))
        self.update()

    def analyze(self)-> None:
        net_profit = self._income - self._expenses
        print(f"Чистая прибыль: {net_profit:.2f}")

    def __str__(self) -> str:
        report = f"Бюджет:\n"
        report += f"Доход: {self._income:.2f}\n"
        report += f"Расходы: {self._expenses:.2f}\n"
        report += f"Статус: {'Сбалансирован' if self.state == 'BALANCED' else 'Дефицит'}\n"
        report += "Транзакции:\n"
        if not self.transactions:
            report += "  Нет транзакций.\n"
        else:
            for i, transaction in enumerate(self.transactions, 1):
                report += f"  {i}. {transaction.__str__()}\n"
        return report

    def print_details(self) -> None:
        print(self)

    def get_income(self) -> float:
        return self._income

    def get_expenses(self) -> float:
        return self._expenses

    def get_transactions(self) -> list:
        return self.transactions
