class Transaction:
    def __init__(self, status: str, amount: float, description: str) -> None:
        self._status = status
        self._amount = amount
        self._description = description

    def __str__(self) -> str:
        status_str = "Доход" if self._status == 'income' else "Расход"
        return f"{status_str}: {self._amount:.2f} ({self._description})"

    def print_details(self) -> None:
        print(self)

    def get_status(self) -> str:
        return self._status

    def get_amount(self) -> float:
        return self._amount

    def get_description(self) -> str:
        return self._description