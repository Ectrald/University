from fastapi import FastAPI, HTTPException, Header
from db import queries

app = FastAPI(title="MTC Management API")


# === Авторизация ===
def authorize(role: str, allowed: list):
    """Проверяет, есть ли у роли пользователя доступ к эндпоинту."""
    if role not in allowed:
        raise HTTPException(status_code=403, detail="Недостаточно прав")


@app.post("/login")
def login(data: dict):
    """Аутентификация пользователя."""
    user = queries.authenticate_user(data["login"], data["password"])
    if not user:
        raise HTTPException(status_code=401, detail="Неверный логин или пароль")
    return user


# === Клиенты (для Технолога И ОПЕРАТОРА) ===
@app.get("/clients")
def get_clients(role: str = Header(...)):
    # РАЗРЕШАЕМ ДОСТУП ОПЕРАТОРУ
    authorize(role, ["technologist", "operator"])
    return queries.get_all_clients()

@app.post("/clients")
def add_client(data: dict, role: str = Header(...)):
    authorize(role, ["technologist"])
    queries.add_client(
        data["login"], data["password"], data["full_name"],
        data["phone_number"], data["address"], data["registration_date"]
    )
    return {"status": "ok"}

@app.put("/clients/{client_id}")
def update_client(client_id: int, data: dict, role: str = Header(...)):
    authorize(role, ["technologist"])
    queries.update_client(client_id, data)
    return {"status": "updated"}

@app.delete("/clients/{client_id}")
def delete_client(client_id: int, role: str = Header(...)):
    authorize(role, ["technologist"])
    queries.delete_client(client_id)
    return {"status": "deleted"}


# === Тарифы (для Технолога) ===
@app.get("/tariffs")
def get_tariffs(role: str = Header(...)):
    authorize(role, ["technologist", "operator"])
    return queries.get_all_tariffs()

@app.post("/tariffs")
def add_tariff(data: dict, role: str = Header(...)):
    authorize(role, ["technologist"])
    queries.add_tariff(
        data["provider_id"], data["effective_date"], data["city_name"],
        data["standard_rate"], data["preferential_rate"]
    )
    return {"status": "ok"}

@app.put("/tariffs/{tariff_id}")
def update_tariff(tariff_id: int, data: dict, role: str = Header(...)):
    authorize(role, ["technologist"])
    queries.update_tariff(tariff_id, data)
    return {"status": "updated"}

@app.delete("/tariffs/{tariff_id}")
def delete_tariff(tariff_id: int, role: str = Header(...)):
    authorize(role, ["technologist"])
    queries.delete_tariff(tariff_id)
    return {"status": "deleted"}


# === Звонки (для Оператора и Клиента) ===
@app.get("/calls")
def get_calls(role: str = Header(...), client_id: int = None):
    authorize(role, ["operator", "client", "technologist"])
    if role == "client" and client_id is not None:
        return queries.get_calls_by_client(client_id)
    return queries.get_all_calls()

@app.post("/calls")
def add_call(data: dict, role: str = Header(...)):
    authorize(role, ["operator"])
    queries.add_call(
        data["client_id"], data["tariff_id"],
        data["destination_city"], data["duration_minutes"]
    )
    return {"status": "ok"}

@app.put("/calls/{call_id}/pay")
def pay_for_call(call_id: int, role: str = Header(...)):
    authorize(role, ["client"]) # Только клиент может оплатить свой звонок
    queries.mark_paid(call_id)
    return {"status": "paid"}


# === Отчеты (для Технолога) ===
@app.get("/reports/debtors")
def get_debtors_report(role: str = Header(...)):
    """Отчет по клиентам с задолженностью более 20 дней."""
    authorize(role, ["technologist"])
    return queries.get_debtors()

@app.get("/reports/calls_by_city")
def get_calls_by_city_report(city: str, month: int, year: int, role: str = Header(...)):
    """Отчет по звонкам в выбранный город за месяц с разбивкой по дням."""
    authorize(role, ["technologist"])
    return queries.get_calls_by_city_daily(city, month, year)

@app.get("/reports/tariffs_on_date")
def get_tariffs_on_date_report(report_date: str, role: str = Header(...)):
    """Отчет по тарифам на конкретную дату."""
    authorize(role, ["technologist"])
    return queries.get_tariffs_on_date(report_date)