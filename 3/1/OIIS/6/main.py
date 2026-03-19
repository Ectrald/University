import cv2
import numpy as np
import matplotlib.pyplot as plt

# --- 1. Загрузка изображений ---
# Загружаем основное изображение (карту)
map_image = cv2.imread('map.jpg')
# Загружаем изображение-шаблон (то, что ищем)
template_image = cv2.imread('template.jpg')

# Проверяем, загрузились ли изображения
if map_image is None or template_image is None:
    print("Ошибка: одно или оба изображения не найдены. Проверьте пути.")
else:
    # --- 2. Подготовка изображений ---
    # Для более надежного сопоставления лучше работать с изображениями в оттенках серого
    map_gray = cv2.cvtColor(map_image, cv2.COLOR_BGR2GRAY)
    template_gray = cv2.cvtColor(template_image, cv2.COLOR_BGR2GRAY)

    # Получаем размеры шаблона (ширину и высоту)
    w, h = template_gray.shape[::-1]

    # --- 3. Сопоставление с шаблоном ---
    # cv2.matchTemplate(где_ищем, что_ищем, метод_сравнения)
    # TM_CCOEFF_NORMED - один из лучших методов, дает результат от -1.0 до 1.0
    # Чем ближе к 1.0, тем большее совпадение.
    result = cv2.matchTemplate(map_gray, template_gray, cv2.TM_CCOEFF_NORMED)

    # Находим координаты точки с максимальным совпадением
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

    # max_loc - это координаты верхнего левого угла найденной области
    top_left = max_loc
    # Вычисляем координаты правого нижнего угла
    bottom_right = (top_left[0] + w, top_left[1] + h)

    # --- 4. Визуализация результата ---
    # Рисуем прямоугольник на цветном оригинальном изображении карты
    # Копируем изображение, чтобы не изменять оригинал
    map_with_rectangle = map_image.copy()
    cv2.rectangle(map_with_rectangle, top_left, bottom_right, (0, 0, 255),
                  3)  # Красный прямоугольник толщиной 3 пикселя

    # Отображаем результат
    plt.figure(figsize=(15, 10))
    plt.suptitle("Распознавание объекта на карте методом сопоставления с шаблоном", fontsize=16)

    # Исходная карта
    plt.subplot(1, 2, 1)
    plt.title("Исходная карта и шаблон для поиска")
    # Отображаем карту
    plt.imshow(cv2.cvtColor(map_image, cv2.COLOR_BGR2RGB))
    # Отображаем шаблон поверх карты для наглядности (в углу)
    # Создаем маленькую ось внутри текущей
    ax = plt.gca()
    inset_ax = ax.inset_axes([0.05, 0.7, 0.25, 0.25])  # [x, y, width, height]
    inset_ax.imshow(cv2.cvtColor(template_image, cv2.COLOR_BGR2RGB))
    inset_ax.set_title("Шаблон")
    inset_ax.axis('off')

    # Карта с найденным объектом
    plt.subplot(1, 2, 2)
    plt.title("Результат: найденный объект")
    plt.imshow(cv2.cvtColor(map_with_rectangle, cv2.COLOR_BGR2RGB))
    plt.axis('off')

    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.show()

    # Выводим информацию в консоль
    print(f"Объект найден с уверенностью: {max_val:.2f}")
    print(f"Координаты верхнего левого угла: {top_left}")
    print(f"Координаты правого нижнего угла: {bottom_right}")