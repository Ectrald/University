-- ============================================================
-- Создание таблиц (нормализованная структура)
-- ============================================================
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- 1. Организации
CREATE TABLE IF NOT EXISTS service_provider (
    provider_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    address TEXT
);

-- 2. Пользователи (единая таблица)
CREATE TABLE IF NOT EXISTS user_account (
    user_id SERIAL PRIMARY KEY,
    login VARCHAR(100) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('technologist', 'operator', 'client'))
);

-- 3. Клиенты
CREATE TABLE IF NOT EXISTS client (
    client_id SERIAL PRIMARY KEY,
    user_id INT UNIQUE REFERENCES user_account(user_id) ON DELETE CASCADE,
    phone_number VARCHAR(20) UNIQUE NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    address TEXT NOT NULL,
    registration_date DATE NOT NULL
);

-- 4. Операторы
CREATE TABLE IF NOT EXISTS operator (
    operator_id SERIAL PRIMARY KEY,
    user_id INT UNIQUE REFERENCES user_account(user_id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL
);

-- 5. Технологи
CREATE TABLE IF NOT EXISTS technologist (
    technologist_id SERIAL PRIMARY KEY,
    user_id INT UNIQUE REFERENCES user_account(user_id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL
);

-- 6. Тарифы
CREATE TABLE IF NOT EXISTS tariff (
    tariff_id SERIAL PRIMARY KEY,
    provider_id INT NOT NULL REFERENCES service_provider(provider_id),
    effective_date DATE NOT NULL,
    city_name VARCHAR(255) NOT NULL,
    standard_rate DECIMAL(10,2) NOT NULL,
    preferential_rate DECIMAL(10,2) NOT NULL,
    UNIQUE (effective_date, city_name)
);

-- 7. Звонки
CREATE TABLE IF NOT EXISTS call (
    call_id SERIAL PRIMARY KEY,
    client_id INT NOT NULL REFERENCES client(client_id),
    tariff_id INT NOT NULL REFERENCES tariff(tariff_id),
    call_date TIMESTAMP NOT NULL DEFAULT NOW(),
    destination_city VARCHAR(255) NOT NULL,
    duration_minutes INT NOT NULL,
    call_cost DECIMAL(10,2) NOT NULL,
    receipt_issue_date DATE,
    is_paid BOOLEAN NOT NULL DEFAULT FALSE,
    payment_date DATE
);

CREATE INDEX IF NOT EXISTS idx_call_client_date ON call(client_id, call_date);
CREATE INDEX IF NOT EXISTS idx_call_destination_city ON call(destination_city);
CREATE INDEX IF NOT EXISTS idx_call_is_paid ON call(is_paid);

-- Тестовые пользователи
INSERT INTO user_account (login, password_hash, role)
VALUES
('tech1', crypt('12345', gen_salt('bf')), 'technologist'),
('oper1', crypt('12345', gen_salt('bf')), 'operator'),
('client1', crypt('12345', gen_salt('bf')), 'client')
ON CONFLICT (login) DO NOTHING;
