
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- ============================================================
-- Аутентификация и CRUD
-- ============================================================

-- Аутентификация пользователя
CREATE OR REPLACE FUNCTION authenticate_user(p_login VARCHAR(100), p_password VARCHAR(100))
RETURNS TABLE (user_id INT, login VARCHAR(100), role VARCHAR(50)) LANGUAGE plpgsql SECURITY DEFINER AS $$
BEGIN
    RETURN QUERY SELECT ua.user_id, ua.login, ua.role FROM user_account ua
    WHERE ua.login = p_login AND ua.password_hash = crypt(p_password, ua.password_hash) LIMIT 1;
END;
$$;

-- Добавление клиента
CREATE OR REPLACE FUNCTION add_client(p_login VARCHAR(100), p_password VARCHAR(100), p_full_name VARCHAR(255), p_phone VARCHAR(20), p_address VARCHAR(500), p_registration_date DATE)
RETURNS VOID LANGUAGE plpgsql AS $$
DECLARE new_user_id INT;
BEGIN
    INSERT INTO user_account (login, password_hash, role)
    VALUES (p_login, crypt(p_password, gen_salt('bf')), 'client')
    RETURNING user_id INTO new_user_id;
    INSERT INTO client (user_id, full_name, phone_number, address, registration_date)
    VALUES (new_user_id, p_full_name, p_phone, p_address, p_registration_date);
END;
$$;

-- Обновление клиента
CREATE OR REPLACE PROCEDURE update_client(p_client_id INT, p_full_name VARCHAR(255), p_phone_number VARCHAR(20), p_address TEXT, p_registration_date DATE)
LANGUAGE plpgsql AS $$
BEGIN
    UPDATE client SET full_name = p_full_name, phone_number = p_phone_number, address = p_address, registration_date = p_registration_date
    WHERE client_id = p_client_id;
END;
$$;

-- Удаление клиента (через user_account)
CREATE OR REPLACE FUNCTION delete_client(p_client_id INT)
RETURNS VOID LANGUAGE plpgsql AS $$
BEGIN
    DELETE FROM user_account WHERE user_id = (SELECT user_id FROM client WHERE client_id = p_client_id);
END;
$$;


-- Добавление тарифа
CREATE OR REPLACE FUNCTION add_tariff(p_provider_id INT, p_effective_date DATE, p_city_name VARCHAR(255), p_standard_rate DECIMAL(10,2), p_preferential_rate DECIMAL(10,2))
RETURNS VOID LANGUAGE plpgsql AS $$
BEGIN
    INSERT INTO tariff (provider_id, effective_date, city_name, standard_rate, preferential_rate)
    VALUES (p_provider_id, p_effective_date, p_city_name, p_standard_rate, p_preferential_rate)
    ON CONFLICT (effective_date, city_name) DO UPDATE SET standard_rate = EXCLUDED.standard_rate, preferential_rate = EXCLUDED.preferential_rate;
END;
$$;

-- Обновление тарифа
CREATE OR REPLACE FUNCTION update_tariff(p_tariff_id INT, p_provider_id INT, p_effective_date DATE, p_city_name VARCHAR(255), p_standard_rate DECIMAL(10,2), p_preferential_rate DECIMAL(10,2))
RETURNS VOID LANGUAGE plpgsql AS $$
BEGIN
    UPDATE tariff SET provider_id = p_provider_id, effective_date = p_effective_date, city_name = p_city_name, standard_rate = p_standard_rate, preferential_rate = p_preferential_rate
    WHERE tariff_id = p_tariff_id;
END;
$$;

-- Удаление тарифа
CREATE OR REPLACE FUNCTION delete_tariff(p_tariff_id INT)
RETURNS VOID LANGUAGE plpgsql AS $$
BEGIN
    DELETE FROM tariff WHERE tariff_id = p_tariff_id;
END;
$$;

-- Добавление звонка
CREATE OR REPLACE FUNCTION add_call(p_client_id INT, p_tariff_id INT, p_destination_city VARCHAR(255), p_duration INT)
RETURNS VOID LANGUAGE plpgsql AS $$
DECLARE v_rate DECIMAL(10,2); v_is_preferential_time BOOLEAN;
BEGIN
    v_is_preferential_time := EXTRACT(HOUR FROM NOW()) >= 20 OR EXTRACT(HOUR FROM NOW()) < 6;
    IF v_is_preferential_time THEN
        SELECT preferential_rate INTO v_rate FROM tariff WHERE tariff_id = p_tariff_id;
    ELSE
        SELECT standard_rate INTO v_rate FROM tariff WHERE tariff_id = p_tariff_id;
    END IF;
    IF v_rate IS NULL THEN RAISE EXCEPTION 'Tarif id % не найден', p_tariff_id; END IF;
    INSERT INTO call (client_id, tariff_id, destination_city, duration_minutes, call_cost, call_date, receipt_issue_date)
    VALUES (p_client_id, p_tariff_id, p_destination_city, p_duration, v_rate * p_duration, CURRENT_TIMESTAMP, CURRENT_DATE);
END;
$$;

-- Отметка оплаты звонка
CREATE OR REPLACE FUNCTION mark_paid(p_call_id INT)
RETURNS VOID LANGUAGE plpgsql AS $$
BEGIN
    UPDATE call SET is_paid = TRUE, payment_date = CURRENT_DATE WHERE call_id = p_call_id;
END;
$$;

-- ============================================================
-- Функции для получения данных и отчетов
-- ============================================================

-- Получение всех клиентов
CREATE OR REPLACE FUNCTION get_all_clients()
RETURNS TABLE (client_id INT, full_name VARCHAR(255), phone_number VARCHAR(20), address TEXT, registration_date DATE, user_id INT)
LANGUAGE plpgsql AS $$
BEGIN
    RETURN QUERY SELECT c.client_id, c.full_name, c.phone_number, c.address, c.registration_date, c.user_id FROM client c ORDER BY c.client_id;
END;
$$;

-- Получение всех тарифов
CREATE OR REPLACE FUNCTION get_all_tariffs()
RETURNS TABLE (tariff_id INT, provider_id INT, effective_date DATE, city_name VARCHAR(255), standard_rate DECIMAL(10,2), preferential_rate DECIMAL(10,2), provider_name VARCHAR(255))
LANGUAGE plpgsql AS $$
BEGIN
    RETURN QUERY SELECT t.tariff_id, t.provider_id, t.effective_date, t.city_name, t.standard_rate, t.preferential_rate, p.name as provider_name
    FROM tariff t JOIN service_provider p ON t.provider_id = p.provider_id ORDER BY t.tariff_id;
END;
$$;

-- Получение всех звонков
CREATE OR REPLACE FUNCTION get_all_calls()
RETURNS TABLE (call_id INT, client_id INT, tariff_id INT, call_date TIMESTAMP, destination_city VARCHAR(255), duration_minutes INT, call_cost DECIMAL(10,2), is_paid BOOLEAN)
LANGUAGE plpgsql AS $$
BEGIN
    RETURN QUERY SELECT ca.call_id, ca.client_id, ca.tariff_id, ca.call_date, ca.destination_city, ca.duration_minutes, ca.call_cost, ca.is_paid
    FROM call ca ORDER BY ca.call_date DESC;
END;
$$;

-- Получение звонков конкретного клиента
CREATE OR REPLACE FUNCTION get_calls_by_client(p_client_id INT)
RETURNS TABLE (call_id INT, destination_city VARCHAR(255), call_date TIMESTAMP, duration_minutes INT, call_cost DECIMAL(10,2), is_paid BOOLEAN)
LANGUAGE plpgsql AS $$
BEGIN
    RETURN QUERY SELECT ca.call_id, ca.destination_city, ca.call_date, ca.duration_minutes, ca.call_cost, ca.is_paid
    FROM call ca WHERE ca.client_id = p_client_id ORDER BY ca.call_date DESC;
END;
$$;


-- Отчет по должникам
CREATE OR REPLACE FUNCTION get_debtors(p_days_overdue INT)
RETURNS TABLE (call_date DATE, provider_name VARCHAR(255), phone_number VARCHAR(20), full_name VARCHAR(255), address TEXT, total_debt DECIMAL(10,2))
LANGUAGE plpgsql AS $$
BEGIN
    RETURN QUERY
    SELECT MIN(ca.call_date)::DATE, sp.name, c.phone_number, c.full_name, c.address, SUM(ca.call_cost) AS total_debt
    FROM client c
    JOIN call ca ON ca.client_id = c.client_id
    JOIN tariff t ON ca.tariff_id = t.tariff_id
    JOIN service_provider sp ON t.provider_id = sp.provider_id
    WHERE ca.is_paid = FALSE AND ca.receipt_issue_date < (CURRENT_DATE - p_days_overdue)
    GROUP BY sp.name, c.client_id, c.full_name, c.phone_number, c.address
    HAVING SUM(ca.call_cost) > 0;
END;
$$;

-- Отчет по звонкам в город за месяц
CREATE OR REPLACE FUNCTION get_calls_by_city_daily(p_city VARCHAR(255), p_month INT, p_year INT)
RETURNS TABLE (call_day DATE, total_calls BIGINT, unique_clients BIGINT)
LANGUAGE plpgsql AS $$
BEGIN
    RETURN QUERY
    SELECT DATE(call_date) AS call_day, COUNT(*) AS total_calls, COUNT(DISTINCT client_id) AS unique_clients
    FROM call WHERE destination_city = p_city AND EXTRACT(MONTH FROM call_date) = p_month AND EXTRACT(YEAR FROM call_date) = p_year
    GROUP BY call_day ORDER BY call_day;
END;
$$;

-- Отчет по тарифам на дату
CREATE OR REPLACE FUNCTION get_tariffs_on_date(p_report_date DATE)
RETURNS TABLE (provider_name VARCHAR(255), effective_date DATE, city_name VARCHAR(255), standard_rate DECIMAL(10,2), preferential_rate DECIMAL(10,2))
LANGUAGE plpgsql AS $$
BEGIN
    RETURN QUERY
    SELECT DISTINCT ON (t.city_name) p.name, t.effective_date, t.city_name, t.standard_rate, t.preferential_rate
    FROM tariff t JOIN service_provider p ON t.provider_id = p.provider_id
    WHERE t.effective_date <= p_report_date ORDER BY t.city_name, t.effective_date DESC;
END;
$$;