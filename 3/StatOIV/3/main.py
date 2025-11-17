import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import RobustScaler
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, roc_auc_score, confusion_matrix
)

from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB

# ======================================================
#   1. Загрузка и предобработка данных
# ======================================================

df = pd.read_csv("winequality-red.csv")

print("Размер датасета:", df.shape)
print(df.dtypes)
print(df.info())

# 1.1 Пропуски
df = df.dropna()

# 1.2 Дубликаты
df = df.drop_duplicates()

# 1.3 Визуализация выбросов (опционально)
plt.figure(figsize=(18, 12))
df.boxplot(figsize=(18, 12))
plt.title("Boxplot признаков")
plt.show()

# 1.4 Удаление выбросов по IQR
numerical_cols = df.columns.drop("quality")
df_filtered = df.copy()

for col in numerical_cols:
    Q1 = df[col].quantile(0.25)
    Q3 = df[col].quantile(0.75)
    IQR = Q3 - Q1
    low = Q1 - 1.5 * IQR
    high = Q3 + 1.5 * IQR
    df_filtered = df_filtered[(df_filtered[col] >= low) & (df_filtered[col] <= high)]

print("До выбросов:", len(df))
print("После выбросов:", len(df_filtered))

# ======================================================
#   2. Создание 3-классовой целевой переменной
# ======================================================

df_filtered["quality_cat"] = pd.cut(
    df_filtered["quality"],
    bins=[0, 5, 6, 10],
    labels=[0, 1, 2]
).astype(int)

print(df_filtered["quality_cat"].value_counts())

# Удаляем старую метку
df_filtered = df_filtered.drop(columns=["quality"])

# ======================================================
#   3. Разделение выборки
# ======================================================

X = df_filtered.drop(columns=["quality_cat"])
y = df_filtered["quality_cat"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# Масштабирование
scaler = RobustScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# ======================================================
#   4. Обучение моделей
# ======================================================

models = {
    "DecisionTree": DecisionTreeClassifier(random_state=42),
    "KNN": KNeighborsClassifier(n_neighbors=5),
    "LogisticRegression": LogisticRegression(max_iter=500),
    "NaiveBayes": GaussianNB()
}

results = []

# ======================================================
#   5. Оценка моделей
# ======================================================

def evaluate_model(name, model, X_train, y_train, X_test, y_test):
    model.fit(X_train, y_train)
    preds = model.predict(X_test)

    acc = accuracy_score(y_test, preds)
    prec = precision_score(y_test, preds, average="macro")
    rec = recall_score(y_test, preds, average="macro")
    f1 = f1_score(y_test, preds, average="macro")

    # ROC-AUC OvR
    try:
        proba = model.predict_proba(X_test)
        roc = roc_auc_score(y_test, proba, multi_class="ovr")
    except:
        roc = np.nan

    results.append([name, acc, prec, rec, f1, roc])

    # Матрица ошибок
    cm = confusion_matrix(y_test, preds)
    plt.figure(figsize=(5, 4))
    sns.heatmap(cm, annot=True, cmap="Blues", fmt="d")
    plt.title(f"Confusion Matrix — {name}")
    plt.xlabel("Предсказанный класс")
    plt.ylabel("Истинный класс")
    plt.show()


for name, model in models.items():
    evaluate_model(name, model, X_train_scaled, y_train, X_test_scaled, y_test)

# ======================================================
#   6. Таблица результатов
# ======================================================

results_df = pd.DataFrame(
    results,
    columns=["Model", "Accuracy", "Precision", "Recall", "F1-score", "ROC-AUC"]
)

print("\nСравнительная таблица моделей:")
print(results_df)
