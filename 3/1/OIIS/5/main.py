import cv2
import numpy as np
import matplotlib.pyplot as plt

# --- 1. Загрузка изображений стереопары ---
# Укажите пути к вашим изображениям
left_image_path = 'left_eye.jpg'
right_image_path = 'right_eye.jpg'

# Читаем изображения с помощью OpenCV
left_image = cv2.imread(left_image_path)
right_image = cv2.imread(right_image_path)

# --- 2. Проверка и подготовка изображений ---
if left_image is None or right_image is None:
    print("Ошибка: одно или оба изображения не найдены. Проверьте пути:")
    print(f"- Левое: {left_image_path}")
    print(f"- Правое: {right_image_path}")
else:
    print("Изображения успешно загружены. Создание анаглифа...")

    # Для корректного совмещения каналов изображения должны быть одного размера.
    # Приведем размер правого изображения к размеру левого.
    height, width, _ = left_image.shape
    right_image = cv2.resize(right_image, (width, height))

    # --- 3. Создание анаглифного изображения ---

    # Разделяем изображения на B, G, R каналы. OpenCV хранит их в таком порядке.
    b_left, g_left, r_left = cv2.split(left_image)
    b_right, g_right, r_right = cv2.split(right_image)

    # Создаем анаглиф:
    # Красный канал берем из левого изображения.
    # Синий и зеленый каналы - из правого изображения.
    anaglyph_image = cv2.merge([b_right, g_right, r_left])

    # --- 4. Отображение результатов ---
    plt.figure(figsize=(20, 7))
    plt.suptitle("Создание стереоскопического (анаглифного) изображения", fontsize=16)

    # Исходное изображение для левого глаза
    plt.subplot(1, 3, 1)
    plt.title("Левый ракурс")
    plt.imshow(cv2.cvtColor(left_image, cv2.COLOR_BGR2RGB))
    plt.axis('off')

    # Исходное изображение для правого глаза
    plt.subplot(1, 3, 2)
    plt.title("Правый ракурс")
    plt.imshow(cv2.cvtColor(right_image, cv2.COLOR_BGR2RGB))
    plt.axis('off')

    # Результат - анаглифное изображение
    plt.subplot(1, 3, 3)
    plt.title("Анаглиф (для просмотра в Red-Cyan очках)")
    plt.imshow(cv2.cvtColor(anaglyph_image, cv2.COLOR_BGR2RGB))
    plt.axis('off')

    plt.tight_layout(rect=[0, 0, 1, 0.95])

    # Сохраняем результат в файл
    cv2.imwrite("anaglyph_result.jpg", anaglyph_image)
    print("Результат сохранен в файл 'anaglyph_result.jpg'")

    plt.show()