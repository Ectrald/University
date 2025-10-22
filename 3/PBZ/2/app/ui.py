import streamlit as st
import requests
import pandas as pd
from datetime import date, datetime

API_URL = "http://localhost:8000"

st.set_page_config(page_title="MTC System", layout="wide")

# === Управление сессией ===
if "user" not in st.session_state:
    st.session_state["user"] = None

if not st.session_state["user"]:
    st.title("🔐 Вход в систему МТС")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            login = st.text_input("Логин")
            password = st.text_input("Пароль", type="password")
            if st.form_submit_button("Войти"):
                try:
                    resp = requests.post(f"{API_URL}/login", json={"login": login, "password": password})
                    if resp.ok:
                        st.session_state["user"] = resp.json()
                        st.rerun()
                    else:
                        st.error("Неверный логин или пароль")
                except requests.exceptions.ConnectionError:
                    st.error("Не удалось подключиться к серверу API.")
    st.stop()

user = st.session_state["user"]
role = user.get("role")
user_id = user.get("user_id")

st.sidebar.success(f"Вы вошли как: **{role}**")
st.sidebar.button("🚪 Выйти", on_click=lambda: st.session_state.clear() or st.rerun())

headers = {"role": role}

# ============================================================
# === ИНТЕРФЕЙС ТЕХНОЛОГА ===
# ============================================================
if role == "technologist":
    st.title("Панель Технолога")
    tab = st.sidebar.radio("Меню", ["Клиенты", "Тарифы", "Отчеты"])

    # --- ВКЛАДКА КЛИЕНТЫ ---
    if tab == "Клиенты":
        st.header("📋 Управление клиентами")
        try:
            clients_resp = requests.get(f"{API_URL}/clients", headers=headers)
            if not clients_resp.ok:
                st.error("Не удалось загрузить список клиентов.")
                st.stop()

            clients_list = clients_resp.json()
            clients_df = pd.DataFrame(clients_list)
            st.dataframe(clients_df, use_container_width=True)

            # --- БЛОК ДОБАВЛЕНИЯ НОВОГО КЛИЕНТА ---
            with st.expander("➕ Добавить нового клиента"):
                with st.form("new_client_form", clear_on_submit=True):
                    st.subheader("Форма добавления")
                    login = st.text_input("Логин клиента")
                    password = st.text_input("Пароль", type="password")
                    name = st.text_input("ФИО")
                    phone = st.text_input("Телефон")
                    address = st.text_area("Адрес")
                    reg_date = st.date_input("Дата регистрации", value=date.today())
                    if st.form_submit_button("Добавить клиента"):
                        data = {"login": login, "password": password, "full_name": name, "phone_number": phone,
                                "address": address, "registration_date": str(reg_date)}
                        requests.post(f"{API_URL}/clients", json=data, headers=headers)
                        st.success("Клиент успешно добавлен.")
                        st.rerun()

            # --- НОВЫЙ БЛОК: УПРАВЛЕНИЕ СУЩЕСТВУЮЩИМ КЛИЕНТОМ ---
            st.subheader("✏️ Редактирование и удаление клиентов")
            if not clients_list:
                st.warning("В системе нет клиентов для управления.")
            else:
                selected_client = st.selectbox(
                    "Выберите клиента для управления",
                    options=clients_list,
                    format_func=lambda x: f"{x['full_name']} (ID: {x['client_id']})"
                )

                if selected_client:
                    # --- РЕДАКТИРОВАНИЕ ---
                    with st.expander("✏️ Редактировать выбранного клиента"):
                        with st.form(f"edit_client_{selected_client['client_id']}", clear_on_submit=False):
                            st.write(f"Редактирование: **{selected_client['full_name']}**")
                            # Преобразуем дату из строки в объект date для виджета
                            reg_date_obj = datetime.fromisoformat(
                                selected_client['registration_date']).date() if selected_client.get(
                                'registration_date') else date.today()

                            edit_data = {
                                "full_name": st.text_input("ФИО", value=selected_client['full_name']),
                                "phone_number": st.text_input("Телефон", value=selected_client['phone_number']),
                                "address": st.text_area("Адрес", value=selected_client['address']),
                                "registration_date": str(st.date_input("Дата регистрации", value=reg_date_obj))
                            }
                            if st.form_submit_button("Сохранить изменения"):
                                requests.put(f"{API_URL}/clients/{selected_client['client_id']}", json=edit_data,
                                             headers=headers)
                                st.success(f"Данные клиента {selected_client['full_name']} обновлены.")
                                st.rerun()

                    # --- УДАЛЕНИЕ ---
                    if st.button("🗑️ Удалить выбранного клиента", key=f"del_{selected_client['client_id']}"):
                        requests.delete(f"{API_URL}/clients/{selected_client['client_id']}", headers=headers)
                        st.success(f"Клиент {selected_client['full_name']} удален.")
                        st.rerun()

        except Exception as e:
            st.error(f"Ошибка при работе с клиентами: {e}")

    # --- ВКЛАДКА ТАРИФЫ ---
    elif tab == "Тарифы":
        st.header("📈 Управление тарифами")
        try:
            tariffs_resp = requests.get(f"{API_URL}/tariffs", headers=headers)
            if not tariffs_resp.ok:
                st.error("Не удалось загрузить список тарифов.")
                st.stop()

            tariffs_list = tariffs_resp.json()
            tariffs_df = pd.DataFrame(tariffs_list)
            st.dataframe(tariffs_df, use_container_width=True)

            # --- БЛОК ДОБАВЛЕНИЯ НОВОГО ТАРИФА ---
            with st.expander("➕ Добавить новый тариф"):
                with st.form("new_tariff_form", clear_on_submit=True):
                    provider_id = st.number_input("ID провайдера", min_value=1, step=1)
                    effective_date = st.date_input("Дата вступления в силу", value=date.today())
                    city_name = st.text_input("Название города")
                    standard_rate = st.number_input("Стандартный тариф", format="%.2f")
                    preferential_rate = st.number_input("Льготный тариф", format="%.2f")
                    if st.form_submit_button("Добавить тариф"):
                        data = {"provider_id": provider_id, "effective_date": str(effective_date),
                                "city_name": city_name, "standard_rate": standard_rate,
                                "preferential_rate": preferential_rate}
                        requests.post(f"{API_URL}/tariffs", json=data, headers=headers)
                        st.success("Тариф успешно добавлен.")
                        st.rerun()

            # --- НОВЫЙ БЛОК: УПРАВЛЕНИЕ СУЩЕСТВУЮЩИМ ТАРИФОМ ---
            st.subheader("✏️ Редактирование и удаление тарифов")
            if not tariffs_list:
                st.warning("В системе нет тарифов для управления.")
            else:
                selected_tariff = st.selectbox(
                    "Выберите тариф для управления",
                    options=tariffs_list,
                    format_func=lambda x: f"{x['city_name']} от {x['effective_date']} (ID: {x['tariff_id']})"
                )

                if selected_tariff:
                    # --- РЕДАКТИРОВАНИЕ ---
                    with st.expander("✏️ Редактировать выбранный тариф"):
                        with st.form(f"edit_tariff_{selected_tariff['tariff_id']}", clear_on_submit=False):
                            st.write(f"Редактирование тарифа для: **{selected_tariff['city_name']}**")
                            eff_date_obj = datetime.fromisoformat(
                                selected_tariff['effective_date']).date() if selected_tariff.get(
                                'effective_date') else date.today()

                            edit_data = {
                                "provider_id": st.number_input("ID провайдера", value=selected_tariff['provider_id']),
                                "effective_date": str(st.date_input("Дата вступления", value=eff_date_obj)),
                                "city_name": st.text_input("Город", value=selected_tariff['city_name']),
                                "standard_rate": st.number_input("Стандартный тариф",
                                                                 value=selected_tariff['standard_rate'], format="%.2f"),
                                "preferential_rate": st.number_input("Льготный тариф",
                                                                     value=selected_tariff['preferential_rate'],
                                                                     format="%.2f")
                            }
                            if st.form_submit_button("Сохранить изменения"):
                                requests.put(f"{API_URL}/tariffs/{selected_tariff['tariff_id']}", json=edit_data,
                                             headers=headers)
                                st.success(f"Тариф для города {selected_tariff['city_name']} обновлен.")
                                st.rerun()

                    # --- УДАЛЕНИЕ ---
                    if st.button("🗑️ Удалить выбранный тариф", key=f"del_{selected_tariff['tariff_id']}"):
                        requests.delete(f"{API_URL}/tariffs/{selected_tariff['tariff_id']}", headers=headers)
                        st.success(f"Тариф для города {selected_tariff['city_name']} удален.")
                        st.rerun()

        except Exception as e:
            st.error(f"Ошибка при работе с тарифами: {e}")

    # --- ВКЛАДКА ОТЧЕТЫ ---
    elif tab == "Отчеты":
        st.header("📊 Аналитические отчеты")
        report_type = st.selectbox("Выберите тип отчета", ["Должники", "Звонки по городу за месяц", "Тарифы на дату"])

        if report_type == "Должники":
            st.subheader("Клиенты с задолженностью (срок оплаты > 20 дней)")
            if st.button("Сформировать отчет"):
                resp = requests.get(f"{API_URL}/reports/debtors", headers=headers)
                st.dataframe(pd.DataFrame(resp.json()), use_container_width=True)

        elif report_type == "Звонки по городу за месяц":
            st.subheader("Статистика звонков в город за месяц")
            city = st.text_input("Город")
            month = st.number_input("Месяц", min_value=1, max_value=12, value=date.today().month)
            year = st.number_input("Год", min_value=2020, max_value=date.today().year, value=date.today().year)
            if st.button("Сформировать отчет"):
                params = {"city": city, "month": month, "year": year}
                resp = requests.get(f"{API_URL}/reports/calls_by_city", headers=headers, params=params)
                if resp.ok:
                    df = pd.DataFrame(resp.json())
                    st.dataframe(df, use_container_width=True)
                    if not df.empty:
                        st.bar_chart(df.set_index('call_day')['total_calls'])
                else:
                    st.error(f"Ошибка при формировании отчета: {resp.text}")

        elif report_type == "Тарифы на дату":
            st.subheader("Актуальные тарифы на указанную дату")
            report_date = st.date_input("Выберите дату", date.today())
            if st.button("Сформировать отчет"):
                params = {"report_date": str(report_date)}
                resp = requests.get(f"{API_URL}/reports/tariffs_on_date", headers=headers, params=params)
                if resp.ok:
                    st.dataframe(pd.DataFrame(resp.json()), use_container_width=True)
                else:
                    st.error(f"Ошибка при формировании отчета: {resp.text}")

# ============================================================
# === ИНТЕРФЕЙС ОПЕРАТОРА ===
# ============================================================
elif role == "operator":
    st.title("Панель Оператора")
    st.header("☎️ Управление звонками")

    try:
        # Загружаем необходимые данные
        clients_resp = requests.get(f"{API_URL}/clients", headers=headers)
        tariffs_resp = requests.get(f"{API_URL}/tariffs", headers=headers)

        # Проверяем успешность запросов
        if clients_resp.ok and tariffs_resp.ok:
            clients_list = clients_resp.json()
            tariffs_list = tariffs_resp.json()
        else:
            clients_list = []
            tariffs_list = []
            st.error("Не удалось загрузить списки клиентов или тарифов.")

        with st.expander("➕ Зарегистрировать новый звонок", expanded=True):
            # Проверяем, есть ли данные для работы
            if not clients_list or not tariffs_list:
                st.warning("Невозможно добавить звонок: в системе нет клиентов или тарифов.")
            else:
                with st.form("new_call_form", clear_on_submit=True):
                    # Безопасно получаем выбранного клиента
                    selected_client = st.selectbox(
                        "Клиент",
                        options=clients_list,
                        format_func=lambda x: f"{x['full_name']} (ID: {x['client_id']})"
                    )

                    selected_tariff = st.selectbox(
                        "Тариф",
                        options=tariffs_list,
                        format_func=lambda x: f"{x['city_name']} от {x['effective_date']} (ID: {x['tariff_id']})"
                    )

                    destination_city = st.text_input("Город назначения")
                    duration_minutes = st.number_input("Длительность (минут)", min_value=1)

                    # Эта кнопка теперь будет отображаться корректно
                    submitted = st.form_submit_button("Добавить звонок")

                    if submitted:
                        # Убеждаемся, что что-то выбрано перед отправкой
                        if selected_client and selected_tariff:
                            data = {
                                "client_id": selected_client['client_id'],
                                "tariff_id": selected_tariff['tariff_id'],
                                "destination_city": destination_city,
                                "duration_minutes": duration_minutes
                            }
                            requests.post(f"{API_URL}/calls", json=data, headers=headers)
                            st.success("Звонок успешно зарегистрирован.")
                            st.rerun()
                        else:
                            st.error("Пожалуйста, выберите клиента и тариф.")

        st.subheader("Все зарегистрированные звонки")
        calls_resp = requests.get(f"{API_URL}/calls", headers=headers)
        if calls_resp.ok:
            st.dataframe(pd.DataFrame(calls_resp.json()), use_container_width=True)

    except Exception as e:
        st.error(f"Произошла непредвиденная ошибка: {e}")

# ============================================================
# === ИНТЕРФЕЙС КЛИЕНТА ===
# ============================================================
elif role == "client":
    st.title(f"Личный кабинет клиента")
    st.header("💳 Мои звонки и оплата")

    try:
        # Получаем client_id по user_id
        # В реальной системе это было бы частью данных сессии
        clients_resp = requests.get(f"{API_URL}/clients", headers={"role": "technologist"})
        client_info = next((c for c in clients_resp.json() if c.get('user_id') == user_id), None)

        if not client_info:
            st.error("Не удалось найти данные вашего профиля.")
            st.stop()

        client_id_from_session = client_info['client_id']
        params = {"client_id": client_id_from_session}
        resp = requests.get(f"{API_URL}/calls", headers=headers, params=params)
        df = pd.DataFrame(resp.json())

        st.subheader("Неоплаченные звонки")
        df_unpaid = df[df["is_paid"] == False]

        if df_unpaid.empty:
            st.success("У вас нет неоплаченных счетов. 🎉")
        else:
            for index, row in df_unpaid.iterrows():
                col1, col2, col3, col4, col5 = st.columns(5)
                col1.text(row['destination_city'])
                col2.text(datetime.fromisoformat(row['call_date']).strftime('%Y-%m-%d %H:%M'))
                col3.text(f"{row['duration_minutes']} мин.")
                col4.text(f"{row['call_cost']} руб.")
                if col5.button("Оплатить", key=f"pay_{row['call_id']}"):
                    pay_resp = requests.put(f"{API_URL}/calls/{row['call_id']}/pay", headers=headers)
                    if pay_resp.ok:
                        st.success(f"Звонок #{row['call_id']} успешно оплачен!")
                        st.rerun()
                    else:
                        st.error("Не удалось произвести оплату.")

        st.subheader("История всех звонков")
        st.dataframe(df, use_container_width=True)

    except Exception as e:
        st.error(f"Ошибка при загрузке ваших данных: {e}")