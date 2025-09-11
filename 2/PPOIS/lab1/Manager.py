from BankAccount import *
from Budget import *
from Investment import *
from Report import *
class Manager:
    def __init__(self):
        self.list_of_investments = []
        self.list_of_bank_accounts = []
        self.budget = Budget.Budget()
        self.list_of_reports = []
