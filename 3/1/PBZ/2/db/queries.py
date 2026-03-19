import psycopg2
from psycopg2.extras import RealDictCursor

# ==============================
# Создание подключения (Стандартное)
# ==============================
def get_connection():
    conn = psycopg2.connect(
        dbname="mtc_database",
        user="postgres",
        password="1423",
        host="localhost"
    )
    conn.set_client_encoding("UTF8")
    return conn

# ==============================
# Вспомогательные функции
# ==============================
def call_procedure(proc_name, args=()):
    with get_connection() as conn:
        with conn.cursor() as cur:
            query = f"CALL {proc_name}({','.join(['%s'] * len(args))});"
            cur.execute(query, args)
            conn.commit()

def fetch_from_function(func_name, args=()):
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            query = f"SELECT * FROM {func_name}({','.join(['%s'] * len(args))});"
            cur.execute(query, args)
            return cur.fetchall()

# ==============================
# Аутентификация
# ==============================
def authenticate_user(login, password):
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM authenticate_user(%s, %s);", (login, password))
            return cur.fetchone()

# ==============================
# Клиенты
# ==============================
def get_all_clients():
    return fetch_from_function("get_all_clients")

# ОПТИМИЗАЦИЯ: Получение одного клиента по ID пользователя
def get_client_by_user_id(user_id):
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Ищем напрямую в таблице client
            cur.execute("SELECT * FROM client WHERE user_id = %s;", (user_id,))
            return cur.fetchone()

def add_client(login, password, full_name, phone, address, reg_date):
    call_procedure("add_client", (login, password, full_name, phone, address, reg_date))

def update_client(client_id, data):
    args = (
        client_id,
        data["full_name"],
        data["phone_number"],
        data["address"],
        data["registration_date"]
    )
    call_procedure("update_client", args)

def delete_client(client_id):
    call_procedure("delete_client", (client_id,))

# ==============================
# Тарифы
# ==============================
def get_all_tariffs():
    return fetch_from_function("get_all_tariffs")

def add_tariff(provider_id, date, city, std_rate, pref_rate):
    call_procedure("add_tariff", (provider_id, date, city, std_rate, pref_rate))

def update_tariff(tariff_id, data):
    args = (
        tariff_id,
        data["provider_id"],
        data["effective_date"],
        data["city_name"],
        data["standard_rate"],
        data["preferential_rate"]
    )
    call_procedure("update_tariff", args)

def delete_tariff(tariff_id):
    call_procedure("delete_tariff", (tariff_id,))

# ==============================
# Звонки и счета
# ==============================
def get_all_calls():
    return fetch_from_function("get_all_calls")

def get_calls_by_client(client_id):
    return fetch_from_function("get_calls_by_client", (client_id,))

def add_call(phone_number, city, duration, call_date=None):
    if call_date:
        call_procedure("add_call", (phone_number, city, duration, call_date))
    else:
        call_procedure("add_call", (phone_number, city, duration))

def generate_invoice(client_id):
    call_procedure("generate_invoice", (client_id,))

def mark_invoice_paid(invoice_id):
    call_procedure("mark_invoice_paid", (invoice_id,))

# ==============================
# Отчеты
# ==============================
def get_debtors(days_overdue=20):
    return fetch_from_function("get_debtors", (days_overdue,))

def get_calls_by_city_daily(city, month, year):
    return fetch_from_function("get_calls_by_city_daily", (city, month, year))

def get_tariffs_on_date(report_date):
    return fetch_from_function("get_tariffs_on_date", (report_date,))