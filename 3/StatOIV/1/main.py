import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

# Загрузка данных
bmw_sales = pd.read_csv("Bmw sales.csv")

# Проверка	размерности
print(f"Размер	датасета:	{bmw_sales.shape}")

#	Типы	данных
print("Типы данных:")
print(bmw_sales.dtypes)

# Первые и последние строки
print("Первые строки:")
print(bmw_sales.head())
print("Последние строки:")
print(bmw_sales.tail())

# Общая информация
print("общая информация")
print(bmw_sales.info())
print(bmw_sales.describe())

# Обработка пропусков
print("Обработка пропусков:")
print(bmw_sales.isnull().sum())
print(bmw_sales.isnull().sum() / len(bmw_sales) * 100)
# bmw_sales_cleaned = bmw_sales.dropna()

# Обработка дубликатов
print("Дубликаты:")
print(bmw_sales.duplicated().sum())
# bmw_sales_unique = bmw_sales.drop_duplicates()

# Обработка выбросов
#	Метод	межквартильного	размаха	(IQR)
list_of_numerical_column = ['Year', 'Engine_Size_L', 'Mileage_KM', 'Price_USD','Sales_Volume']
bmw_sales_filtered = bmw_sales[:]
for column in list_of_numerical_column:
    Q1 = bmw_sales[column].quantile(0.25)
    Q3 = bmw_sales[column].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    #	Фильтрация	выбросов
    bmw_sales_filtered = bmw_sales_filtered[(bmw_sales_filtered[column] >= lower_bound) & (bmw_sales_filtered[column] <= upper_bound)]

# Анализ
# Какая модель BMW продавалась чаще всего?
most_sold_model = bmw_sales_filtered['Model'].mode()[0]
print(f"Самая продаваемая модель: {most_sold_model}")
# В каком регионе было больше всего продаж?
top_region = bmw_sales_filtered['Region'].mode()[0]
print(f"Регион с наибольшим количеством продаж: {top_region}")
# Какой цвет автомобиля самый популярный?
most_popular_color = bmw_sales_filtered['Color'].mode()[0]
print(f"Самый популярный цвет: {most_popular_color}")
# Автомобили с каким типом коробки передач продаются чаще: автоматической или механической?
transmission_counts = bmw_sales_filtered['Transmission'].value_counts()
print("Частота продаж по типу коробки передач:")
print(transmission_counts)
# Какая средняя цена у автомобилей с дизельным двигателем по сравнению с бензиновым?
diesel_avg_price = bmw_sales_filtered[bmw_sales_filtered['Fuel_Type'] == 'Diesel']['Price_USD'].mean().round(2)
petrol_avg_price = bmw_sales_filtered[bmw_sales_filtered['Fuel_Type'] == 'Petrol']['Price_USD'].mean().round(2)
#avg_price_by_fuel = bmw_sales_filtered.groupby('Fuel_Type')['Price_USD'].mean().round(2)
print("Средняя цена по типу топлива:")
print(f"Diesel: {diesel_avg_price}")
print(f"Petrol: {petrol_avg_price}")
# Какая средняя цена у автомобилей, отнесенных к категории "High" по объему продаж?
bins = [0, 150, 300, np.inf]
labels = ['Low', 'Medium', 'High']
bmw_sales_filtered['Sales_Category'] = pd.cut(bmw_sales_filtered['Sales_Volume'], bins=bins, labels=labels)
avg_price_high_sales = bmw_sales_filtered[bmw_sales_filtered['Sales_Category'] == 'High']['Price_USD'].mean().round(2)
#amount_of_high_sales = bmw_sales_filtered[bmw_sales_filtered['Sales_Category'] == 'High'].value_counts()
#print(f"Количество продаж категории high: {amount_of_high_sales}")
print(f"Средняя цена автомобилей в категории 'High' по объему продаж: ${avg_price_high_sales}")
# Продажи каких моделей чаще классифицируются как "High"?
high_sales_models = bmw_sales_filtered[bmw_sales_filtered['Sales_Category'] == 'High']['Model'].value_counts().head(5)
print("Модели, продажи которых чаще всего классифицируются как 'High':")
print(high_sales_models)
# У каких автомобилей в среднем больше пробег: у бензиновых или гибридных?
diesel_avg_mileage = bmw_sales_filtered[bmw_sales_filtered['Fuel_Type'] == 'Diesel']['Mileage_KM'].mean().round(2)
gibrid_avg_mileage = bmw_sales_filtered[bmw_sales_filtered['Fuel_Type'] == 'Petrol']['Mileage_KM'].mean().round(2)
#avg_mileage_by_fuel = bmw_sales_filtered.groupby('Fuel_Type')['Mileage_KM'].mean().round(2)
print("Средний пробег по типу топлива:")
print(f"Diesel: {diesel_avg_mileage}")
print(f"Gibrid: {gibrid_avg_mileage}")
# В каком году были произведены самые дорогие проданные автомобили?
most_expensive_car_year = bmw_sales_filtered.loc[bmw_sales_filtered['Price_USD'].idxmax()]['Year']
print(f"Год выпуска самого дорогого автомобиля: {most_expensive_car_year}")
# Какая зависимость между пробегом и ценой автомобиля?
correlation_price_mileage = bmw_sales_filtered['Mileage_KM'].corr(bmw_sales_filtered['Price_USD'])
print(f"Корреляция между пробегом и ценой: {correlation_price_mileage:.4f}")



# 1. Гистограмма для Price_USD
plt.figure()
plt.hist(bmw_sales_filtered['Price_USD'], bins=30, alpha=0.7, edgecolor='black')
plt.title('Гистограмма: Распределение цен автомобилей')
plt.xlabel('Цена (USD)')
plt.ylabel('Частота')
plt.grid(True, alpha=0.3)
plt.show()


# 2. Гистограмма для Mileage_KM
plt.figure()
plt.hist(bmw_sales_filtered['Mileage_KM'], bins=30, alpha=0.7, edgecolor='black')
plt.title('Гистограмма: Распределение пробега')
plt.xlabel('Пробег (км)')
plt.ylabel('Частота')
plt.grid(True, alpha=0.3)
plt.show()


# 3. Box plot для Price_USD
plt.figure()
plt.boxplot(bmw_sales_filtered['Price_USD'])
plt.title('Box plot: Распределение цен')
plt.ylabel('Цена (USD)')
plt.show()


# 4. Box plot для Mileage_KM
plt.figure()
plt.boxplot(bmw_sales_filtered['Mileage_KM'])
plt.title('Box plot: Распределение пробега')
plt.ylabel('Пробег (км)')
plt.show()


# 5. Bar plot для категориальной переменной (топ-10 моделей)
top_models = bmw_sales_filtered['Model'].value_counts().head(10)
plt.figure()
top_models.plot(kind='bar')
plt.title('Bar plot: Топ-10 самых продаваемых моделей BMW')
plt.xlabel('Модель')
plt.ylabel('Количество продаж')
plt.xticks(rotation=45)
plt.show()


# 6. Bar plot для регионов
region_counts = bmw_sales_filtered['Region'].value_counts()
plt.figure()
region_counts.plot(kind='bar')
plt.title('Bar plot: Распределение продаж по регионам')
plt.xlabel('Регион')
plt.ylabel('Количество продаж')
plt.xticks(rotation=45)
plt.show()


# 7. Correlation matrix
numeric_cols = bmw_sales_filtered.select_dtypes(include=[np.number]).columns
corr_matrix = bmw_sales_filtered[numeric_cols].corr()
plt.figure(figsize=(10, 8))
sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0, square=True, fmt='.2f')
plt.title('Correlation Matrix: Корреляция числовых признаков')
plt.show()


# 8. Scatter plot: Price_USD vs Mileage_KM
plt.figure()
plt.scatter(bmw_sales_filtered['Mileage_KM'], bmw_sales_filtered['Price_USD'], alpha=0.1)
plt.xlabel('Пробег (км)')
plt.ylabel('Цена (USD)')
plt.title('Scatter plot: Зависимость цены от пробега')
plt.grid(True, alpha=0.3)
plt.show()


# 9. Scatter plot: Price_USD vs Year
plt.figure()
plt.scatter(bmw_sales_filtered['Year'], bmw_sales_filtered['Price_USD'], alpha=0.6)
plt.xlabel('Год выпуска')
plt.ylabel('Цена (USD)')
plt.title('Scatter plot: Зависимость цены от года выпуска')
plt.grid(True, alpha=0.3)
plt.show()


# 10. Contingency table: Fuel_Type vs Transmission
contingency_table = pd.crosstab(bmw_sales_filtered['Fuel_Type'], bmw_sales_filtered['Transmission'])
plt.figure(figsize=(8, 6))
sns.heatmap(contingency_table, annot=True, fmt='d', cmap='Blues')
plt.title('Contingency Table: Тип топлива vs Коробка передач')
plt.xlabel('Коробка передач')
plt.ylabel('Тип топлива')
plt.show()


#Violin plot для Price_USD по типам топлива
plt.figure()
sns.violinplot(data=bmw_sales_filtered, x='Fuel_Type', y='Price_USD')
plt.title('Violin plot: Распределение цен по типам топлива')
plt.xlabel('Тип топлива')
plt.ylabel('Цена (USD)')
plt.show()


