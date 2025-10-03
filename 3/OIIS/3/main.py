import cv2
import numpy as np
import matplotlib.pyplot as plt


def process_and_display_image(image_path, image_title):
    """
    Функция для загрузки, обработки и отображения изображения и его гистограмм.
    """
    original_image = cv2.imread(image_path)
    if original_image is None:
        print(f"Ошибка: не удалось загрузить изображение по пути: {image_path}")
        return

    gray_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2GRAY)
    equalized_gray_image = cv2.equalizeHist(gray_image)

    ycrcb_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2YCrCb)
    y_channel, cr_channel, cb_channel = cv2.split(ycrcb_image)
    y_channel_equalized = cv2.equalizeHist(y_channel)
    equalized_ycrcb_image = cv2.merge([y_channel_equalized, cr_channel, cb_channel])
    equalized_color_image = cv2.cvtColor(equalized_ycrcb_image, cv2.COLOR_YCrCb2BGR)

    plt.figure(figsize=(18, 10))
    plt.suptitle(f"Анализ изображения: {image_title}", fontsize=16)

    # Исходное изображение
    plt.subplot(2, 3, 1)
    plt.title("Исходное цветное")
    plt.imshow(cv2.cvtColor(original_image, cv2.COLOR_BGR2RGB))
    plt.axis('off')

    # Гистограмма исходного изображения (ИСПРАВЛЕНО)
    plt.subplot(2, 3, 4)
    plt.title("Гистограмма яркости (до)")
    # Используем именованные аргументы bins и range, чтобы избежать предупреждения
    plt.hist(gray_image.ravel(), bins=256, range=[0, 256], color='darkgray')
    plt.xlabel("Интенсивность")
    plt.ylabel("Количество пикселей")

    # Выровненное серое изображение
    plt.subplot(2, 3, 2)
    plt.title("Выровненное (Grayscale)")
    plt.imshow(equalized_gray_image, cmap='gray')
    plt.axis('off')

    # Гистограмма выровненного изображения (ИСПРАВЛЕНО)
    plt.subplot(2, 3, 5)
    plt.title("Гистограмма яркости (после)")
    # Используем именованные аргументы bins и range
    plt.hist(equalized_gray_image.ravel(), bins=256, range=[0, 256], color='gray')
    plt.xlabel("Интенсивность")
    plt.ylabel("Количество пикселей")

    # Выровненное цветное изображение
    plt.subplot(2, 3, 3)
    plt.title("Выровненное цветное (YCrCb)")
    plt.imshow(cv2.cvtColor(equalized_color_image, cv2.COLOR_BGR2RGB))
    plt.axis('off')

    ax = plt.subplot(2, 3, 6)
    ax.axis('off')

    plt.tight_layout(rect=[0, 0, 1, 0.96])

    # Эта команда покажет окно и остановит выполнение до его закрытия
    plt.show()


# --- Основной блок ---
if __name__ == "__main__":
    dark_image_path = 'dark_image.jpg'
    normal_image_path = 'normal_image.jpg'

    print("Обработка темного изображения...")
    process_and_display_image(dark_image_path, "Темное изображение")

    print("\nОбработка изображения с нормальной яркостью...")
    process_and_display_image(normal_image_path, "Нормальное изображение")

    print("\nОбе картинки были обработаны и показаны последовательно.")