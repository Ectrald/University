from fastapi import FastAPI, HTTPException, Header
from db import queries

app = FastAPI(title="MTC Management API")


# ============================================================
# Авторизация
# ============================================================
def authorize(role: str, allowed: list):
    """Проверяет, есть ли у роли пользователя доступ к эндпоинту."""
    if role not in allowed:
        raise HTTPException(status_code=403, detail="Недостаточно прав")


# ============================================================
# ЛОГИН
# ============================================================
@app.post("/login")
def login(data: dict):
    """Аутентификация пользователя."""
    user = queries.authenticate_user(data["login"], data["password"])
    if not user:
        raise HTTPException(status_code=401, detail="Неверный логин или пароль")
    return user


# ============================================================
# КЛИЕНТЫ
# ============================================================
@app.get("/clients")
def get_clients(role: str = Header(...)):
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


# ============================================================
# ТАРИФЫ
# ============================================================
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


# ============================================================
# ЗВОНКИ
# ============================================================
@app.get("/calls")
def get_calls(role: str = Header(...), user_id: int = None):
    """
    Клиент видит свои звонки. Технолог и оператор видят всё.
    """
    authorize(role, ["operator", "client", "technologist"])

    if role == "client":
        if user_id is None:
            raise HTTPException(status_code=400, detail="Для клиента нужен user_id")

        # ОПТИМИЗАЦИЯ: Быстрый поиск клиента
        client = queries.get_client_by_user_id(user_id)
        if not client:
            raise HTTPException(status_code=404, detail="Клиент не найден")

        return queries.get_calls_by_client(client["client_id"])

    return queries.get_all_calls()


@app.post("/calls")
def add_call(data: dict, role: str = Header(...)):
    authorize(role, ["operator"])
    queries.add_call(
        data["phone_number"],
        data["destination_city"],
        data["duration_minutes"],
        data.get("call_date")
    )
    return {"status": "ok"}


# ============================================================
# СЧЕТА / КВИТАНЦИИ
# ============================================================
@app.post("/invoices/generate")
def generate_invoice(data: dict, role: str = Header(...)):
    authorize(role, ["operator"])
    queries.generate_invoice(data["client_id"])
    return {"status": "invoice_generated"}


@app.put("/invoices/{invoice_id}/pay")
def pay_invoice(invoice_id: int, role: str = Header(...), user_id: int = None):
    authorize(role, ["client", "operator"])

    if role == "client":
        if user_id is None:
            raise HTTPException(status_code=400, detail="User ID required")

        # ОПТИМИЗАЦИЯ: Быстрый поиск клиента
        client = queries.get_client_by_user_id(user_id)
        if not client:
            raise HTTPException(status_code=404, detail="Клиент не найден")

        # Проверяем, принадлежит ли счет этому клиенту
        client_calls = queries.get_calls_by_client(client["client_id"])

        # Собираем ID счетов клиента
        client_invoice_ids = {c["invoice_id"] for c in client_calls if c["invoice_id"] is not None}

        if invoice_id not in client_invoice_ids:
            raise HTTPException(status_code=403, detail="Вы не можете оплачивать чужой счет")

    queries.mark_invoice_paid(invoice_id)
    return {"status": "paid"}


# ============================================================
# ОТЧЕТЫ
# ============================================================
@app.get("/reports/debtors")
def get_debtors_report(role: str = Header(...)):
    authorize(role, ["technologist"])
    return queries.get_debtors()


@app.get("/reports/calls_by_city")
def get_calls_by_city_report(city: str, month: int, year: int, role: str = Header(...)):
    authorize(role, ["technologist"])
    return queries.get_calls_by_city_daily(city, month, year)


@app.get("/reports/tariffs_on_date")
def get_tariffs_on_date_report(report_date: str, role: str = Header(...)):
    authorize(role, ["technologist", "operator"])
    return queries.get_tariffs_on_date(report_date)