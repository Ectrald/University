import Budget

class Report:
    def __init__(self, budget: Budget):
        self.budget = budget

    def generate_income_report(self) -> str:
        report = f"--- Отчет о доходе ---\n"
        report += f"Общий доход: {self.budget.get_income():.2f}\n"
        report += "Транзакции:\n"
        for transaction in self.budget.get_transactions():
            if transaction.get_status() == 'income':
                report += f"- {transaction.get_description()}: {transaction.get_amount():.2f}\n"
        return report

    def generate_expense_report(self) -> str:
        report = f"--- Отчет о расходе ---\n"
        report += f"Общий расход: {self.budget.get_expenses():.2f}\n"
        report += "Транзакции:\n"
        for transaction in self.budget.get_transactions():
            if transaction.get_status() == 'expense':
                report += f"- {transaction.get_description()}: {transaction.get_amount():.2f}\n"
        return report

    def generate_net_profit_report(self) -> str:
        net_profit = self.budget.get_income() - self.budget.get_expenses()
        report = f"--- Отчет о прибыли ---\n"
        report += f"Чистая прибыль: {net_profit:.2f}\n"
        return report

    def print_report(self) -> None:
        print(self.generate_income_report())
        print(self.generate_expense_report())
        print(self.generate_net_profit_report())