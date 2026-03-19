import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from sklearn import preprocessing
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression, Ridge, RidgeCV, Lasso, ElasticNetCV, LassoCV
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

EPS = 1e-9

# --- Проверка и обработка датасета ---

# Инициализация
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
red_wine_quality_unique = red_wine_quality_cleaned.drop_duplicates()

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
red_wine_quality_filtered = red_wine_quality_unique.copy()
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
red_wine_quality_with_releases = red_wine_quality_unique.copy()

red_wine_quality_with_releases['Release'] = 0  # сначала всё нормальное
for column in list_of_numerical_column:
    Q1 = red_wine_quality_unique[column].quantile(0.25)
    Q3 = red_wine_quality_unique[column].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    # если есть выброс — ставим 1
    red_wine_quality_with_releases['Release'] |= (
        (red_wine_quality_with_releases[column] < lower_bound) |
        (red_wine_quality_with_releases[column] > upper_bound)
    ).astype(int)

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

# --- Модели ---

# -- Линейная регрессия --

# Обучение
linear_regression = LinearRegression()
liner_model = linear_regression.fit(features_train_scaled, target_train)

# Проверка
target_predict_linear = liner_model.predict(features_test_scaled)

# Метрики
linear_mae = mean_absolute_error(target_test, target_predict_linear)
mse_linear = mean_squared_error(target_test, target_predict_linear)
rmse_linear = np.sqrt(mse_linear)
r2_linear_test = r2_score(target_test, target_predict_linear)
r2_linear_train = r2_score(target_train, liner_model.predict(features_train_scaled))

# -- Полиномиальная регрессия степени --

# - Вариант со всеми взаимодействиями -

# Обучение
poly = PolynomialFeatures(degree=2, include_bias=False, interaction_only=True)

features_train_poly = poly.fit_transform(features_train_scaled)
poly_model = linear_regression.fit(features_train_poly, target_train)

# Проверка
features_test_poly = poly.transform(features_test_scaled)
target_predict_poly = poly_model.predict(features_test_poly)

poly_mae = mean_absolute_error(target_test, target_predict_poly)
mse_poly = mean_squared_error(target_test, target_predict_poly)
rmse_poly = np.sqrt(mse_poly)
r2_poly_test = r2_score(target_test, target_predict_poly)
r2_poly_train = r2_score(target_train, poly_model.predict(features_train_poly))
# - Ручные столбцы -

# Создание столбцов
features_train_poly_better = features_train.copy()
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

features_test_poly_better = features_test.copy()
# 1. Буферная система
features_test_poly_better["acid_pH_ratio"] = features_test_poly_better["fixed acidity"] / (features_test_poly_better["pH"]
                                                                                                 + EPS)
features_test_poly_better["total_acidity_effect"] = (features_test_poly_better["fixed acidity"]
                                                          + features_test_poly_better["volatile acidity"]
                                                          - features_test_poly_better["citric acid"])

# 2. Баланс сахара и спирта
features_test_poly_better["alcohol_sugar_density"] = (features_test_poly_better["alcohol"]
                                                           * features_test_poly_better["residual sugar"]
                                                           / (features_test_poly_better["density"] + EPS))
features_test_poly_better["sweetness_balance"] = (features_test_poly_better["residual sugar"]
                                                       / (features_test_poly_better["alcohol"] + EPS))

# 3. Сера и кислотность
features_test_poly_better["sulfur_balance"] = (features_test_poly_better["free sulfur dioxide"]
                                                    / (features_test_poly_better["total sulfur dioxide"] + EPS))
features_test_poly_better["sulfur_acidity_interaction"] = (features_test_poly_better["total sulfur dioxide"]
                                                                * features_test_poly_better["volatile acidity"])

# 4. Минерализация
features_test_poly_better["salty_mineral_effect"] = features_test_poly_better["chlorides"] * features_test_poly_better["sulphates"]
features_test_poly_better["chlorides_to_density"] = features_test_poly_better["chlorides"] / (features_test_poly_better["density"] + EPS)

# 5. Комплексный индекс структуры
features_test_poly_better["structure_index"] = (
        features_test_poly_better["alcohol"] * features_test_poly_better["fixed acidity"] * features_test_poly_better["sulphates"]
        / (features_test_poly_better["volatile acidity"] + features_test_poly_better["chlorides"] + EPS)
    )

# 6. Индекс свежести
features_test_poly_better["freshness_index"] = ((features_test_poly_better["pH"]
                                                     * features_test_poly_better["citric acid"])
                                                     / (features_test_poly_better["volatile acidity"] + EPS))

# Нормализация датасетов с новыми столбцами
robust_scaler_poly = preprocessing.RobustScaler()
robust_scaler_poly.fit(features_train_poly_better)
features_train_poly_better_scaled = robust_scaler_poly.transform(features_train_poly_better)
features_test_poly_better_scaled = robust_scaler_poly.transform(features_test_poly_better)

# Обучение
poly_model_better = linear_regression.fit(features_train_poly_better_scaled, target_train)

# Проверка
target_predict_poly_better = poly_model_better.predict(features_test_poly_better_scaled)

# Метрики
poly_better_mae = mean_absolute_error(target_test, target_predict_poly_better)
mse_poly_better = mean_squared_error(target_test, target_predict_poly_better)
rmse_poly_better = np.sqrt(mse_poly_better)
r2_poly_better_test = r2_score(target_test, target_predict_poly_better)
r2_poly_better_train = r2_score(target_train, poly_model_better.predict(features_train_poly_better_scaled))

# -- Регрессия с регуляризацией Ridge --

# Обучение
ridge_regression = Ridge(alpha=0.5)
ridge_regression_cv = RidgeCV(alphas=[0.1, 1.0, 10.0])


ridge_model = ridge_regression.fit(features_train_scaled, target_train)
ridge_model_cv = ridge_regression_cv.fit(features_train_scaled, target_train)

# Проверка
target_predict_ridge = ridge_model.predict(features_test_scaled)
target_predict_ridge_cv = ridge_model_cv.predict(features_test_scaled)

# Метрики
ridge_mae = mean_absolute_error(target_test, target_predict_ridge)
mse_ridge = mean_squared_error(target_test, target_predict_ridge)
rmse_ridge = np.sqrt(mse_ridge)
r2_ridge_test = r2_score(target_test, target_predict_ridge)
r2_ridge_train = r2_score(target_train, ridge_model.predict(features_train_scaled))

ridge_cv_mae = mean_absolute_error(target_test, target_predict_ridge_cv)
mse_ridge_cv = mean_squared_error(target_test, target_predict_ridge_cv)
rmse_ridge_cv = np.sqrt(mse_ridge_cv)
r2_ridge_cv_test = r2_score(target_test, target_predict_ridge_cv)
r2_ridge_cv_train = r2_score(target_train, ridge_model_cv.predict(features_train_scaled))

# -- Регрессия с регуляризацией Lasso --

# Обучение
lasso_regression = Lasso(alpha=0.5)
lasso_model = lasso_regression.fit(features_train_poly, target_train)

# Проверка
target_predict_lasso = lasso_model.predict(features_test_poly)

# Метрики
lasso_mae = mean_absolute_error(target_test, target_predict_lasso)
mse_lasso = mean_squared_error(target_test, target_predict_lasso)
rmse_lasso = np.sqrt(mse_lasso)
r2_lasso_test = r2_score(target_test, target_predict_lasso)
r2_lasso_train = r2_score(target_train, lasso_model.predict(features_train_poly))

# -- Регрессия с регуляризацией LassoCV --

# Обучение
lasso_regression_cv = LassoCV(
    alphas=[0.0001, 0.001, 0.01, 0.1, 1.0, 10.0],
    cv=5,
    n_jobs=-1,
    random_state=42
)
lasso_model_cv = lasso_regression_cv.fit(features_train_poly, target_train)

# Проверка
target_predict_lasso_cv = lasso_model_cv.predict(features_test_poly)

# Метрики
lasso_cv_mae = mean_absolute_error(target_test, target_predict_lasso_cv)
mse_lasso_cv = mean_squared_error(target_test, target_predict_lasso_cv)
rmse_lasso_cv = np.sqrt(mse_lasso_cv)
r2_lasso_cv_test = r2_score(target_test, target_predict_lasso_cv)
r2_lasso_cv_train = r2_score(target_train, lasso_model_cv.predict(features_train_poly))

# -- Эластичная сеть --

# Обучение
elastic_net_model = make_pipeline(
    preprocessing.RobustScaler(),
    ElasticNetCV(
        l1_ratio=[0.1, 0.5, 0.9],
        alphas=[0.001, 0.01, 0.1, 1.0],
        cv=5,
        random_state=42
    )
)

elastic_net_model.fit(features_train_poly, target_train)

# Проверка
target_predict_elastic_net = elastic_net_model.predict(features_test_poly)

# Метрики
elastic_net_mae = mean_absolute_error(target_test, target_predict_elastic_net)
mse_elastic_net = mean_squared_error(target_test, target_predict_elastic_net)
rmse_elastic_net = np.sqrt(mse_elastic_net)
r2_elastic_net_test = r2_score(target_test, target_predict_elastic_net)
r2_elastic_net_train = r2_score(target_train, elastic_net_model.predict(features_train_poly))

# --- Сводные таблицы результатов моделей ---

# Общая сравнительная таблица
results = pd.DataFrame({
    'Model': [
        'Linear Regression',
        'Polynomial Regression (interaction only)',
        'Polynomial Regression (better features)',
        'Ridge Regression',
        'RidgeCV',
        'Lasso Regression',
        'LassoCV',
        'ElasticNetCV'
    ],
    'MAE (Test)': [
        linear_mae,
        poly_mae,
        poly_better_mae,
        ridge_mae,
        ridge_cv_mae,
        lasso_mae,
        lasso_cv_mae,
        elastic_net_mae
    ],
    'MSE (Test)': [
        mse_linear,
        mse_poly,
        mse_poly_better,
        mse_ridge,
        mse_ridge_cv,
        mse_lasso,
        mse_lasso_cv,
        mse_elastic_net
    ],
    'RMSE (Test)': [
        rmse_linear,
        rmse_poly,
        rmse_poly_better,
        rmse_ridge,
        rmse_ridge_cv,
        rmse_lasso,
        rmse_lasso_cv,
        rmse_elastic_net
    ],
    'R² (Test)': [
        r2_linear_test,
        r2_poly_test,
        r2_poly_better_test,
        r2_ridge_test,
        r2_ridge_cv_test,
        r2_lasso_test,
        r2_lasso_cv_test,
        r2_elastic_net_test
    ],
    'R² (Train)': [
        r2_linear_train,
        r2_poly_train,
        r2_poly_better_train,
        r2_ridge_train,
        r2_ridge_cv_train,
        r2_lasso_train,
        r2_lasso_cv_train,
        r2_elastic_net_train
    ]
})

results['Overfitting (R² Train - Test)'] = results['R² (Train)'] - results['R² (Test)']
pd.set_option('display.width', 1000)
pd.set_option('display.max_columns', None)  # Показать все столбцы
pd.set_option('display.max_colwidth', None)  # Показать полное содержимое ячеек
print("\n===== Общая сравнительная таблица моделей =====")
print(results)

# Отдельная таблица для сравнения Полиномиальных моделей
poly_comparison = pd.DataFrame({
    'Метрика': ['MAE', 'MSE', 'RMSE', 'R² (Test)', 'R² (Train)'],
    'Polynomial (interaction only)': [poly_mae, mse_poly, rmse_poly, r2_poly_test, r2_poly_train],
    'Polynomial (better features)': [poly_better_mae, mse_poly_better, rmse_poly_better, r2_poly_better_test, r2_poly_better_train]
})

print("\n===== Сравнение полиномиальных моделей =====")
print(poly_comparison)

# Отдельная таблица для сравнения Ridge и RidgeCV
ridge_comparison = pd.DataFrame({
    'Метрика': ['MAE', 'MSE', 'RMSE', 'R² (Test)', 'R² (Train)'],
    'Ridge (alpha=0.5)': [ridge_mae, mse_ridge, rmse_ridge, r2_ridge_test, r2_ridge_train],
    'RidgeCV': [ridge_cv_mae, mse_ridge_cv, rmse_ridge_cv, r2_ridge_cv_test, r2_ridge_cv_train]
})

print("\n===== Сравнение Ridge моделей =====")
print(ridge_comparison)

# Отдельная таблица для сравнения Lasso и LassoCV
lasso_comparison = pd.DataFrame({
    'Метрика': ['MAE', 'MSE', 'RMSE', 'R² (Test)', 'R² (Train)'],
    'Lasso (alpha=0.5)': [lasso_mae, mse_lasso, rmse_lasso, r2_lasso_test, r2_lasso_train],
    'LassoCV': [lasso_cv_mae, mse_lasso_cv, rmse_lasso_cv, r2_lasso_cv_test, r2_lasso_cv_train]
})

print("\n===== Сравнение Lasso моделей =====")
print(lasso_comparison)


# === Анализ важности признаков для лучшей модели (ElasticNetCV) ===
best_model = elastic_net_model.named_steps['elasticnetcv']

# Получаем имена признаков после полиномиального преобразования
poly_feature_names = poly.get_feature_names_out(features_train.columns)

# Берем коэффициенты
coef = best_model.coef_

# Формируем таблицу важности
importance_df = pd.DataFrame({
    'Признак': poly_feature_names,
    'Коэффициент': coef,
    'Абсолютная важность': np.abs(coef)
}).sort_values(by='Абсолютная важность', ascending=False)

print("\n===== Важность признаков для ElasticNetCV =====")
print(importance_df.head(15))

# Визуализация важности признаков
plt.figure(figsize=(10, 6))
sns.barplot(
    data=importance_df.head(15),
    x='Абсолютная важность',
    y='Признак',
    palette='viridis'
)
plt.title("Топ-15 наиболее значимых признаков ElasticNetCV")
plt.xlabel("Абсолютная важность (|коэффициент|)")
plt.ylabel("Признак")
plt.tight_layout()
plt.show()

# === Сравнение предсказаний с эталонными ===
plt.figure(figsize=(6, 6))
plt.scatter(target_test, target_predict_elastic_net, alpha=0.6, edgecolor='k')
plt.plot([target_test.min(), target_test.max()],
         [target_test.min(), target_test.max()],
         'r--', lw=2)
plt.title("Сравнение предсказанных и реальных значений качества вина")
plt.xlabel("Реальное качество (y_test)")
plt.ylabel("Предсказанное качество (y_pred)")
plt.grid(True)
plt.show()
