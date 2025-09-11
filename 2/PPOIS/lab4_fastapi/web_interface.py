import streamlit as st
import requests

# Настройки
API_URL = "http://127.0.0.1:8000"
st.set_page_config(page_title="Финансовый мониторинг", layout="wide")


# Вспомогательные функции
def call_api(endpoint, method="GET", json=None):
    try:
        if method == "GET":
            response = requests.get(f"{API_URL}{endpoint}")
        elif method == "POST":
            response = requests.post(f"{API_URL}{endpoint}", json=json)

        # Проверяем статус ответа
        if response.status_code >= 400:
            try:
                error_data = response.json()
                if 'detail' in error_data:
                    if isinstance(error_data['detail'], dict):
                        return {"error": error_data['detail'].get('error', 'Неизвестная ошибка')}
                    return {"error": str(error_data['detail'])}
                return {"error": "Неизвестная ошибка сервера"}
            except:
                return {"error": response.text}

        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}


# Основной интерфейс
def main():
    st.title("Система финансового мониторинга")

    tab1, tab2, tab3, tab4 = st.tabs(["Счета", "Бюджет", "Инвестиции", "Отчеты"])

    with tab1:
        st.header("Управление банковскими счетами")

        col1, col2 = st.columns(2)

        with col1:
            with st.form("create_account"):
                st.subheader("Создать новый счет")
                balance = st.number_input("Начальный баланс")
                if st.form_submit_button("Создать"):
                    if balance > 0:
                        result = call_api("/accounts", "POST", {"balance": balance})
                        if result:
                            st.success(f"Счет создан! ID: {result['id']}")
                    else:
                        st.info("Значение не может быть меньше 0")




        with col2:
            with st.form("account_operations"):
                st.subheader("Операции со счетом")
                accounts = call_api("/accounts") or []
                account_id = st.selectbox("Выберите счет", [acc["id"] for acc in accounts])
                operation = st.radio("Операция", ["Пополнить", "Снять"])
                amount = st.number_input("Сумма")
                description = st.text_input("Описание")
                if st.form_submit_button("Выполнить"):
                    if amount > 0:
                        endpoint = f"/accounts/{account_id}/deposit" if operation == "Пополнить" else f"/accounts/{account_id}/withdraw"
                        result = call_api(endpoint, "POST", {"amount": amount, "description": description})
                        if result:
                            st.success(result["message"])
                    else:
                        st.info("Значение не может быть меньше 0")

        st.subheader("Детальная информация по счетам")
        accounts = call_api("/accounts") or []

        if accounts:
            # Сортировка счетов по статусу (активные сначала)
            accounts_sorted = sorted(accounts, key=lambda x: x['state'] == 'frozen')

            for acc in accounts_sorted:
                status = "Активен ✅" if acc['state'] == 'active' else "Заморожен ❄️"
                status_color = "green" if acc['state'] == 'active' else "red"

                with st.container(border=True):
                    cols = st.columns([1, 2, 1, 1, 1])
                    cols[0].write(f"**ID счета:**")
                    cols[1].code(acc['id'], language="text")

                    cols[2].metric(
                        "Баланс",
                        f"{acc['balance']:.2f} ₽",
                        delta_color="normal" if acc['balance'] >= 0 else "inverse"
                    )

                    cols[3].markdown(
                        f"<span style='color:{status_color}; font-weight:bold;'>{status}</span>",
                        unsafe_allow_html=True
                    )

                    # Кнопка для обновления состояния счета
                    if cols[4].button("Обновить", key=f"refresh_{acc['id']}"):
                        st.rerun()

                    # Дополнительная информация при нажатии
                    with st.expander("Подробнее", expanded=False):
                        st.write(f"**Последние операции:**")

                        # Получаем транзакции для этого счета (примерная реализация)
                        budget_data = call_api("/budget")
                        if budget_data:
                            account_transactions = [
                                                       t for t in budget_data.get('transactions', [])
                                                       if acc['id'] in t.get('description', '')
                                                   ][-5:]  # Последние 5 операций

                            if account_transactions:
                                for t in reversed(account_transactions):
                                    op_type = "➕ Доход" if t['type'] == 'income' else "➖ Расход"
                                    st.write(f"{op_type}: {t['amount']:.2f} ₽ - {t['description']}")
                            else:
                                st.info("Нет операций по этому счету")
        else:
            st.info("У вас пока нет банковских счетов")

    with tab2:
        st.header("Управление бюджетом")

        col1, col2 = st.columns(2)

        with col1:
            with st.form("add_income"):
                st.subheader("Добавить доход")
                income_amount = st.number_input("Сумма дохода")
                income_desc = st.text_input("Описание дохода")
                if st.form_submit_button("Добавить"):
                    if income_amount > 0:
                        result = call_api("/budget/income", "POST", {"amount": income_amount, "description": income_desc})
                        if result:
                            st.success("Доход добавлен")
                    else:
                        st.info("Значение не может быть меньше 0")

        with col2:
            with st.form("add_expense"):
                st.subheader("Добавить расход")
                expense_amount = st.number_input("Сумма расхода")
                expense_desc = st.text_input("Описание расхода")
                if st.form_submit_button("Добавить"):
                    if expense_amount > 0:
                        result = call_api("/budget/expense", "POST",
                                          {"amount": expense_amount, "description": expense_desc})
                        if result:
                            st.success("Расход добавлен")
                    else:
                        st.info("Значение не может быть меньше 0")

        budget = call_api("/budget")
        if budget:
            st.subheader("Текущее состояние бюджета")
            col1, col2, col3 = st.columns(3)
            col1.metric("Доходы", f"{budget['income']:.2f} ₽")
            col2.metric("Расходы", f"{budget['expenses']:.2f} ₽")
            col3.metric("Баланс", f"{budget['income'] - budget['expenses']:.2f} ₽",
                        delta="Сбалансирован" if budget['state'] == "BALANCED" else "Дефицит")

    with tab3:
        st.header("Управление инвестициями")

        with st.form("add_investment"):
            st.subheader("Добавить инвестицию")
            accounts = call_api("/accounts") or []
            inv_type = st.text_input("Тип инвестиции (акции, облигации и т.д.)")
            inv_desc = st.text_input("Описание инвестиции")
            inv_units = st.number_input("Количество единиц")
            inv_price = st.number_input("Цена за единицу")
            account_id = st.selectbox("Счет для списания", [acc["id"] for acc in accounts])

            if st.form_submit_button("Добавить инвестицию"):
                if inv_units and inv_price > 0:
                    result = call_api("/investments", "POST", {
                        "type_of_investment": inv_type,
                        "description": inv_desc,
                        "number_of_units": inv_units,
                        "unit_price": inv_price,
                        "account_id": account_id
                    })
                    if result and "error" not in result:
                        st.success(result["message"])
                    elif result and "error" in result:
                        st.error(f"Ошибка: {result['error']}")
                else:
                    st.info("Значение не может быть меньше 0")



        investments = call_api("/investments") or []
        if investments:
            st.subheader("Ваши инвестиции")
            for inv in investments:
                with st.expander(f"{inv['type']} - {inv['description']}"):
                    st.write(f"Количество: {inv['units']:.2f}")
                    st.write(f"Цена за единицу: {inv['unit_price']:.2f} ₽")
                    st.write(f"Общая стоимость: {inv['total_value']:.2f} ₽")
                    st.write(f"Привязанный счет: {inv['account_id']}")

                    with st.form(f"sell_{inv['id']}"):
                        units_to_sell = st.number_input(
                            "Количество для продажи",
                            value=inv['units'],
                            key=f"units_{inv['id']}"
                        )

                        if st.form_submit_button("Продать"):
                            if units_to_sell <= inv['units'] and units_to_sell > 0:
                                result = call_api(
                                    f"/investments/{inv['id']}/sell",
                                    "POST",
                                    {"units_to_sell": units_to_sell}
                                )
                                if result:
                                    st.success(result["message"])
                            else:
                                st.info("Неверное значение")



    with tab4:
        st.header("Финансовые отчеты")

        reports = call_api("/reports/profit")
        if reports:
            st.metric("Чистая прибыль", f"{reports['net_profit']:.2f} ₽")

        st.subheader("Детализация доходов")
        income_report = call_api("/reports/income")
        if income_report:
            st.dataframe(income_report["transactions"])

        st.subheader("Детализация расходов")
        expense_report = call_api("/reports/expense")
        if expense_report:
            st.dataframe(expense_report["transactions"])


if __name__ == "__main__":
    main()