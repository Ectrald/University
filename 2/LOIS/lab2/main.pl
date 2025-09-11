% Лабораторная работа №2
% Тема: Логическое программирование поиска решения задачи
% Автор: [Ваше имя], [Ваша группа], [Год]
% Вариант 14: Три путешественника с велосипедами

% Основной предикат для запуска программы
main :-
    write('Enter cyclist speed (v, km/h): '), read(V), number(V), V > 0,
    write('Enter speed of transporting broken bicycle (y, km/h): '), read(Y), number(Y), Y > 0,
    write('Enter pedestrian speed (w, km/h): '), read(W), number(W), W > 0,
    write('Enter speed of pedestrian with bicycle (u, km/h): '), read(U), number(U), U > 0,
    write('Enter distance between points A and B (km): '), read(Distance), number(Distance), Distance > 0,
    (V >= Y, Y >= W, W >= U ->
        calculate_strategy(V, W, U, Distance, TotalTime, Strategy),
        format('Minimum time: ~2f hours~n', [TotalTime]),
        write('Optimal strategy:'), nl,
        print_strategy(Strategy)
    ;   write('Error: Condition v >= y >= w >= u must hold'), nl, fail).

% Расчет оптимальной стратегии
calculate_strategy(V, W, U, Distance, TotalTime, Strategy) :-
    HalfDistance is Distance / 2,
    % Шаг 1: Все движутся до середины пути
    Time1 is HalfDistance / V, % Время велосипедистов до середины
    Pos1 is HalfDistance,
    format(atom(Desc1), 'All move: cyclists at ~2f km/h, pedestrian at ~2f km/h to position ~2f km', [V, W, Pos1]),
    % Шаг 2: Велосипедист 2 оставляет велосипед, велосипедист 1 доезжает до Б
    Time2 is (Distance - HalfDistance) / V, % Время до конца для велосипедиста 1
    format(atom(Desc2), 'Cyclist 2 leaves bicycle at ~2f km, cyclist 1 reaches B, pedestrian 3 takes broken bicycle', [HalfDistance]),
    % Шаг 3: Пешеход 3 с велосипедом движется от середины до Б
    Time3 is (Distance - HalfDistance) / U, % Время пешехода с велосипедом
    format(atom(Desc3), 'Cyclist 1 and pedestrian 3 with bicycle move to B at ~2f km/h', [U]),
    % Суммарное время
    TotalTime is Time1 + Time2 + Time3,
    % Стратегия как список шагов
    Strategy = [Desc1, Desc2, Desc3].

% Вывод протокола стратегии
print_strategy([]) :- nl.
print_strategy([Move|Rest]) :-
    write(Move), nl,
    print_strategy(Rest).