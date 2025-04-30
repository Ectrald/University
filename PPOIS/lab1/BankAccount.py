import uuid
from transitions import Machine
class BankAccount:
    states = ['active', 'frozen']
    def __init__(self, balance: float )-> None:
        self.__id = str(uuid.uuid4())
        self._balance = balance
        # Инициализация FSM
        self.machine = Machine(
            model=self,
            states=BankAccount.states,
            initial='active' if balance >= 0 else 'frozen'
        )
        self.machine.add_transition(
            trigger='check_balance',
            source='active',
            dest='frozen',
            conditions=['is_negative_balance']
        )
        self.machine.add_transition(
            trigger='check_balance',
            source='frozen',
            dest='active',
            conditions=['is_positive_balance']
        )

    def is_negative_balance(self) -> bool:
        return self._balance < 0

    def is_positive_balance(self) -> bool:
        return self._balance >= 0
    def add_money(self, money: float) -> None:
        if money <= 0:
            raise ValueError("Сумма пополнения должна быть положительной.")
        self._balance += money
        self.check_balance()
    def withdraw_money(self, money: float) -> None:
        if money <= 0:
            raise ValueError("Сумма снятия должна быть положительной.")
        if self.state == 'active':
            new_balance = self._balance - money
            if new_balance < -1000:
                print(f"Ошибка: Снятие {money:.2f} приведет к высокой задолженности(максимальная задолженность - 1000). Текущий баланс: {self._balance:.2f}")
                return
            self._balance = new_balance
        else:
            print("Ваш банковский аккаунт заморожен. Устраните задолженность для активации")
            print(f"Баланс: {self._balance:.2f}")
        self.check_balance()

    def __str__(self)-> str:
        status = "Активен" if self.state == 'active' else "Заморожен"
        return (f"Банковский счет [ID: {self.get_id()}]\n"
                f"Баланс: {self.get_balance():.2f}\n"
                f"Статус: {status}")

    def print_details(self) -> None:
        print(self)
    def get_id(self)-> str:
        return self.__id
    def get_balance(self)-> float:
        return self._balance

    def get_state(self) -> str:
        return self.state