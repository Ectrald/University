import torch
import torch.nn as nn
import torch.optim as optim
import torchvision
import torchvision.transforms as transforms
from torch.utils.data import DataLoader, Subset
import numpy as np
import matplotlib.pyplot as plt

# Установим device, чтобы использовать GPU (если есть) или CPU. Платформа PyTorch автоматически направляет тензоры на нужное устройство.
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')


# ==========================================
# 0. ОБЩИЕ ФУНКЦИИ И ПРЕОБРАЗОВАНИЯ
# ==========================================

# БАЗОВЫЕ ПРЕОБРАЗОВАНИЯ
# Здесь мы НЕ применяем аугментацию. Только перевод в тензор и нормализация.
# Нормализация: вычитает математическое ожидание (mean=0.1307) и делит на стандартное отклонение (std=0.3081).
# Эти числа - известные предвычисленные статистики для сета MNIST. Нормализация помогает обучению сети быть более стабильным.
base_transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize((0.1307,), (0.3081,))
])

# ПРЕОБРАЗОВАНИЯ С АУГМЕНТАЦИЕЙ
# Аугментация предотвращает переобучение, генерируя немного измененные примеры изображений, обогащая датасет.
# Выбраны именно Resize/RandomCrop/RandomRotation, так как для рукописных цифр (MNIST) операции вроде зеркального
# отражения (Flip) или смены цветов (ColorJitter) приведут к искажению смысла цифр (например "6" станет как "9").
aug_transform = transforms.Compose([
    # Добавляет 2 пикселя "отсупа" вокруг, затем случайно вырезает 28x28 (стандартный размер MNIST).
    # Это позволяет симулировать небольшие сдвиги цифры на картинке.
    transforms.RandomCrop(28, padding=2),
    # Поворачивает изображение на случайный угол в диапазоне [-10, +10] градусов.
    # Параметры которые можно было бы задать, но мы опустили:
    # resample=False (определяет алгоритм интерполяции)
    # expand=False (определяет, нужно ли расширять картинку, чтобы вместить повернутую версию, мы оставляем исходный размер)
    transforms.RandomRotation(degrees=10),
    # Преобразует объект PIL Image (или numpy массив) в многомерный тензор torch.Tensor и нормализует пиксели к диапазону [0.0, 1.0].
    transforms.ToTensor(),
    transforms.Normalize((0.1307,), (0.3081,))
])


def get_data_loaders(train_transform, test_transform, batch_size=64):
    """
    Функция для загрузки данных MNIST с нужными трансформациями
    """
    # Загружаем полный обучающий датасет двумя способами (с разными трансформациями).
    # Параметр root - папка, куда сохраняются скачанные файлы.
    # download=True - скачивать ли датасет из интернета при отсутствии.
    train_dataset_full = torchvision.datasets.MNIST(root='./data', train=True, transform=train_transform, download=True)
    val_dataset_full = torchvision.datasets.MNIST(root='./data', train=True, transform=test_transform, download=True)
    
    # Загружаем тестовую часть (официально отложенные 10,000 картинок).
    test_dataset = torchvision.datasets.MNIST(root='./data', train=False, transform=test_transform, download=True)

    # Разделение на тренировочную и валидационную выборку (например, 50,000 / 10,000).
    # Мы делаем случайное перемешивание индексов для честного распределения данных.
    indices = list(range(len(train_dataset_full)))
    np.random.seed(42) # Фиксируем генератор случайных чисел для воспроизводимости
    np.random.shuffle(indices)

    train_indices = indices[:50000]
    val_indices = indices[50000:]

    # Subset берет подвыборку по индексам из изначального датасета.
    train_subset = Subset(train_dataset_full, train_indices)
    val_subset = Subset(val_dataset_full, val_indices)

    # DataLoader (Загрузчик Данных) - итератор, который группирует по batch_size элементов для батчированного обучения.
    # batch_size=64: сеть будет скармливать (обрабатывать) по 64 картинки за раз во время прямого и обратного прохода.
    # shuffle=True (для трейна): перемешивает порядок внутри трейна каждую новую эпоху.
    # num_workers=0: количество подпроцессов ОС для подгрузки изображений. Отключен (0), так как датасет мал и работает быстро. Параметр полезен на огромных файловых датасетах (ImageNet).
    train_ld = DataLoader(dataset=train_subset, batch_size=batch_size, shuffle=True)
    val_ld = DataLoader(dataset=val_subset, batch_size=batch_size, shuffle=False)
    test_ld = DataLoader(dataset=test_dataset, batch_size=batch_size, shuffle=False)
    
    return train_ld, val_ld, test_ld


# ==========================================
# БАЗОВАЯ МОДЕЛЬ (BASELINE)
# ==========================================

class BaselineCNN(nn.Module):
    """
    Простая (базовая) модель, выполняющая все минимальные требования.
    Один блок свертки с BatchNorm и MaxPool, один Dropout, один скрытый Linear.
    """
    def __init__(self):
        super(BaselineCNN, self).__init__()
        
        # СВЕРТОЧНЫЙ СЛОЙ
        # Выполняет операцию извлечения локальных признаков (граней, углов, паттернов).
        # in_channels=1 (ч/б картинка)
        # out_channels=16 (создаст 16 различных фильтров-ядер)
        # kernel_size=3 (размер окна 3x3 пикселя)
        # stride=1 (шаг сдвига ядра)
        # padding=1 (сохраняет размер картинки 28x28 после свертки)
        # bias=False (не используем добавление сдвига, так как следом идет BatchNorm).
        self.conv1 = nn.Conv2d(in_channels=1, out_channels=16, kernel_size=3, stride=1, padding=1, bias=False)
        
        # Пакетная нормализация центрирует результаты свертки (mean=0, std=1) по каждому батчу.
        # Это защищает сеть от "взрыва градиентов".
        self.bn1 = nn.BatchNorm2d(16)
        
        # Функция активации ReLU (оставляет только положительные значения)
        self.relu1 = nn.ReLU()
        
        # MaxPooling: Уменьшает размер картинки в 2 раза из 28x28 в 14x14 пикселей (при 16 каналах)
        self.pool = nn.MaxPool2d(kernel_size=2, stride=2)
        
        # ПОЛНОСВЯЗНАЯ ЧАСТЬ
        # После пулинга: пространственный размер 14x14. Общее число нейронов: 16 каналов * 14 * 14 = 3136
        self.fc1 = nn.Linear(3136, 64)
        self.relu2 = nn.ReLU()
        
        # Обычный Dropout. Случайно обнуляет 30% связей (p=0.3) внутри полносвязного слоя.
        # Чтобы ослабить "зубрежку".
        self.dropout = nn.Dropout(p=0.3)
        
        # Выходной слой на 10 классов
        self.fc2 = nn.Linear(64, 10)

    def forward(self, x):
        """Прямой проход - алгоритм прохождения картинки."""
        x = self.conv1(x)
        x = self.bn1(x)
        x = self.relu1(x)
        x = self.pool(x)
        
        # Разворачиваем 4D тензор в плоский вектор
        x = torch.flatten(x, 1)
        
        x = self.fc1(x)
        x = self.relu2(x)
        x = self.dropout(x)
        
        # Возвращаем "сырые" значения логитов.
        out = self.fc2(x)
        return out


# ==========================================
# УЛУЧШЕННАЯ МОДЕЛЬ 
# ==========================================

class ImprovedCNN(nn.Module):
    """
    Улучшенная глубокая модель. 
    Больше слоев, фильтров (до 64), добавлен Spatial Dropout перед Linear-частью, добавлены дополнительные активации.
    Сеть более мощная, чтобы извлекать больше сложных паттернов из увеличенного аугментацией датасета.
    """
    def __init__(self):
        super(ImprovedCNN, self).__init__()
        
        # БЛОК 1: Извлекает первичные признаки
        # Здесь мы увеличиваем число фильтров со старта до 32.
        self.conv1 = nn.Conv2d(1, 32, kernel_size=3, padding=1, bias=False)
        self.bn1 = nn.BatchNorm2d(32)
        self.relu1 = nn.ReLU(inplace=True) # inplace=True немного экономит VRAM, перезаписывая тензор в той же памяти.
        self.pool1 = nn.MaxPool2d(2, 2)
        
        # БЛОК 2: Еще глубже извлекаем уже более абстрактные характеристики.
        # Увеличиваем число каналов еще в 2 раза - до 64 фильтров.
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1, bias=False)
        self.bn2 = nn.BatchNorm2d(64)
        self.relu2 = nn.ReLU(inplace=True)
        # Второй раз пулинг уменьшит картинку с 14x14 до 7x7. Общий объем: 64 канала по 7x7 пикселей.
        self.pool2 = nn.MaxPool2d(2, 2)
        
        # РЕГУЛЯРИЗАЦИЯ И КЛАССИФИКАТОР
        # Spatial Dropout (Dropout2d). Отключает с вероятностью p=0.25 целые плоские "карты признаков" (каналы), а не просто пиксели.
        # Это заставляет сеть искать разные признаки по всей площади, не зацикливаясь на одном конкретном.
        self.dropout2d = nn.Dropout2d(p=0.25)
        
        # Linear: 64 канала * 7 высоты * 7 ширины = 3136 входов. Выход 128 "смыслов"
        self.fc1 = nn.Linear(64 * 7 * 7, 128)
        
        # По требованиям задания 2 мы можем применять Batch Norm и после Linear слоев для ускорения.
        self.bn_fc = nn.BatchNorm1d(128) 
        self.relu3 = nn.ReLU(inplace=True)
        
        # Усиленный классический Dropout, отрубаем половину (p=0.5) весовых связей, так как сеть очень "глубокая".
        self.dropout = nn.Dropout(p=0.5)
        
        # Финальный выходной слой на 10 классов (цифры 0-9)
        self.fc2 = nn.Linear(128, 10)

    def forward(self, x):
        # Блок 1
        x = self.pool1(self.relu1(self.bn1(self.conv1(x))))
        # Блок 2
        x = self.pool2(self.relu2(self.bn2(self.conv2(x))))
        
        x = self.dropout2d(x)
        x = torch.flatten(x, 1)
        
        # Классификатор
        x = self.dropout(self.relu3(self.bn_fc(self.fc1(x))))
        out = self.fc2(x)
        
        # Аналогично возвращаем "сырые логиты" без ручного Softmax в конце, 
        # так как CrossEntropyLoss сделает это сама.
        return out


# ==========================================
# 3. ФУНКЦИЯ ОБУЧЕНИЯ (ОБЩАЯ)
# ==========================================

def train_model(model, train_loader, val_loader, num_epochs, lr, use_scheduler=False, weight_decay=0.0):
    """
    Универсальная функция обучения, которая подойдет как для Baseline, так и для Improved (улучшенной).
    """
    model = model.to(device)
    
    # CrossEntropyLoss вычисляет ошибку между предсказанными сетью выводами и правильными метками класса.
    criterion = nn.CrossEntropyLoss()
    
    # Адаптивный оптимизатор: Adam. Он накапливает историю градиентов (моментум) 
    # и индивидуально подгоняет learning rate для каждого веса.
    # weight_decay добавляет штраф L2.
    optimizer = optim.Adam(model.parameters(), lr=lr, weight_decay=weight_decay)
    
    # Планировщик скорости обучения. (Scheduler). 
    # Подстраивает lr во время обучения. Применяется по требованию из Задания 2.
    # Если Точность на валидации (mode='max') не растет (patience=2), то он снизит скорость (lr) в два раза (factor=0.5).
    scheduler = None
    if use_scheduler:
        scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='max', factor=0.5, patience=2)

    train_losses = []
    val_accuracies = []
    
    # Настройки для Early Stopping и сохранения лучшей модели
    best_val_acc = 0.0
    early_stop_patience = 4 # Ранняя остановка, если метрика перестанет расти
    patience_counter = 0 
    
    # Файл, куда сохранятся лучшие веса
    save_path = f"best_{model.__class__.__name__}.pth"
    
    for epoch in range(num_epochs):
        # 1. ТРЕНИРОВКА. 
        # Метод model.train() переводит BatchNorm и Dropout в "активный режим".
        model.train()
        running_loss = 0.0
        
        for images, labels in train_loader:
            images, labels = images.to(device), labels.to(device)
            
            # Обнуляем матрицу старых градиентов
            optimizer.zero_grad()
            
            # Высчитываем предсказания и ошибку (Прямой проход)
            outputs = model(images)
            loss = criterion(outputs, labels)
            
            # Вычисляет градиенты каждого параметра сети (Обратное распространение)
            loss.backward()
            
            # Оптимизатор "двигает" веса на 1 шаг (Шаг оптимизации)
            optimizer.step()
            
            running_loss += loss.item() * images.size(0)
            
        epoch_loss = running_loss / len(train_loader.dataset)
        train_losses.append(epoch_loss)
        
        # 2. ВАЛИДАЦИЯ.
        # Метод eval() отключает Dropout и фиксирует скользящие средние BatchNorm.
        model.eval()
        correct = 0
        total = 0
        
        # torch.no_grad() блокирует вычисление градиентов. Экономит оперативную память и ускоряет процесс проверки.
        with torch.no_grad():
            for images, labels in val_loader:
                images, labels = images.to(device), labels.to(device)
                outputs = model(images)
                
                # Ищем самую большую вероятность выхода, номер этого нейрона = предсказанный класс.
                _, predicted = torch.max(outputs.data, 1)
                total += labels.size(0)
                correct += (predicted == labels).sum().item()
                
        val_acc = 100.0 * correct / total
        val_accuracies.append(val_acc)
        
        print(f"[{model.__class__.__name__}] Эпоха [{epoch+1}/{num_epochs}], Train Loss: {epoch_loss:.4f}, Val Acc: {val_acc:.2f}%")
        
        # Отдаем валидационную метрику Планировщику для принятия решений
        if use_scheduler:
            scheduler.step(val_acc)
            
        # Логика Early Stopping и сохранения
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            patience_counter = 0
            # Сохраняем лучшие "веса" (структуру state_dict)
            torch.save(model.state_dict(), save_path)
        else:
            patience_counter += 1
            if patience_counter >= early_stop_patience:
                print(f"Early Stopping! Модель больше не может улучшить скор за последние {early_stop_patience} эпох(-и).")
                break
                
    return train_losses, val_accuracies, save_path

def evaluate_model(model_cls, weights_path, test_loader):
    """
    Оценивает обученную модель ТОЛЬКО один раз на закрытой тестовой выборке.
    """
    model = model_cls().to(device)
    # Загружаем сохраненные лучшие веса эпохи, weights_only=True для безопасности.
    model.load_state_dict(torch.load(weights_path, weights_only=True))
    model.eval()
    
    correct = 0
    total = 0
    with torch.no_grad():
        for images, labels in test_loader:
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
            
    return 100.0 * correct / total


# ==========================================
# 4. ГЛАВНЫЙ БЛОК: СРАВНЕНИЕ ДВУХ МОДЕЛЕЙ
# ==========================================

if __name__ == '__main__':
    print(f"===================================")
    print(f"Запуск на устройстве: {device}")
    print(f"===================================\n")
    
    num_epochs = 15
    batch_size = 64
    
    # ----------------------------------------------------
    # Baseline (без аугментации, простая сеть)
    # ----------------------------------------------------
    print(">>> СТАРТ: Обучение Baseline модели (без аугментации) <<<")
    
    # Вызываем ДатаЛоадеры с функцией базовых трансформаций (без кропов/зума)
    train_ld_base, val_ld_base, test_ld_base = get_data_loaders(base_transform, base_transform, batch_size)
    
    baseline_model = BaselineCNN()
    
    # Обучаем Baseline: без scheduler, без L2-регуляризации(weight_decay=0.0)
    base_train_losses, base_val_accs, base_weights = train_model(
        baseline_model, train_ld_base, val_ld_base, 
        num_epochs=num_epochs, lr=0.001, use_scheduler=False, weight_decay=0.0
    )
    
    # Оценка
    base_test_acc = evaluate_model(BaselineCNN, base_weights, test_ld_base)
    print(f"Итоговая точность на тесте (Baseline): {base_test_acc:.2f}%\n")


    # ----------------------------------------------------
    # Улучшенная модель (с аугментацией и доп. слоями)
    # ----------------------------------------------------
    print(">>> СТАРТ: Обучение Улучшенной модели (с аугментацией) <<<")
    
    # Вызываем ДатаЛоадеры с функцией продвинутых трансформаций (aug_transform) для тренировочной выборки
    train_ld_aug, val_ld_aug, test_ld_aug = get_data_loaders(aug_transform, base_transform, batch_size)
    
    improved_model = ImprovedCNN()
    
    # Обучаем Улучшенную модель: включаем planning-Scheduler(use_scheduler=True) и L2-penalty(weight_decay=1e-4)
    imp_train_losses, imp_val_accs, imp_weights = train_model(
        improved_model, train_ld_aug, val_ld_aug, 
        num_epochs=num_epochs, lr=0.001, use_scheduler=True, weight_decay=1e-4
    )
    
    # Оценка
    imp_test_acc = evaluate_model(ImprovedCNN, imp_weights, test_ld_aug)
    print(f"Итоговая точность на тесте (Улучшенная): {imp_test_acc:.2f}%\n")
    
    
    # ----------------------------------------------------
    # ВЫВОД ГРАФИКОВ
    # ----------------------------------------------------
    # Строим двойные графики, чтобы в отчете можно было показать наглядное отличие
    print(">>> Построение графиков для сравнения... <<<")
    plt.figure(figsize=(12, 5))

    plt.subplot(1, 2, 1)
    
    # Если Early Stopping остановил модель раньше (длина графиков не равна кол-ву num_epochs),
    # обрезаем до текущих длин списков, чтобы Matplotlib не упал с ошибкой
    plt.plot(range(1, len(base_train_losses) + 1), base_train_losses, label='Baseline Loss', color='red', linestyle='--')
    plt.plot(range(1, len(imp_train_losses) + 1), imp_train_losses, label='Improved Loss (with Augmentation)', color='blue')
    plt.title('Функция потерь (Train Loss)')
    plt.xlabel('Эпохи')
    plt.ylabel('Loss')
    plt.grid(True)
    plt.legend()

    plt.subplot(1, 2, 2)
    plt.plot(range(1, len(base_val_accs) + 1), base_val_accs, label=f'Baseline Val (Test: {base_test_acc:.2f}%)', color='red', linestyle='--')
    plt.plot(range(1, len(imp_val_accs) + 1), imp_val_accs, label=f'Improved Val (Test: {imp_test_acc:.2f}%)', color='blue')
    plt.title('Точность на Валидации (Accuracy)')
    plt.xlabel('Эпохи')
    plt.ylabel('Accuracy (%)')
    plt.grid(True)
    plt.legend()

    plt.tight_layout()
    plt.savefig('comparison_results.png')
    print("Графики сохранены в 'comparison_results.png'")
    # В консоли может быть не открыть окно matplotlib, 
    # но картинка comparison_results.png точно сохранится рядом со скриптом.
    plt.show()
