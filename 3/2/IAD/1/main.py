from sklearn import datasets
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import f1_score
import torch
from torch import nn
import torch.nn.functional as f
import matplotlib.pyplot as plt

wine_dataset = datasets.load_wine()

X, Y = wine_dataset.data, wine_dataset.target
X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size = 0.2, random_state = 42, stratify=Y)

scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

X_train_tensor = torch.FloatTensor(X_train)
X_test_tensor = torch.FloatTensor(X_test)
Y_train_tensor = torch.LongTensor(Y_train)
Y_test_tensor = torch.LongTensor(Y_test)

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
X_train_tensor = X_train_tensor.to(device)
X_test_tensor = X_test_tensor.to(device)
Y_train_tensor = Y_train_tensor.to(device)
Y_test_tensor = Y_test_tensor.to(device)

class NeuralNetwork(nn.Module):
    def __init__(self, input_size, output_size):
        super(NeuralNetwork, self).__init__()
        # y = Wx + b, x - вектор входных данных, W - матрица весов, b - вектор смещений
        self.fc1 = nn.Linear(input_size, 64)
        self.fc2 = nn.Linear(64, 32)
        self.fc3 = nn.Linear(32, output_size)

    def forward(self, x):
        # добавляет нелинейность, без нее был бы максимум 1 слой
        # f(x) = max(0, x)
        x = f.relu(self.fc1(x))
        x = f.relu(self.fc2(x))
        x = self.fc3(x)
        return x

input_size = X_train_tensor.shape[1]  # 13 признаков в датасете wine
output_size = len(torch.unique(Y_train_tensor))  # 3 класса вина

model = NeuralNetwork(input_size, output_size).to(device)

# Adam - адаптирует шаг обучения шаг обучения (lr) для каждого веса сети, опираясь на историю предыдущих градиентов
# градиент - вектор из частных производных, показывает как сильно увеличится потеря при изменении веса
# сначала считается монументум, mt​=β1​⋅mt−1​+(1−β1​)⋅gt​,β1​=0.9 - Это скользящее среднее градиентов.
#Шаг 1: g=+5  → m = 0.1·5  = 0.50
#Шаг 2: g=+4  → m = 0.9·0.50 + 0.1·4 = 0.85
#Шаг 3: g=-1  → m = 0.9·0.85 + 0.1·(-1) = 0.665
# после адаптация шага vt​=β2​⋅vt−1​+(1−β2​)⋅gt2​,β2​=0.999
# Скользящее среднее квадратов градиентов. Если у этого веса градиенты всегда большие → vtv_t
#vt​ большое → шаг уменьшается. Если маленькие → шаг увеличивается.

optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
# Cross Entropy Loss - объединяет Softmax и Cross-Entropy в одну функцию
# берет логиты и переводит их в вероятности, e^логит / сумма(e^логит)
# далее логариф от получившегося числа умножается на -1, значение этого и есть потеря, чем больше тем хуже
criterion = nn.CrossEntropyLoss()

epochs = 100

train_losses, test_losses = [], []
train_accuracies, test_accuracies = [], []

for epoch in range(epochs):
    # Переводим модель в режим обучения
    model.train()
    optimizer.zero_grad()
    outputs = model(X_train_tensor)
    loss = criterion(outputs, Y_train_tensor)
    # запуск алгоритма обратного распространения ошибки, он вычисляет градиенты функции потерь по каждому весу сети
    loss.backward()
    # обновление весов сети на основе вычисленных градиентов
    optimizer.step()
    predicted_train = torch.argmax(outputs, dim=1)
    correct_train = (predicted_train == Y_train_tensor).sum().item()
    train_acc = correct_train / Y_train_tensor.size(0)
    train_losses.append(loss.item())
    train_accuracies.append(train_acc)

    model.eval()  # Переводим модель в режим оценки (отключаются некоторые слои вроде Dropout, если бы они были)

    # Отключаем вычисление градиентов для экономии памяти и времени
    with torch.no_grad():
        test_outputs = model(X_test_tensor)
        test_loss = criterion(test_outputs, Y_test_tensor)

        predicted_test = torch.argmax(test_outputs, dim=1)
        correct_test = (predicted_test == Y_test_tensor).sum().item()
        test_acc = correct_test / Y_test_tensor.size(0)

    # Сохраняем метрики тестирования
    test_losses.append(test_loss.item())
    test_accuracies.append(test_acc)
    y_pred_last = predicted_test  # Сохраняем предсказания для F1

    # Печатаем прогресс каждые 10 эпох
    if (epoch + 1) % 10 == 0:
        print(f'Эпоха [{epoch + 1}/{epochs}] | '
              f'Train Loss: {loss.item():.4f}, Train Acc: {train_acc:.4f} | '
              f'Test Loss: {test_loss.item():.4f}, Test Acc: {test_acc:.4f}')

# 4. Визуализация результатов

plt.figure(figsize=(14, 5))

# График функции потерь
plt.subplot(1, 2, 1)
plt.plot(train_losses, label='Обучающая выборка (Train)')
plt.plot(test_losses, label='Тестовая выборка (Test)')
plt.title('График изменения функции потерь (Loss)')
plt.xlabel('Эпохи')
plt.ylabel('Потери')
plt.legend()
plt.grid(True)

# График точности
plt.subplot(1, 2, 2)
plt.plot(train_accuracies, label='Обучающая выборка (Train)')
plt.plot(test_accuracies, label='Тестовая выборка (Test)')
plt.title('График изменения точности (Accuracy)')
plt.xlabel('Эпохи')
plt.ylabel('Точность')
plt.legend()
plt.grid(True)

plt.tight_layout()
plt.show()

prev_table = """Сравнительная таблица моделей:
                Model  Accuracy  Precision    Recall  F1-score   ROC-AUC
0        DecisionTree  0.939394   0.938889  0.944444  0.940186  0.957341
1                 KNN  1.000000   1.000000  1.000000  1.000000  1.000000
2  LogisticRegression  1.000000   1.000000  1.000000  1.000000  1.000000
3          NaiveBayes  0.939394   0.952381  0.944444  0.944056  0.997354"""

# =============================================================================
# Сравнение нейронной сети с классическими методами
# =============================================================================

# Метрики нейронной сети (последняя эпоха)
nn_accuracy = test_accuracies[-1]
nn_f1 = f1_score(Y_test, y_pred_last.cpu().numpy(), average='weighted')

print(f'\nНейронная сеть: Accuracy = {nn_accuracy:.4f}, F1-score = {nn_f1:.4f}')

# Данные для сравнения (классические методы из prev_table)
classical_models = {
    'DecisionTree': {'accuracy': 0.939394, 'f1': 0.940186},
    'KNN': {'accuracy': 1.000000, 'f1': 1.000000},
    'LogisticRegression': {'accuracy': 1.000000, 'f1': 1.000000},
    'NaiveBayes': {'accuracy': 0.939394, 'f1': 0.944056},
}

# Добавляем нейронную сеть
classical_models['NeuralNetwork'] = {'accuracy': nn_accuracy, 'f1': nn_f1}

# Таблица сравнения
print('\n' + '=' * 60)
print('Сравнительная таблица Accuracy и F1-score:')
print('=' * 60)
print(f'{"Модель":<20} {"Accuracy":<12} {"F1-score":<12}')
print('-' * 60)
for model_name, metrics in classical_models.items():
    print(f'{model_name:<20} {metrics["accuracy"]:<12.4f} {metrics["f1"]:<12.4f}')
print('=' * 60)

# График сравнения
fig, ax = plt.subplots(figsize=(10, 6))

model_names = list(classical_models.keys())
accuracies = [classical_models[m]['accuracy'] for m in model_names]
f1_scores = [classical_models[m]['f1'] for m in model_names]

x = range(len(model_names))
width = 0.35

bars1 = ax.bar([i - width/2 for i in x], accuracies, width, label='Accuracy', color='steelblue')
bars2 = ax.bar([i + width/2 for i in x], f1_scores, width, label='F1-score', color='coral')

ax.set_xlabel('Модель')
ax.set_ylabel('Значение метрики')
ax.set_title('Сравнение классических методов и нейронной сети\n(Accuracy и F1-score)')
ax.set_xticks(x)
ax.set_xticklabels(model_names, rotation=15, ha='right')
ax.legend()
ax.set_ylim(0, 1.05)
ax.grid(axis='y', alpha=0.3)

# Добавляем значения на столбцы
for bars in [bars1, bars2]:
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{height:.3f}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=8)

plt.tight_layout()
plt.show()
