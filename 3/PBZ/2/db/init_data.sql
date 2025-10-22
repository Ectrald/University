CREATE EXTENSION IF NOT EXISTS pgcrypto;

INSERT INTO service_provider (name, address)
VALUES ('МТС', 'Москва, ул. Связи, 10');

INSERT INTO user_account (login, password_hash, role)
VALUES
('tech1', crypt('12345', gen_salt('bf')), 'technologist'),
('oper1', crypt('12345', gen_salt('bf')), 'operator'),
('client1', crypt('12345', gen_salt('bf')), 'client');
