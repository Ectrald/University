import cv2
import numpy as np
import matplotlib.pyplot as plt

# --- 1. Загрузка изображения ---
# Укажите путь к вашему изображению
image_path = 'image.jpg'
# Читаем изображение с помощью OpenCV
# cv2.IMREAD_COLOR загружает изображение в цвете (BGR формат)
original_image = cv2.imread(image_path, cv2.IMREAD_COLOR)

# Проверяем, загрузилось ли изображение
if original_image is None:
    print(f"Ошибка: не удалось загрузить изображение по пути: {image_path}")
else:
    # OpenCV загружает изображения в формате BGR, а Matplotlib ожидает RGB.
    # Конвертируем изображение из BGR в RGB для корректного отображения.
    original_image_rgb = cv2.cvtColor(original_image, cv2.COLOR_BGR2RGB)

    # --- 2. Применение 5 различных фильтров ---

    # Фильтр 1: Преобразование в оттенки серого (Grayscale)
    # Один из самых частых шагов предобработки. Упрощает изображение,
    # оставляя только информацию о яркости.
    gray_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2GRAY)

    # Фильтр 2: Усредняющий фильтр (Box Filter / Averaging)
    # "Размывает" изображение, заменяя каждый пиксель средним значением
    # пикселей в его окрестности (ядро 5x5). Подавляет шум.
    kernel_size = (5, 5)
    averaged_image = cv2.blur(original_image_rgb, kernel_size)

    # Фильтр 3: Гауссовское размытие (Gaussian Blur)
    # Похож на усредняющий, но использует веса из распределения Гаусса.
    # Пиксели ближе к центру ядра имеют больший вес. Дает более "мягкое" размытие.
    # (0, 0) означает, что стандартное отклонение будет вычислено из размера ядра.
    gaussian_blurred_image = cv2.GaussianBlur(original_image_rgb, kernel_size, 0)

    # Фильтр 4: Медианный фильтр (Median Filter)
    # Отлично подходит для удаления "соль и перец" шума.
    # Заменяет каждый пиксель медианным значением пикселей в его окрестности.
    # Размер апертуры (ядра) должен быть нечетным, например, 5.
    median_filtered_image = cv2.medianBlur(original_image_rgb, 5)

    # Фильтр 5: Билатеральный фильтр (Bilateral Filter)
    # Сложный фильтр, который размывает изображение, сохраняя при этом резкие края.
    # Учитывает не только пространственную близость пикселей, но и их схожесть по цвету/интенсивности.
    # d - диаметр окрестности пикселя
    # sigmaColor - чем больше значение, тем более удаленные по цвету пиксели будут смешиваться
    # sigmaSpace - чем больше значение, тем более удаленные друг от друга пиксели будут влиять на результат
    bilateral_filtered_image = cv2.bilateralFilter(original_image_rgb, d=9, sigmaColor=75, sigmaSpace=75)

    # --- 3. Отображение результатов ---
    # Создаем фигуру для отображения 6 изображений (1 оригинал + 5 фильтров)
    plt.figure(figsize=(15, 10))
    plt.suptitle("Предварительная обработка изображений: 5 фильтров", fontsize=16)

    # Словарь с изображениями и их названиями для удобства
    images = {
        "Оригинал (RGB)": original_image_rgb,
        "Оттенки серого": gray_image,
        "Усредняющий фильтр": averaged_image,
        "Гауссовский фильтр": gaussian_blurred_image,
        "Медианный фильтр": median_filtered_image,
        "Билатеральный фильтр": bilateral_filtered_image
    }

    # Цикл для отображения каждого изображения
    for i, (title, image) in enumerate(images.items()):
        plt.subplot(2, 3, i + 1)  # Создаем сетку 2x3 для изображений
        plt.title(title)
        # Если изображение в оттенках серого, используем соответствующую цветовую карту
        if len(image.shape) == 2:
            plt.imshow(image, cmap='gray')
        else:
            plt.imshow(image)
        plt.axis('off') # Отключаем оси координат

    plt.tight_layout(rect=[0, 0, 1, 0.96]) # Корректируем расположение, чтобы заголовок не накладывался
    plt.show()