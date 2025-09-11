from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from manager import Manager
from save import load_state, save_state
from bank_account import BankAccount
from budget import Budget
from investment import Investment
import uvicorn

app = FastAPI(
    title="Финансовый мониторинг",
    description="Система для отслеживания и анализа финансовых операций",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Загружаем состояние при старте
manager = load_state()


# Модели Pydantic для запросов и ответов
class BankAccountCreate(BaseModel):
    balance: float


class TransactionRequest(BaseModel):
    amount: float
    description: str = ""


class InvestmentCreate(BaseModel):
    type_of_investment: str
    description: str
    number_of_units: float
    unit_price: float
    account_id: str


class InvestmentSell(BaseModel):
    units_to_sell: float


@app.on_event("shutdown")
def shutdown_event():
    save_state(manager)


# Корневой endpoint
@app.get("/", summary="Главная страница API")
def read_root():
    return {
        "message": "Добро пожаловать в систему финансового мониторинга",
        "endpoints": {
            "accounts": "/accounts",
            "budget": "/budget",
            "investments": "/investments",
            "reports": "/reports",
            "docs": "/docs",
            "redoc": "/redoc"
        }
    }


# Банковские счета
@app.get("/accounts", summary="Получить список всех счетов")
def get_all_accounts():
    return [{
        "id": acc.get_id(),
        "balance": acc.get_balance(),
        "state": acc.get_state()
    } for acc in manager.list_of_bank_accounts]


@app.post("/accounts", summary="Создать новый счет")
def create_account(account: BankAccountCreate):
    try:
        new_account = BankAccount(account.balance)
        manager.list_of_bank_accounts.append(new_account)
        if account.balance > 0:
            manager.budget.add_income(account.balance, "Создание нового счета")
        return {
            "id": new_account.get_id(),
            "balance": new_account.get_balance(),
            "state": new_account.get_state()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/accounts/{account_id}/deposit", summary="Пополнить счет")
def deposit_to_account(account_id: str, transaction: TransactionRequest):
    account = next((acc for acc in manager.list_of_bank_accounts if acc.get_id() == account_id), None)
    if not account:
        raise HTTPException(status_code=404, detail="Счет не найден")

    try:
        account.add_money(transaction.amount)
        manager.budget.add_income(transaction.amount, transaction.description)
        return {"message": "Счет успешно пополнен", "new_balance": account.get_balance()}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/accounts/{account_id}/withdraw", summary="Снять деньги со счета")
def withdraw_from_account(account_id: str, transaction: TransactionRequest):
    account = next((acc for acc in manager.list_of_bank_accounts if acc.get_id() == account_id), None)
    if not account:
        raise HTTPException(status_code=404, detail="Счет не найден")

    try:
        initial_balance = account.get_balance()
        account.withdraw_money(transaction.amount)
        if account.get_balance() != initial_balance:
            manager.budget.add_expense(transaction.amount, transaction.description)
            return {"message": "Деньги успешно сняты", "new_balance": account.get_balance()}
        return {"message": "Снятие не выполнено", "balance": account.get_balance()}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Бюджет
@app.get("/budget", summary="Получить текущее состояние бюджета")
def get_budget():
    return {
        "income": manager.budget.get_income(),
        "expenses": manager.budget.get_expenses(),
        "state": manager.budget.state,
        "transactions": [
            {
                "type": "income" if t.get_status() == "income" else "expense",
                "amount": t.get_amount(),
                "description": t.get_description()
            } for t in manager.budget.get_transactions()
        ]
    }


@app.post("/budget/income", summary="Добавить доход")
def add_income(transaction: TransactionRequest):
    try:
        manager.budget.add_income(transaction.amount, transaction.description)
        return {"message": "Доход добавлен"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/budget/expense", summary="Добавить расход")
def add_expense(transaction: TransactionRequest):
    try:
        manager.budget.add_expense(transaction.amount, transaction.description)
        return {"message": "Расход добавлен"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Инвестиции
@app.get("/investments", summary="Получить список всех инвестиций")
def get_all_investments():
    return [{
        "id": idx,
        "type": inv.get_type_of_investment(),
        "description": inv.get_description(),
        "units": inv.get_number_of_units_invested(),
        "unit_price": inv.get_unit_price(),
        "account_id": inv.get_account_id(),
        "total_value": inv.get_number_of_units_invested() * inv.get_unit_price()
    } for idx, inv in enumerate(manager.list_of_investments)]


@app.post("/investments", summary="Добавить новую инвестицию")
def create_investment(investment: InvestmentCreate):
    account = next((acc for acc in manager.list_of_bank_accounts if acc.get_id() == investment.account_id), None)
    if not account:
        raise HTTPException(status_code=404, detail={"error": "Счет не найден"})

    try:
        total_cost = investment.number_of_units * investment.unit_price

        # Проверяем достаточно ли средств на счете
        if account.get_balance() < total_cost:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Недостаточно средств на счете",
                    "available": account.get_balance(),
                    "required": total_cost
                }
            )

        # Списываем средства
        account.withdraw_money(total_cost)

        # Добавляем запись о расходе
        manager.budget.add_expense(total_cost, f"Инвестиция: {investment.description}")

        # Создаем инвестицию
        new_investment = Investment(
            investment.type_of_investment,
            investment.description,
            investment.number_of_units,
            investment.unit_price,
            investment.account_id
        )
        manager.list_of_investments.append(new_investment)

        return {
            "message": "Инвестиция добавлена",
            "investment": {
                "id": len(manager.list_of_investments) - 1,
                "type": new_investment.get_type_of_investment(),
                "description": new_investment.get_description(),
                "units": new_investment.get_number_of_units_invested(),
                "unit_price": new_investment.get_unit_price(),
                "account_id": new_investment.get_account_id(),
                "total_value": new_investment.get_number_of_units_invested() * new_investment.get_unit_price()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail={"error": str(e)})


@app.post("/investments/{investment_id}/sell", summary="Продать часть инвестиции")
def sell_investment(investment_id: int, sell: InvestmentSell):
    if investment_id < 0 or investment_id >= len(manager.list_of_investments):
        raise HTTPException(status_code=404, detail="Инвестиция не найдена")

    investment = manager.list_of_investments[investment_id]
    max_units = investment.get_number_of_units_invested()

    if sell.units_to_sell > max_units or sell.units_to_sell <= 0:
        raise HTTPException(status_code=400, detail="Неверное количество единиц")

    account = next((acc for acc in manager.list_of_bank_accounts if acc.get_id() == investment.get_account_id()), None)
    if not account:
        raise HTTPException(status_code=404, detail="Счет не найден")

    sale_amount = sell.units_to_sell * investment.get_unit_price()
    account.add_money(sale_amount)
    manager.budget.add_income(sale_amount, f"Продажа инвестиции: {investment.get_description()}")

    if sell.units_to_sell == max_units:
        manager.list_of_investments.pop(investment_id)
        return {"message": "Инвестиция полностью продана"}
    else:
        investment.set_number_of_units_invested(max_units - sell.units_to_sell)
        return {
            "message": "Часть инвестиции продана",
            "remaining_units": max_units - sell.units_to_sell,
            "sold_amount": sale_amount
        }


# Отчеты
@app.get("/reports/income", summary="Отчет о доходах")
def get_income_report():
    income = manager.budget.get_income()
    transactions = [
        {"amount": t.get_amount(), "description": t.get_description()}
        for t in manager.budget.get_transactions() if t.get_status() == 'income'
    ]
    return {"total_income": income, "transactions": transactions}


@app.get("/reports/expense", summary="Отчет о расходах")
def get_expense_report():
    expenses = manager.budget.get_expenses()
    transactions = [
        {"amount": t.get_amount(), "description": t.get_description()}
        for t in manager.budget.get_transactions() if t.get_status() == 'expense'
    ]
    return {"total_expenses": expenses, "transactions": transactions}


@app.get("/reports/profit", summary="Отчет о прибыли")
def get_profit_report():
    profit = manager.budget.get_income() - manager.budget.get_expenses()
    return {"net_profit": profit}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)