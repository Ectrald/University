-- 29 Получить номера проектов, полностью обеспечиваемых поставщиком П1.
SELECT pr
FROM PSJ
GROUP BY pr
HAVING COUNT(DISTINCT d) = COUNT(DISTINCT CASE WHEN p = 'П1' THEN d END)
   AND COUNT(DISTINCT CASE WHEN p = 'П1' THEN d END) > 0;
-- 14 Получить все такие пары номеров деталей, которые обе поставляются одновременно одним  поставщиком.
SELECT DISTINCT p1.d AS "деталь 1", p2.d AS "деталь 2"
FROM PSJ p1
INNER JOIN PSJ p2 ON p1.p = p2.p AND p1.d < p2.d;
-- 22 Получить номера проектов, использующих по крайней мере одну деталь, имеющуюся у  поставщика П1. 
WITH details as (
SELECT d
FROM PSJ
WHERE p = 'П1'
)
SELECT DISTINCT pr
FROM PSJ
INNER JOIN details ON PSJ.d = details.d
-- 11 Получить все пары названий городов, для которых поставщик из первого города обеспечивает проект во втором городе. 
SELECT DISTINCT S.city, J.city
FROM S 
INNER JOIN PSJ ON S.p = PSJ.p
INNER JOIN  J ON PSJ.pr = J.pr
WHERE S.city <> J.city;
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
WHERE J.city = 'Москва';
-- 4 Получить все отправки, где количество находится в диапазоне от 300 до 750 включительно.
SELECT *
FROM PSJ
WHERE S >= 300 AND S <= 750;
-- 8 Получить все такие тройки "номера поставщиков-номера деталей-номера проектов", для которых  никакие из двух выводимых поставщиков, деталей и проектов не размещены в одном городе. 
SELECT S.city, P.city, J.city
FROM S
INNER JOIN PSJ ON S.p = PSJ.p
INNER JOIN  J ON PSJ.pr = J.pr
INNER JOIN P ON PSJ.d = P.d
WHERE S.city <> J.city AND S.city <> P.city AND P.city <> J.city;
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
SELECT DISTINCT PSJ1.p
FROM PSJ AS PSJ1
WHERE PSJ1.d = 'Д1'
  AND PSJ1.S > (
    SELECT AVG(PSJ2.S)
    FROM PSJ AS PSJ2
    WHERE PSJ2.d = 'Д1'
      AND PSJ2.pr = PSJ1.pr
  );
