CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- 1. Провайдеры услуг
CREATE TABLE IF NOT EXISTS service_provider (
    provider_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    address TEXT
);

-- 2. Учетные записи пользователей
CREATE TABLE IF NOT EXISTS user_account (
    user_id SERIAL PRIMARY KEY,
    login VARCHAR(100) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('technologist','operator','client')),
    full_name VARCHAR(255)
);

-- 3. Клиенты
CREATE TABLE IF NOT EXISTS client (
    client_id SERIAL PRIMARY KEY,
    user_id INT UNIQUE REFERENCES user_account(user_id) ON DELETE CASCADE,
    phone_number VARCHAR(20) UNIQUE NOT NULL,
    address TEXT NOT NULL,
    registration_date DATE NOT NULL
);

-- 4. Персонал (Операторы / Технологи)
CREATE TABLE IF NOT EXISTS operator (
    operator_id SERIAL PRIMARY KEY,
    user_id INT UNIQUE REFERENCES user_account(user_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS technologist (
    technologist_id SERIAL PRIMARY KEY,
    user_id INT UNIQUE REFERENCES user_account(user_id) ON DELETE CASCADE
);

-- 5. Тарифы
CREATE TABLE IF NOT EXISTS tariff (
    tariff_id SERIAL PRIMARY KEY,
    provider_id INT NOT NULL REFERENCES service_provider(provider_id) ON DELETE RESTRICT,
    effective_date DATE NOT NULL,
    city_name VARCHAR(255) NOT NULL,
    standard_rate NUMERIC(10,2) NOT NULL CHECK (standard_rate >= 0),
    preferential_rate NUMERIC(10,2) NOT NULL CHECK (preferential_rate >= 0),
    UNIQUE (provider_id, effective_date, city_name)
);

-- 6. Счета
CREATE TABLE IF NOT EXISTS invoice (
    invoice_id SERIAL PRIMARY KEY,
    client_id INT NOT NULL REFERENCES client(client_id) ON DELETE RESTRICT,
    issue_date DATE NOT NULL DEFAULT CURRENT_DATE,
    payment_date DATE,
    is_paid BOOLEAN NOT NULL DEFAULT FALSE,
    total_amount NUMERIC(12,2) NOT NULL DEFAULT 0.00
);

-- 7. Звонки
CREATE TABLE IF NOT EXISTS call (
    call_id SERIAL PRIMARY KEY,
    client_id INT REFERENCES client(client_id) ON DELETE SET NULL,
    phone_number VARCHAR(20) NOT NULL,
    tariff_id INT REFERENCES tariff(tariff_id) ON DELETE RESTRICT,
    invoice_id INT REFERENCES invoice(invoice_id) ON DELETE SET NULL,
    call_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    destination_city VARCHAR(255) NOT NULL,
    duration_minutes INT NOT NULL CHECK (duration_minutes >= 0),
    call_cost NUMERIC(12,2) NOT NULL DEFAULT 0.00
);

-- Индексы
CREATE INDEX IF NOT EXISTS idx_call_client_date ON call(client_id, call_date);
CREATE INDEX IF NOT EXISTS idx_call_destination_city ON call(destination_city);
CREATE INDEX IF NOT EXISTS idx_call_phone_number ON call(phone_number);
CREATE INDEX IF NOT EXISTS idx_invoice_is_paid ON invoice(is_paid);
CREATE INDEX IF NOT EXISTS idx_invoice_client ON invoice(client_id);
CREATE INDEX IF NOT EXISTS idx_tariff_city_effective ON tariff(city_name, effective_date);

-- Функция обновления суммы счета
CREATE OR REPLACE FUNCTION _update_invoice_total(p_invoice_id INT) RETURNS VOID LANGUAGE plpgsql AS $$
BEGIN
    IF p_invoice_id IS NULL THEN
        RETURN;
    END IF;
    UPDATE invoice
    SET total_amount = COALESCE((
        SELECT SUM(call_cost) FROM call WHERE invoice_id = p_invoice_id
    ), 0.00)
    WHERE invoice_id = p_invoice_id;
END;
$$;

-- Триггер для синхронизации суммы счета
CREATE OR REPLACE FUNCTION trg_call_invoice_total_sync() RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        PERFORM _update_invoice_total(NEW.invoice_id);
        RETURN NEW;
    ELSIF TG_OP = 'UPDATE' THEN
        IF OLD.invoice_id IS DISTINCT FROM NEW.invoice_id THEN
            PERFORM _update_invoice_total(OLD.invoice_id);
            PERFORM _update_invoice_total(NEW.invoice_id);
        ELSE
            PERFORM _update_invoice_total(NEW.invoice_id);
        END IF;
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        PERFORM _update_invoice_total(OLD.invoice_id);
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$;

DROP TRIGGER IF EXISTS call_invoice_sync ON call;
CREATE TRIGGER call_invoice_sync
AFTER INSERT OR UPDATE OR DELETE ON call
FOR EACH ROW EXECUTE FUNCTION trg_call_invoice_total_sync();

-- Тестовые данные
INSERT INTO user_account (login, password_hash, role, full_name)
VALUES
('tech1', crypt('12345', gen_salt('bf')), 'technologist', 'Технолог 1'),
('oper1', crypt('12345', gen_salt('bf')), 'operator', 'Оператор 1'),
('client1', crypt('12345', gen_salt('bf')), 'client', 'Клиент 1')
ON CONFLICT (login) DO NOTHING;