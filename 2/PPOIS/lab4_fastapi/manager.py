from report import *
from bank_account import BankAccount
from budget import Budget
from investment import Investment
from report import Report
class Manager:
    def __init__(self):
        self.list_of_investments = []
        self.list_of_bank_accounts = []
        self.budget = Budget()
        self.list_of_reports = []
