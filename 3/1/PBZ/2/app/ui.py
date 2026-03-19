import streamlit as st
import requests
import pandas as pd
from datetime import date, datetime

# ==========================================
# КОНФИГУРАЦИЯ
# ==========================================
API_URL = "http://localhost:8000"
st.set_page_config(
    page_title="МТС: Система управления",
    page_icon="📞",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Инициализация сессии
if "user" not in st.session_state:
    st.session_state["user"] = None


# ==========================================
# API КЛИЕНТ
# ==========================================
def get_headers():
    """Возвращает заголовки с ролью текущего пользователя"""
    if st.session_state["user"]:
        return {"role": st.session_state["user"]["role"]}
    return {}


def api_request(method, endpoint, **kwargs):
    """Универсальная функция для запросов к API с обработкой ошибок"""
    url = f"{API_URL}{endpoint}"
    headers = get_headers()

    try:
        if method == "GET":
            response = requests.get(url, headers=headers, **kwargs)
        elif method == "POST":
            response = requests.post(url, headers=headers, **kwargs)
        elif method == "PUT":
            response = requests.put(url, headers=headers, **kwargs)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers, **kwargs)

        if not response.ok:
            error_detail = response.json().get("detail", "Неизвестная ошибка")
            st.error(f"Ошибка API: {error_detail}")
            return None

        return response.json()
    except requests.exceptions.ConnectionError:
        st.error("🔴 Нет соединения с сервером. Убедитесь, что main.py запущен.")
        return None


# ==========================================
# ЭКРАН АВТОРИЗАЦИИ
# ==========================================
def render_login():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("📞 Вход в систему МТС")
        with st.form("login_form"):
            login = st.text_input("Логин")
            password = st.text_input("Пароль", type="password")
            submit = st.form_submit_button("Войти", use_container_width=True)

            if submit:
                # Прямой запрос без get_headers, т.к. мы еще не авторизованы
                try:
                    r = requests.post(f"{API_URL}/login", json={"login": login, "password": password})
                    if r.ok:
                        st.session_state["user"] = r.json()
                        st.rerun()
                    else:
                        st.error("Неверный логин или пароль")
                except Exception:
                    st.error("Сервер недоступен")


def logout():
    st.session_state["user"] = None
    st.rerun()


# ==========================================
# ИНТЕРФЕЙС ТЕХНОЛОГА
# ==========================================
def render_technologist_ui():
    st.title("🛠 Панель Технолога")

    tab_clients, tab_tariffs, tab_reports = st.tabs([
        "👥 Управление клиентами",
        "💰 Управление тарифами",
        "📊 Отчеты и аналитика"
    ])

    # --- ВКЛАДКА КЛИЕНТЫ ---
    with tab_clients:
        col_act, col_view = st.columns([1, 2])

        with col_act:
            st.subheader("Действия")
            with st.expander("➕ Добавить нового клиента", expanded=False):
                with st.form("add_client_form"):
                    f_login = st.text_input("Логин для входа")
                    f_pass = st.text_input("Пароль", type="password")
                    f_name = st.text_input("ФИО")
                    f_phone = st.text_input("Телефон")
                    f_addr = st.text_input("Адрес")
                    if st.form_submit_button("Создать клиента"):
                        data = {
                            "login": f_login, "password": f_pass,
                            "full_name": f_name, "phone_number": f_phone,
                            "address": f_addr, "registration_date": date.today().isoformat()
                        }
                        if api_request("POST", "/clients", json=data):
                            st.success("Клиент успешно создан")
                            st.rerun()  # Обновить таблицу

            with st.expander("✏️ Редактировать данные", expanded=False):
                clients_data = api_request("GET", "/clients")
                if clients_data:
                    df_c = pd.DataFrame(clients_data)
                    client_id_to_edit = st.selectbox("Выберите клиента", df_c["client_id"].tolist(),
                                                     format_func=lambda x: f"ID {x}")

                    # Получаем текущие данные выбранного клиента
                    current_client = df_c[df_c["client_id"] == client_id_to_edit].iloc[0]

                    with st.form("edit_client_form"):
                        e_name = st.text_input("ФИО", value=current_client["full_name"])
                        e_phone = st.text_input("Телефон", value=current_client["phone_number"])
                        e_addr = st.text_input("Адрес", value=current_client["address"])
                        e_date = st.date_input("Дата регистрации",
                                               value=datetime.fromisoformat(str(current_client["registration_date"])))

                        if st.form_submit_button("Сохранить изменения"):
                            upd_data = {
                                "full_name": e_name, "phone_number": e_phone,
                                "address": e_addr, "registration_date": e_date.isoformat()
                            }
                            if api_request("PUT", f"/clients/{client_id_to_edit}", json=upd_data):
                                st.success("Данные обновлены")
                                st.rerun()

        with col_view:
            st.subheader("Список клиентов")
            clients = api_request("GET", "/clients")
            if clients:
                df = pd.DataFrame(clients)
                st.dataframe(
                    df[["client_id", "full_name", "phone_number", "address", "registration_date"]],
                    use_container_width=True,
                    hide_index=True
                )

                # Удаление
                st.write("---")
                del_col1, del_col2 = st.columns([3, 1])
                del_id = del_col1.selectbox("ID для удаления", df["client_id"], label_visibility="collapsed")
                if del_col2.button("🗑 Удалить"):
                    if api_request("DELETE", f"/clients/{del_id}"):
                        st.warning(f"Клиент {del_id} удален")
                        st.rerun()

    # --- ВКЛАДКА ТАРИФЫ ---
    with tab_tariffs:
        st.info("Здесь управляется стоимость звонков по городам и времени.")

        tariffs = api_request("GET", "/tariffs")
        if tariffs:
            df_t = pd.DataFrame(tariffs)
            st.dataframe(df_t, use_container_width=True)
        else:
            df_t = pd.DataFrame()

        col_add, col_edit = st.columns(2)

        with col_add:
            with st.form("add_tariff_form"):
                st.write("📖 **Добавить тариф**")
                prov_id = st.number_input("ID Провайдера", min_value=1, value=1)
                eff_date = st.date_input("Дата вступления в силу")
                city_name = st.text_input("Город назначения")
                std_rate = st.number_input("Стандартная цена (руб/мин)", min_value=0.0, step=0.1)
                pref_rate = st.number_input("Льготная цена (20:00-06:00)", min_value=0.0, step=0.1)

                if st.form_submit_button("Добавить"):
                    t_data = {
                        "provider_id": prov_id, "effective_date": eff_date.isoformat(),
                        "city_name": city_name, "standard_rate": std_rate, "preferential_rate": pref_rate
                    }
                    if api_request("POST", "/tariffs", json=t_data):
                        st.success("Тариф добавлен")
                        st.rerun()

        with col_edit:
            if not df_t.empty:
                t_id = st.selectbox("Изменить тариф (ID)", df_t["tariff_id"])
                if st.button("Удалить выбранный тариф"):
                    if api_request("DELETE", f"/tariffs/{t_id}"):
                        st.success("Удалено")
                        st.rerun()

    # --- ВКЛАДКА ОТЧЕТЫ ---
    with tab_reports:
        r_type = st.radio("Выберите тип отчета",
                          ["📋 Список должников", "🏙 Звонки по городам (Статистика)", "💲 Тарифы на дату"],
                          horizontal=True
                          )

        st.divider()

        if r_type == "📋 Список должников":
            st.markdown("**Абоненты, не оплатившие счета более 20 дней**")
            debtors = api_request("GET", "/reports/debtors")
            if debtors:
                st.dataframe(pd.DataFrame(debtors), use_container_width=True)
            else:
                st.info("Должников не найдено.")

        elif r_type == "🏙 Звонки по городам (Статистика)":
            c1, c2, c3 = st.columns(3)
            city_filter = c1.text_input("Город", "Москва")
            month_filter = c2.number_input("Месяц", 1, 12, date.today().month)
            year_filter = c3.number_input("Год", 2000, 2030, date.today().year)

            if st.button("Сформировать статистику"):
                stats = api_request("GET", "/reports/calls_by_city",
                                    params={"city": city_filter, "month": month_filter, "year": year_filter})
                if stats:
                    st.dataframe(pd.DataFrame(stats), use_container_width=True)
                else:
                    st.warning("Нет данных за этот период.")

        elif r_type == "💲 Тарифы на дату":
            d_filter = st.date_input("Выберите дату среза")
            if st.button("Показать цены"):
                t_rep = api_request("GET", "/reports/tariffs_on_date", params={"report_date": d_filter.isoformat()})
                if t_rep:
                    st.dataframe(pd.DataFrame(t_rep), use_container_width=True)
                else:
                    st.info("Нет действующих тарифов на эту дату.")


# ==========================================
# ИНТЕРФЕЙС ОПЕРАТОРА
# ==========================================
def render_operator_ui():
    st.title("🎧 Рабочее место Оператора")

    tab_calls, tab_inv, tab_control = st.tabs(
        ["📞 Регистрация звонков", "🧾 Счета и Оплата", "⚠️ Контроль задолженностей"])

    with tab_calls:
        col1, col2 = st.columns([1, 2])
        with col1:
            st.subheader("Новый звонок")
            with st.form("new_call"):
                ph = st.text_input("Номер телефона клиента")
                dest = st.text_input("Город назначения")
                dur = st.number_input("Длительность (мин)", min_value=1)

                # Опциональная дата
                use_custom_date = st.checkbox("Указать прошлую дату?")
                c_date = st.date_input("Дата", disabled=not use_custom_date)
                c_time = st.time_input("Время", disabled=not use_custom_date)

                if st.form_submit_button("Зафиксировать звонок"):
                    payload = {"phone_number": ph, "destination_city": dest, "duration_minutes": dur}
                    if use_custom_date:
                        dt = datetime.combine(c_date, c_time)
                        payload["call_date"] = dt.isoformat()

                    if api_request("POST", "/calls", json=payload):
                        st.success("Звонок сохранен в базе")

        with col2:
            st.subheader("Журнал всех звонков")
            calls = api_request("GET", "/calls")
            if calls:
                st.dataframe(pd.DataFrame(calls), use_container_width=True)

    with tab_inv:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("### Генерация счетов")
            st.caption("Формирует счет по всем неоплаченным звонкам клиента")
            inv_client_id = st.number_input("ID Клиента", min_value=1)
            if st.button("Сформировать квитанцию"):
                res = api_request("POST", "/invoices/generate", json={"client_id": inv_client_id})
                if res:
                    st.success("Квитанция успешно сформирована и отправлена абоненту")

        with c2:
            st.markdown("### Прием оплаты")
            pay_inv_id = st.number_input("ID Счета (из квитанции)", min_value=1)
            if st.button("✅ Зафиксировать оплату"):
                if api_request("PUT", f"/invoices/{pay_inv_id}/pay"):
                    st.success(f"Счет #{pay_inv_id} оплачен!")

    with tab_control:
        st.subheader("Список должников (просрочка > 20 дней)")
        if st.button("Обновить список"):
            debtors = api_request("GET", "/reports/debtors")
            if debtors:
                df_d = pd.DataFrame(debtors)
                st.error(f"Найдено {len(df_d)} должников")
                st.dataframe(df_d)
            else:
                st.success("Должников нет")


# ==========================================
# ИНТЕРФЕЙС КЛИЕНТА
# ==========================================
def render_client_ui():
    user = st.session_state["user"]
    st.title(f"👤 Кабинет абонента: {user['full_name']}")

    # Получение ID клиента через API (небольшой хак: получаем звонки и берем client_id оттуда, либо отдельный запрос)
    # В идеале нужен эндпоинт /me, но используем существующие

    st.subheader("История звонков и Счета")

    # Получаем звонки текущего пользователя
    my_calls = api_request("GET", "/calls", params={"user_id": user["user_id"]})

    if not my_calls:
        st.info("У вас пока нет зарегистрированных звонков.")
        return

    df = pd.DataFrame(my_calls)

    # Группировка по счетам
    df["invoice_label"] = df["invoice_id"].apply(lambda x: f"Счет #{int(x)}" if pd.notnull(x) else "Не выставлен")

    unique_invoices = df["invoice_label"].unique()

    for invoice in unique_invoices:
        group = df[df["invoice_label"] == invoice]
        total_cost = group["call_cost"].sum()
        is_paid = group["is_paid"].iloc[0] if "is_paid" in group.columns else False
        inv_id_raw = group["invoice_id"].iloc[0]

        with st.expander(f"{invoice} | Сумма: {total_cost:.2f} руб. | {'✅ Оплачено' if is_paid else '❌ Не оплачено'}",
                         expanded=not is_paid):
            st.table(group[["call_date", "destination_city", "duration_minutes", "call_cost"]])

            if invoice != "Не выставлен" and not is_paid:
                st.info("Вы можете оплатить этот счет прямо сейчас.")
                if st.button(f"💳 Оплатить {invoice}", key=invoice):
                    # Клиент платит за свой счет
                    res = api_request("PUT", f"/invoices/{int(inv_id_raw)}/pay", params={"user_id": user["user_id"]})
                    if res:
                        st.balloons()
                        st.success("Оплата прошла успешно!")
                        st.rerun()


# ==========================================
# MAIN DISPATCHER
# ==========================================
def main():
    if not st.session_state["user"]:
        render_login()
    else:
        role = st.session_state["user"]["role"]

        # Сайдбар с инфо
        with st.sidebar:
            st.header("Инфо")
            st.write(f"Пользователь: **{st.session_state['user']['login']}**")
            st.write(f"Роль: **{role.upper()}**")
            st.markdown("---")
            if st.button("Выйти", use_container_width=True):
                logout()

        # Роутинг по ролям
        if role == "technologist":
            render_technologist_ui()
        elif role == "operator":
            render_operator_ui()
        elif role == "client":
            render_client_ui()
        else:
            st.error("Неизвестная роль пользователя")


if __name__ == "__main__":
    main()