import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from sklearn import preprocessing
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import Ridge
EPS = 1e-9
red_wine_quality = pd.read_csv("winequality-red.csv")
# Проверка	размерности
print(f"Размер	датасета:	{red_wine_quality.shape}")

#	Типы	данных
print("Типы данных:")
print(red_wine_quality.dtypes)

# Общая информация
print("общая информация")
print(red_wine_quality.info())
print(red_wine_quality.describe())

# Обработка пропусков
print("Обработка пропусков:")
print(red_wine_quality.isnull().sum())
print(red_wine_quality.isnull().sum() / len(red_wine_quality) * 100)
red_wine_quality_cleaned = red_wine_quality.dropna()

# Обработка дубликатов
print("Дубликаты:")
print(red_wine_quality_cleaned.duplicated().sum())
red_wine_quality_unique = red_wine_quality.drop_duplicates()

# Визуализация выбросов до обработки
list_of_numerical_column = ['fixed acidity', 'volatile acidity', 'citric acid', 'residual sugar','chlorides',
                            'free sulfur dioxide','total sulfur dioxide', 'density', 'pH', 'sulphates', 'alcohol', 'quality']
print("\n--- 1. Визуализация выбросов (до обработки) ---")

# Фигура
plt.figure(figsize=(20, 15))
plt.suptitle("Диаграммы размаха ('ящики с усами') для признаков до удаления выбросов", fontsize=22)

# box plot
for i, column in enumerate(list_of_numerical_column, 1):
    plt.subplot(4, 3, i)
    sns.boxplot(x=red_wine_quality_unique[column])
    plt.title(f"{column}", fontsize=16)
    plt.xlabel("")

plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.show()

# Обработка выбросов
#	Метод	межквартильного	размаха	(IQR)
red_wine_quality_filtered = red_wine_quality_unique[:]
for column in list_of_numerical_column:
    Q1 = red_wine_quality_unique[column].quantile(0.25)
    Q3 = red_wine_quality_unique[column].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    #	Фильтрация	выбросов
    red_wine_quality_filtered = red_wine_quality_filtered[(red_wine_quality_filtered[column] >= lower_bound) & (red_wine_quality_filtered[column] <= upper_bound)]

print(f"До выбросов: {len(red_wine_quality_unique)}")
print(f"После выбросов: {len(red_wine_quality_filtered)}")

# Анализ
print('Анализ')
# Выводим сравнение для нескольких ключевых столбцов, где было много выбросов
columns_to_compare = ['residual sugar', 'total sulfur dioxide', 'sulphates']
for col in columns_to_compare:
    print(f"\nСравнение статистик для '{col}':")
    # Создаем сравнительную таблицу
    comparison_df = pd.DataFrame({
        "До удаления": red_wine_quality_unique[col].describe(),
        "После удаления": red_wine_quality_filtered[col].describe()
    })
    print(comparison_df)
    print("-" * 40)


# Пометка выброса
red_wine_quality_with_releases = red_wine_quality_unique[:]
for column in list_of_numerical_column:
    Q1 = red_wine_quality_unique[column].quantile(0.25)
    Q3 = red_wine_quality_unique[column].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    #	Фильтрация	выбросов
    red_wine_quality_with_releases['Release'] = np.where((red_wine_quality_with_releases[column] >= lower_bound) & (red_wine_quality_with_releases[column] <= upper_bound), 0, 1)

# Разделение на выборки
feature_columns_of_wine_quality =  red_wine_quality_with_releases.drop(columns=['quality'])
target_column_of_wine_quality = red_wine_quality_with_releases['quality']
features_train, features_test, target_train, target_test = train_test_split(
    feature_columns_of_wine_quality,
    target_column_of_wine_quality,
    test_size=0.2,
    random_state=42
)
# Нормализация
robust_scaler = preprocessing.RobustScaler()
robust_scaler.fit(features_train)
features_train_scaled = robust_scaler.transform(features_train)
features_test_scaled = robust_scaler.transform(features_test)

# Линейная регрессия
linear_regression = LinearRegression()
liner_model = linear_regression.fit(features_test_scaled, target_train)

# Полиномиальная регрессия степени
# Вариант со всеми взаимодействиями
poly = PolynomialFeatures(degree=2, include_bias=False, interaction_only=True)
features_train_poly = poly.fit_transform(features_train_scaled)
poly_model = linear_regression.fit(features_train_poly, target_train)

# Осмысленное взаимодействие
features_train_poly_better = features_train_scaled[:]
# 1. Буферная система
features_train_poly_better["acid_pH_ratio"] = features_train_poly_better["fixed acidity"] / (features_train_poly_better["pH"]
                                                                                                 + EPS)
features_train_poly_better["total_acidity_effect"] = (features_train_poly_better["fixed acidity"]
                                                          + features_train_poly_better["volatile acidity"]
                                                          - features_train_poly_better["citric acid"])

# 2. Баланс сахара и спирта
features_train_poly_better["alcohol_sugar_density"] = (features_train_poly_better["alcohol"]
                                                           * features_train_poly_better["residual sugar"]
                                                           / (features_train_poly_better["density"] + EPS))
features_train_poly_better["sweetness_balance"] = (features_train_poly_better["residual sugar"]
                                                       / (features_train_poly_better["alcohol"] + EPS))

# 3. Сера и кислотность
features_train_poly_better["sulfur_balance"] = (features_train_poly_better["free sulfur dioxide"]
                                                    / (features_train_poly_better["total sulfur dioxide"] + EPS))
features_train_poly_better["sulfur_acidity_interaction"] = (features_train_poly_better["total sulfur dioxide"]
                                                                * features_train_poly_better["volatile acidity"])

# 4. Минерализация
features_train_poly_better["salty_mineral_effect"] = features_train_poly_better["chlorides"] * features_train_poly_better["sulphates"]
features_train_poly_better["chlorides_to_density"] = features_train_poly_better["chlorides"] / (features_train_poly_better["density"] + EPS)

# 5. Комплексный индекс структуры
features_train_poly_better["structure_index"] = (
        features_train_poly_better["alcohol"] * features_train_poly_better["fixed acidity"] * features_train_poly_better["sulphates"]
        / (features_train_poly_better["volatile acidity"] + features_train_poly_better["chlorides"] + EPS)
    )

# 6. Индекс свежести
features_train_poly_better["freshness_index"] = ((features_train_poly_better["pH"]
                                                     * features_train_poly_better["citric acid"])
                                                     / (features_train_poly_better["volatile acidity"] + EPS))

poly_model_better = linear_regression.fit(features_train_poly_better, target_train)
# Регрессия с регуляризацией Ridge