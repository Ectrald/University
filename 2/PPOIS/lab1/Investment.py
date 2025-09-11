class Investment:
    def __init__(self, type_of_investment: str, description: str, number_of_units_invested: float, unit_price: float, account_id: str) -> None:
        self._type_of_investment = type_of_investment
        self._unit_price = unit_price
        self._number_of_units_invested = number_of_units_invested
        self._description = description
        self._account_id = account_id

    def get_type_of_investment(self) -> str:
        return self._type_of_investment

    def get_description(self) -> str:
        return self._description

    def get_number_of_units_invested(self) -> float:
        return self._number_of_units_invested

    def set_number_of_units_invested(self, number: float) -> None:
        self._number_of_units_invested = number

    def get_unit_price(self) -> float:
        return self._unit_price

    def get_account_id(self) -> str:
        return self._account_id

    def __str__(self) -> str:
        total_value = self._number_of_units_invested * self._unit_price
        return (f"Тип инвестиции: {self._type_of_investment}\n"
                f"Описание: {self._description}\n"
                f"Количество единиц: {self._number_of_units_invested:.2f}\n"
                f"Цена за единицу: {self._unit_price:.2f}\n"
                f"Общая стоимость: {total_value:.2f}\n"
                f"ID счета: {self._account_id}")

    def print_details(self) -> None:
        print(self)