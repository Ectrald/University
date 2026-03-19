CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- === Аутентификация ===
CREATE OR REPLACE FUNCTION authenticate_user(p_login VARCHAR(100), p_password VARCHAR(100))
RETURNS TABLE (user_id INT, login VARCHAR(100), role VARCHAR(50), full_name VARCHAR(255)) LANGUAGE plpgsql SECURITY DEFINER AS $$
BEGIN
    RETURN QUERY
    SELECT ua.user_id, ua.login, ua.role, ua.full_name
    FROM user_account ua
    WHERE ua.login = p_login AND ua.password_hash = crypt(p_password, ua.password_hash)
    LIMIT 1;
END;
$$;

-- === Клиенты ===
CREATE OR REPLACE PROCEDURE add_client(
    p_login VARCHAR(100),
    p_password VARCHAR(100),
    p_full_name VARCHAR(255),
    p_phone VARCHAR(20),
    p_address VARCHAR(500),
    p_registration_date DATE
)
LANGUAGE plpgsql AS $$
DECLARE
    new_user_id INT;
BEGIN
    IF EXISTS (SELECT 1 FROM client WHERE phone_number = p_phone) THEN
        RAISE EXCEPTION 'Phone number % already exists', p_phone;
    END IF;

    INSERT INTO user_account (login, password_hash, role, full_name)
    VALUES (p_login, crypt(p_password, gen_salt('bf')), 'client', p_full_name)
    RETURNING user_id INTO new_user_id;

    INSERT INTO client (user_id, phone_number, address, registration_date)
    VALUES (new_user_id, p_phone, p_address, p_registration_date);
END;
$$;

CREATE OR REPLACE PROCEDURE update_client(
    p_client_id INT,
    p_full_name VARCHAR(255),
    p_phone_number VARCHAR(20),
    p_address TEXT,
    p_registration_date DATE
)
LANGUAGE plpgsql AS $$
DECLARE v_user_id INT;
BEGIN
    IF p_phone_number IS NOT NULL THEN
        IF EXISTS (SELECT 1 FROM client WHERE phone_number = p_phone_number AND client_id <> p_client_id) THEN
            RAISE EXCEPTION 'Phone number % used by another client', p_phone_number;
        END IF;
    END IF;

    UPDATE client
    SET phone_number = COALESCE(p_phone_number, phone_number),
        address = COALESCE(p_address, address),
        registration_date = COALESCE(p_registration_date, registration_date)
    WHERE client_id = p_client_id;

    SELECT user_id INTO v_user_id FROM client WHERE client_id = p_client_id;
    IF v_user_id IS NOT NULL THEN
        UPDATE user_account SET full_name = p_full_name WHERE user_id = v_user_id;
    END IF;
END;
$$;

CREATE OR REPLACE PROCEDURE delete_client(p_client_id INT)
LANGUAGE plpgsql AS $$
DECLARE v_user_id INT;
BEGIN
    IF EXISTS (SELECT 1 FROM call WHERE client_id = p_client_id) THEN
        RAISE EXCEPTION 'Cannot delete client: existing calls found.';
    END IF;
    IF EXISTS (SELECT 1 FROM invoice WHERE client_id = p_client_id) THEN
        RAISE EXCEPTION 'Cannot delete client: existing invoices found.';
    END IF;

    SELECT user_id INTO v_user_id FROM client WHERE client_id = p_client_id;
    IF v_user_id IS NULL THEN RAISE EXCEPTION 'Client not found'; END IF;

    DELETE FROM user_account WHERE user_id = v_user_id;
END;
$$;

-- === Тарифы ===
CREATE OR REPLACE PROCEDURE add_tariff(
    p_provider_id INT,
    p_effective_date DATE,
    p_city_name VARCHAR(255),
    p_standard_rate NUMERIC(10,2),
    p_preferential_rate NUMERIC(10,2)
)
LANGUAGE plpgsql AS $$
BEGIN
    INSERT INTO tariff (provider_id, effective_date, city_name, standard_rate, preferential_rate)
    VALUES (p_provider_id, p_effective_date, p_city_name, p_standard_rate, p_preferential_rate)
    ON CONFLICT (provider_id, effective_date, city_name)
    DO UPDATE SET standard_rate = EXCLUDED.standard_rate, preferential_rate = EXCLUDED.preferential_rate;
END;
$$;

CREATE OR REPLACE PROCEDURE update_tariff(
    p_tariff_id INT,
    p_provider_id INT,
    p_effective_date DATE,
    p_city_name VARCHAR(255),
    p_standard_rate NUMERIC(10,2),
    p_preferential_rate NUMERIC(10,2)
)
LANGUAGE plpgsql AS $$
BEGIN
    UPDATE tariff
    SET provider_id = p_provider_id,
        effective_date = p_effective_date,
        city_name = p_city_name,
        standard_rate = p_standard_rate,
        preferential_rate = p_preferential_rate
    WHERE tariff_id = p_tariff_id;
END;
$$;

CREATE OR REPLACE PROCEDURE delete_tariff(p_tariff_id INT)
LANGUAGE plpgsql AS $$
BEGIN
    IF EXISTS (SELECT 1 FROM call WHERE tariff_id = p_tariff_id) THEN
        RAISE EXCEPTION 'Cannot delete tariff referenced by calls';
    END IF;
    DELETE FROM tariff WHERE tariff_id = p_tariff_id;
END;
$$;

-- === Звонки и Счета ===
CREATE OR REPLACE PROCEDURE add_call(
    p_phone_number VARCHAR(20),
    p_destination_city VARCHAR(255),
    p_duration INT,
    p_call_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
LANGUAGE plpgsql AS $$
DECLARE
    v_client_id INT;
    v_tariff_id INT;
    v_rate NUMERIC(10,2);
    v_is_preferential BOOLEAN;
BEGIN
    SELECT client_id INTO v_client_id FROM client WHERE phone_number = p_phone_number LIMIT 1;
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Client with phone % not found.', p_phone_number;
    END IF;

    SELECT tariff_id INTO v_tariff_id
    FROM tariff
    WHERE city_name = p_destination_city AND effective_date <= DATE(p_call_date)
    ORDER BY effective_date DESC LIMIT 1;

    IF v_tariff_id IS NULL THEN
        RAISE EXCEPTION 'No tariff found for city %', p_destination_city;
    END IF;

    v_is_preferential := (EXTRACT(HOUR FROM p_call_date) >= 20 OR EXTRACT(HOUR FROM p_call_date) < 6);
    IF v_is_preferential THEN
        SELECT preferential_rate INTO v_rate FROM tariff WHERE tariff_id = v_tariff_id;
    ELSE
        SELECT standard_rate INTO v_rate FROM tariff WHERE tariff_id = v_tariff_id;
    END IF;

    INSERT INTO call (client_id, phone_number, tariff_id, destination_city, duration_minutes, call_cost, call_date)
    VALUES (v_client_id, p_phone_number, v_tariff_id, p_destination_city, p_duration, ROUND(v_rate * p_duration::numeric, 2), p_call_date);
END;
$$;

CREATE OR REPLACE PROCEDURE generate_invoice(p_client_id INT)
LANGUAGE plpgsql AS $$
DECLARE
    v_invoice_id INT;
    v_total NUMERIC(12,2);
BEGIN
    SELECT SUM(call_cost) INTO v_total FROM call WHERE client_id = p_client_id AND invoice_id IS NULL;

    IF v_total IS NULL OR v_total = 0 THEN
        RAISE EXCEPTION 'No unbilled calls found for client %', p_client_id;
    END IF;

    INSERT INTO invoice (client_id, issue_date, total_amount, is_paid)
    VALUES (p_client_id, CURRENT_DATE, v_total, FALSE)
    RETURNING invoice_id INTO v_invoice_id;

    UPDATE call SET invoice_id = v_invoice_id WHERE client_id = p_client_id AND invoice_id IS NULL;
    PERFORM _update_invoice_total(v_invoice_id);
END;
$$;

CREATE OR REPLACE PROCEDURE mark_invoice_paid(p_invoice_id INT)
LANGUAGE plpgsql AS $$
BEGIN
    UPDATE invoice SET is_paid = TRUE, payment_date = CURRENT_DATE WHERE invoice_id = p_invoice_id;
END;
$$;

-- === Функции чтения (SELECT) ===
CREATE OR REPLACE FUNCTION get_all_clients()
RETURNS TABLE (client_id INT, full_name VARCHAR(255), phone_number VARCHAR(20), address TEXT, registration_date DATE, user_id INT)
LANGUAGE plpgsql AS $$
BEGIN
    RETURN QUERY
    SELECT c.client_id, ua.full_name, c.phone_number, c.address, c.registration_date, c.user_id
    FROM client c
    JOIN user_account ua ON c.user_id = ua.user_id
    ORDER BY c.client_id;
END;
$$;

CREATE OR REPLACE FUNCTION get_all_tariffs()
RETURNS TABLE (tariff_id INT, provider_id INT, effective_date DATE, city_name VARCHAR(255), standard_rate NUMERIC(10,2), preferential_rate NUMERIC(10,2), provider_name VARCHAR(255))
LANGUAGE plpgsql AS $$
BEGIN
    RETURN QUERY
    SELECT t.tariff_id, t.provider_id, t.effective_date, t.city_name, t.standard_rate, t.preferential_rate, p.name
    FROM tariff t JOIN service_provider p ON t.provider_id = p.provider_id
    ORDER BY t.tariff_id;
END;
$$;

CREATE OR REPLACE FUNCTION get_all_calls()
RETURNS TABLE (call_id INT, client_id INT, phone_number VARCHAR(20), tariff_id INT, call_date TIMESTAMP, destination_city VARCHAR(255), duration_minutes INT, call_cost NUMERIC(12,2), is_paid BOOLEAN, invoice_id INT)
LANGUAGE plpgsql AS $$
BEGIN
    RETURN QUERY
    SELECT ca.call_id, ca.client_id, ca.phone_number, ca.tariff_id, ca.call_date, ca.destination_city, ca.duration_minutes, ca.call_cost, COALESCE(inv.is_paid, FALSE), ca.invoice_id
    FROM call ca
    LEFT JOIN invoice inv ON ca.invoice_id = inv.invoice_id
    ORDER BY ca.call_date DESC;
END;
$$;

CREATE OR REPLACE FUNCTION get_calls_by_client(p_client_id INT)
RETURNS TABLE (call_id INT, destination_city VARCHAR(255), call_date TIMESTAMP, duration_minutes INT, call_cost NUMERIC(12,2), is_paid BOOLEAN, invoice_id INT)
LANGUAGE plpgsql AS $$
BEGIN
    RETURN QUERY
    SELECT ca.call_id, ca.destination_city, ca.call_date, ca.duration_minutes, ca.call_cost, COALESCE(inv.is_paid, FALSE), ca.invoice_id
    FROM call ca
    LEFT JOIN invoice inv ON ca.invoice_id = inv.invoice_id
    WHERE ca.client_id = p_client_id
    ORDER BY ca.call_date DESC;
END;
$$;

-- Отчеты
CREATE OR REPLACE FUNCTION get_debtors(p_days_overdue INT)
RETURNS TABLE (invoice_issue_date DATE, provider_name VARCHAR(255), phone_number VARCHAR(20), full_name VARCHAR(255), address TEXT, total_debt NUMERIC(12,2))
LANGUAGE plpgsql AS $$
BEGIN
    RETURN QUERY
    SELECT inv.issue_date, COALESCE(sp.name, 'Unknown'), c.phone_number, ua.full_name, c.address, inv.total_amount
    FROM invoice inv
    JOIN client c ON inv.client_id = c.client_id
    LEFT JOIN user_account ua ON c.user_id = ua.user_id
    LEFT JOIN service_provider sp ON sp.provider_id = (
        SELECT t.provider_id FROM tariff t WHERE t.city_name = (
            SELECT destination_city FROM call WHERE invoice_id = inv.invoice_id LIMIT 1
        ) LIMIT 1
    )
    WHERE inv.is_paid = FALSE AND inv.issue_date < (CURRENT_DATE - p_days_overdue)
    ORDER BY inv.issue_date;
END;
$$;

CREATE OR REPLACE FUNCTION get_calls_by_city_daily(p_city VARCHAR(255), p_month INT, p_year INT)
RETURNS TABLE (call_day DATE, total_calls BIGINT, unique_clients BIGINT)
LANGUAGE plpgsql AS $$
BEGIN
    RETURN QUERY
    SELECT DATE(call_date) AS call_day, COUNT(*) AS total_calls, COUNT(DISTINCT client_id) AS unique_clients
    FROM call
    WHERE destination_city = p_city
      AND EXTRACT(MONTH FROM call_date) = p_month
      AND EXTRACT(YEAR FROM call_date) = p_year
    GROUP BY call_day ORDER BY call_day;
END;
$$;

CREATE OR REPLACE FUNCTION get_tariffs_on_date(p_report_date DATE)
RETURNS TABLE (provider_name VARCHAR(255), effective_date DATE, city_name VARCHAR(255), standard_rate NUMERIC(10,2), preferential_rate NUMERIC(10,2))
LANGUAGE plpgsql AS $$
BEGIN
    RETURN QUERY
    SELECT p.name, t.effective_date, t.city_name, t.standard_rate, t.preferential_rate
    FROM (
        SELECT DISTINCT ON (city_name) *
        FROM tariff
        WHERE effective_date <= p_report_date
        ORDER BY city_name, effective_date DESC
    ) t
    JOIN service_provider p ON t.provider_id = p.provider_id
    ORDER BY t.city_name;
END;
$$;