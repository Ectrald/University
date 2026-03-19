import cv2
import numpy as np
import matplotlib.pyplot as plt

# --- 1. Загрузка и подготовка изображения ---
image_path = 'objects.jpg'
original_image = cv2.imread(image_path)

# Проверяем, загрузилось ли изображение
if original_image is None:
    print(f"Ошибка: не удалось загрузить изображение по пути: {image_path}")
else:
    # Конвертируем изображение в оттенки серого,
    # так как алгоритмы выделения границ работают с интенсивностью, а не с цветом.
    gray_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2GRAY)

    # --- 2. Применение детектора границ Кэнни ---
    # cv2.Canny(image, threshold1, threshold2)
    # threshold1 - Нижний порог для двойной пороговой фильтрации
    # threshold2 - Верхний порог для двойной пороговой фильтрации
    # Рекомендуемое соотношение T2/T1 находится в диапазоне от 2:1 до 3:1.
    low_threshold = 50
    high_threshold = 150
    canny_edges = cv2.Canny(gray_image, low_threshold, high_threshold)

    # --- 3. Для сравнения применим более простой оператор Собеля ---
    # Оператор Собеля вычисляет градиент по осям X и Y

    # Градиент по X
    sobel_x = cv2.Sobel(gray_image, cv2.CV_64F, 1, 0, ksize=5)
    # Градиент по Y
    sobel_y = cv2.Sobel(gray_image, cv2.CV_64F, 0, 1, ksize=5)

    # Вычисляем абсолютные значения градиентов
    abs_sobel_x = cv2.convertScaleAbs(sobel_x)
    abs_sobel_y = cv2.convertScaleAbs(sobel_y)

    # Объединяем градиенты для получения общего контура
    sobel_combined = cv2.addWeighted(abs_sobel_x, 0.5, abs_sobel_y, 0.5, 0)

    # --- 4. Отображение результатов ---
    plt.figure(figsize=(18, 6))
    plt.suptitle("Сегментация изображений: выделение границ", fontsize=16)

    # Исходное изображение
    plt.subplot(1, 3, 1)
    plt.title("Исходное изображение")
    plt.imshow(cv2.cvtColor(original_image, cv2.COLOR_BGR2RGB))
    plt.axis('off')

    # Результат оператора Собеля
    plt.subplot(1, 3, 2)
    plt.title("Оператор Собеля")
    plt.imshow(sobel_combined, cmap='gray')
    plt.axis('off')

    # Результат детектора Кэнни
    plt.subplot(1, 3, 3)
    plt.title("Детектор границ Кэнни")
    plt.imshow(canny_edges, cmap='gray')
    plt.axis('off')

    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.show()