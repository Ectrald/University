CREATE DATABASE IF NOT EXIST MTC;
USE MTC;

CREATE TABLE IF NOT EXIST clienst(
    fio VARCHAR(100),
    phone VARCHAR(50),
    adress VARCHAR(50), 
    date TIMESTAMP
);
CREATE TABLE IF NOT EXIST services(
    date TIMESTAMP,
    city VARCHAR(50),
    one_minute_price FLOAT,
    discounted_cost FLOAT
);

CREATE TABLE IF NOT EXIST calls(
    date TIMESTAMP,
    city VARCHAR(50),
    interlocutor_city VARCHAR(50),
    phone VARCHAR(50),
    duration FLOAT,
    pay VARCHAR(50)
);
