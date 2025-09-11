CREATE DATABASE IF NOT EXISTS trade_turnover;
USE trade_turnover;

CREATE TABLE IF NOT EXIST S (
    p VARCHAR(50) PRIMARY KEY,
    name_p VARCHAR(50) NOT NULL,
    status INT NOT NULL,
    city VARCHAR(50) NOT NULL
);

CREATE TABLE IF NOT EXIST P (
    d VARCHAR(50) PRIMARY KEY,
    name_d VARCHAR(50) NOT NULL,
    color VARCHAR(50) NOT NULL,
    size VARCHAR(50) NOT NULL,
    city VARCHAR(50) NOT NULL
);

CREATE TABLE IF NOT EXIST J (
    pr VARCHAR(50) PRIMARY KEY,
    name_pr VARCHAR(50) NOT NULL,
    city VARCHAR(50) NOT NULL
);

CREATE TABLE IF NOT EXIST PSJ( 
    p VARCHAR(50),
    d VARCHAR(50),
    pr VARCHAR(50),
    FOREIGN KEY (p) REFERENSES S(p)
        ON DELETE CASCADE 
        ON UPDATE CASCADE,
    FOREIGN KEY (d) REFERENSES P(d)
        ON DELETE CASCADE 
        ON UPDATE CASCADE,
    FOREIGN KEY (pr) REFERENSES J(pr)
        ON DELETE CASCADE 
        ON UPDATE CASCADE,
    S INT NOT NULL
    PRIMARY KEY(p, d, pr)
);

INSERT INTO S (p, name_p, status, city) VALUES
('П1', 'Петров', 20, 'Москва'),
('П2', 'Синицин', 10, 'Таллин'),
('П3', 'Федоров', 30, 'Таллин'),
('П4', 'Чаянов', 20, 'Минск'),
('П5', 'Петров', 30, 'Киев');

INSERT INTO P (d, name_d, color, size, city) VALUES
('Д1', 'Болт', 'Красный', 12, 'Москва'),
('Д2', 'Гайка', 'Зеленая', 17, 'Минск'),
('Д3', 'Диск', 'Черный', 17, 'Вильнюс'),
('Д4', 'Диск', 'Черный', 14, 'Москва'),
('Д5', 'Корпус', 'Красный', 12, 'Минск'),
('Д6', 'Крышки', 'Красный', 19, 'Москва');

INSERT INTO J (pr, name_pr, city) VALUES 
('ПР1', 'ИПР1', 'Минск'),
('ПР2', 'ИПР2', 'Таллин'),
('ПР3', 'ИПР3', 'Псков'),
('ПР4', 'ИПР4', 'Псков'),
('ПР5', 'ИПР5', 'Москва'),
('ПР6', 'ИПР6', 'Саратов'),
('ПР7', 'ИПР7', 'Москва');

INSERT INTO PSJ (p, d, pr, S) 
VALUES
('П1','Д1', 'ПР1', 200),
('П1','Д1', 'ПР2', 700),
('П2','Д3', 'ПР1', 400),
('П2','Д2', 'ПР2', 200),
('П2','Д3', 'ПР3', 200),
('П2','Д3', 'ПР4', 500),
('П2','Д3', 'ПР5', 600),
('П2','Д3', 'ПР6', 400),
('П2','Д3', 'ПР7', 800),
('П2','Д5', 'ПР2', 100),
('П3','Д3', 'ПР1', 200),
('П3','Д4', 'ПР2', 500),
('П4','Д6', 'ПР3', 300),
('П4','Д6', 'ПР7', 300),
('П5','Д2', 'ПР2', 200),
('П5','Д2', 'ПР4', 100),
('П5','Д5', 'ПР5', 500),
('П5','Д5', 'ПР7', 100),
('П5','Д6', 'ПР2', 200),
('П5','Д1', 'ПР2', 100),
('П5','Д3', 'ПР4', 200),
('П5','Д4', 'ПР4', 800),
('П5','Д5', 'ПР4', 400),
('П5','Д6', 'ПР4', 500);

-- 29 Получить номера проектов, полностью обеспечиваемых поставщиком П1.
SELECT pr
FROM PSJ
GPOUP BY pr
HAVING COUNT(DISTINCT d) = COUNT(DISTINCT CASE WHEN p = 'П1' THEN d END)
   AND COUNT(DISTINCT CASE WHEN p = 'П1' THEN d END) > 0;
-- 14 Получить все такие пары номеров деталей, которые обе поставляются одновременно одним  поставщиком.
SELECT DISTINCT p1.d AS 'деталь 1', p2.d AS 'деталь 2'
FROM PSJ p1
INNER JOIN PSJ p2 ON p1.p == p2.p AND p1.d < p2.d
-- 22 Получить номера проектов, использующих по крайней мере одну деталь, имеющуюся у  поставщика П1. 
SELECT DISTINCT pr
FROM PSJ
WHERE p == 'П1'
-- 11 Получить все пары названий городов, для которых поставщик из первого города обеспечивает проект во втором городе. 
SELECT DISTINCT S.city, J.city
FROM S 
INNER JOIN PSJ ON S.p = PSJ.p
INNER JOIN  J ON PSJ.pr = J.pr
WHERE S.city <> J.city
-- 2 Получить полную информацию обо всех проектах в Лондоне. 
SELECT 
    J.*,
    S.p AS supplier_id,
    S.name_p AS supplier_name,
    S.status AS supplier_status,
    S.city AS supplier_city,
    P.d AS detail_id,
    P.name_d AS detail_name,
    P.color AS detail_color,
    P.size AS detail_size,
    P.city AS detail_city,
    PSJ.S AS quantity
FROM J
LEFT JOIN PSJ ON J.pr = PSJ.pr
LEFT JOIN S ON PSJ.p = S.p
LEFT JOIN P ON PSJ.d = P.d
WHERE J.city = 'Лондон';
-- 4 Получить все отправки, где количество находится в диапазоне от 300 до 750 включительно.
SELECT *
FROM PSJ
WHERE S => 300 AND S <= 750
-- 8 Получить все такие тройки "номера поставщиков-номера деталей-номера проектов", для которых  никакие из двух выводимых поставщиков, деталей и проектов не размещены в одном городе. 
SELECT S.city, P.city, J.city
FROM S
INNER JOIN PSJ ON S.p = PSJ.p
INNER JOIN  J ON PSJ.pr = J.pr
INNER JOIN P ON PSJ.d = P.d
WHERE S.city <> J.city AND S.city <> P.city AND P.city <> J.city
-- 33 Получить все города, в которых расположен по крайней мере один поставщик, одна деталь или один проект
SELECT city FROM S
UNION
SELECT city FROM P
UNION
SELECT city FROM J;
-- 13 Получить номера проектов, обеспечиваемых по крайней мере одним поставщиком не из того же города.
SELECT DISTINCT J.pr
FROM J
INNER JOIN PSJ ON J.pr = PSJ.pr
INNER JOIN S ON PSJ.p = S.p
WHERE S.city <> J.city;
-- 27 Получить номера поставщиков, поставляющих деталь Д1 для некоторого проекта в количестве, большем среднего количества деталей Д1 в поставках для этого проекта.
-- 27 Получить номера поставщиков, поставляющих деталь Д1 для некоторого проекта в количестве, большем среднего количества деталей Д1 в поставках для этого проекта.
SELECT DISTINCT PSJ1.p
FROM PSJ AS PSJ1
WHERE PSJ1.d = 'Д1'
  AND PSJ1.S > (
    SELECT AVG(PSJ2.S)
    FROM PSJ AS PSJ2
    WHERE PSJ2.d = 'Д1'
      AND PSJ2.pr = PSJ1.pr
  );
