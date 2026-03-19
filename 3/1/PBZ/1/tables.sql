
CREATE TABLE S (
    p VARCHAR(50) PRIMARY KEY,
    name_p VARCHAR(50) NOT NULL,
    status INT NOT NULL,
    city VARCHAR(50) NOT NULL
);

CREATE TABLE P (
    d VARCHAR(50) PRIMARY KEY,
    name_d VARCHAR(50) NOT NULL,
    color VARCHAR(50) NOT NULL,
    size VARCHAR(50) NOT NULL,
    city VARCHAR(50) NOT NULL
);

CREATE TABLE J (
    pr VARCHAR(50) PRIMARY KEY,
    name_pr VARCHAR(50) NOT NULL,
    city VARCHAR(50) NOT NULL
);

CREATE TABLE PSJ( 
    p VARCHAR(50),
    d VARCHAR(50),
    pr VARCHAR(50),
    FOREIGN KEY (p) REFERENCES S(p)
        ON DELETE CASCADE 
        ON UPDATE CASCADE,
    FOREIGN KEY (d) REFERENCES P(d)
        ON DELETE CASCADE 
        ON UPDATE CASCADE,
    FOREIGN KEY (pr) REFERENCES J(pr)
        ON DELETE CASCADE 
        ON UPDATE CASCADE,
    S INT NOT NULL,
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
