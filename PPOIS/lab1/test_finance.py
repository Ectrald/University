import unittest
from BankAccount import BankAccount
from Budget import Budget
from Investment import Investment
from Transaction import Transaction
from Manager import Manager

class TestBankAccount(unittest.TestCase):
    def setUp(self):
        self.account = BankAccount(1000)

    def test_initial_balance(self):
        self.assertEqual(self.account.get_balance(), 1000)

    def test_add_money(self):
        self.account.add_money(500)
        self.assertEqual(self.account.get_balance(), 1500)

    def test_withdraw_money(self):
        self.account.withdraw_money(300)
        self.assertEqual(self.account.get_balance(), 700)

    def test_withdraw_money_insufficient_funds(self):
        self.account.withdraw_money(1500)
        self.assertEqual(self.account.get_balance(), -500)
        self.assertEqual(self.account.get_state(), 'frozen')

class TestBudget(unittest.TestCase):
    def setUp(self):
        self.budget = Budget()

    def test_add_income(self):
        self.budget.add_income(500, "Зарплата")
        self.assertEqual(self.budget.get_income(), 500)
        self.assertEqual(len(self.budget.get_transactions()), 1)

    def test_add_expense(self):
        self.budget.add_expense(200, "Покупка продуктов")
        self.assertEqual(self.budget.get_expenses(), 200)
        self.assertEqual(len(self.budget.get_transactions()), 1)

    def test_analyze(self):
        self.budget.add_income(500, "Зарплата")
        self.budget.add_expense(200, "Покупка продуктов")
        self.assertEqual(self.budget.get_income() - self.budget.get_expenses(), 300)

class TestInvestment(unittest.TestCase):
    def setUp(self):
        self.investment = Investment("акции", "Покупка акций Apple", 10, 150, "test-account-id")

    def test_investment_initialization(self):
        self.assertEqual(self.investment.get_type_of_investment(), "акции")
        self.assertEqual(self.investment.get_description(), "Покупка акций Apple")
        self.assertEqual(self.investment.get_number_of_units_invested(), 10)
        self.assertEqual(self.investment.get_unit_price(), 150)
        self.assertEqual(self.investment.get_account_id(), "test-account-id")

class TestTransaction(unittest.TestCase):
    def setUp(self):
        self.transaction = Transaction("income", 500, "Зарплата")

    def test_transaction_initialization(self):
        self.assertEqual(self.transaction.get_status(), "income")
        self.assertEqual(self.transaction.get_amount(), 500)
        self.assertEqual(self.transaction.get_description(), "Зарплата")

class TestManager(unittest.TestCase):
    def setUp(self):
        self.manager = Manager()

    def test_add_bank_account(self):
        account = BankAccount(1000)
        self.manager.list_of_bank_accounts.append(account)
        self.assertEqual(len(self.manager.list_of_bank_accounts), 1)

    def test_add_investment(self):
        investment = Investment("акции", "Покупка акций Apple", 10, 150, "test-account-id")
        self.manager.list_of_investments.append(investment)
        self.assertEqual(len(self.manager.list_of_investments), 1)

    def test_budget_operations(self):
        self.manager.budget.add_income(500, "Зарплата")
        self.manager.budget.add_expense(200, "Покупка продуктов")
        self.assertEqual(self.manager.budget.get_income(), 500)
        self.assertEqual(self.manager.budget.get_expenses(), 200)

if __name__ == "__main__":
    unittest.main()