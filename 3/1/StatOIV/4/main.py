import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.cluster.hierarchy import dendrogram, linkage
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans, AgglomerativeClustering, DBSCAN
from sklearn.decomposition import PCA
from sklearn.datasets import load_wine
from sklearn.metrics import (
    silhouette_score,
    davies_bouldin_score,
    calinski_harabasz_score,
    adjusted_rand_score,
    normalized_mutual_info_score
)

# Настройка стиля графиков
sns.set(style="whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)

df = pd.read_csv("winequality-red.csv")
df = df.drop_duplicates().dropna()
y_true = df['quality']
X_raw = df.drop(columns=['quality'])

print(f"Размер исходных данных: {X_raw.shape}")

# Обработка выбросов (IQR метод)
numerical_cols = X_raw.columns
Q1 = X_raw[numerical_cols].quantile(0.25)
Q3 = X_raw[numerical_cols].quantile(0.75)
IQR = Q3 - Q1
mask = ~((X_raw[numerical_cols] < (Q1 - 1.5 * IQR)) | (X_raw[numerical_cols] > (Q3 + 1.5 * IQR))).any(axis=1)

X = X_raw[mask].copy()
y_true = y_true[mask].copy()
print(f"Размер данных после удаления выбросов: {X.shape}")

# Масштабирование (Критически важно для кластеризации)
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)



# 2. Определение оптимальных параметров
def plot_kmeans_optimization(data):
    """Строит графики Метода локтя и Силуэтного скора."""
    inertia = []
    silhouette_scores = []
    K_range = range(2, 11)

    for k in K_range:
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        kmeans.fit(data)
        inertia.append(kmeans.inertia_)
        silhouette_scores.append(silhouette_score(data, kmeans.labels_))

    fig, ax1 = plt.subplots(1, 2, figsize=(16, 5))

    # Метод локтя
    ax1[0].plot(K_range, inertia, 'bx-')
    ax1[0].set_xlabel('k (количество кластеров)')
    ax1[0].set_ylabel('Inertia')
    ax1[0].set_title('Метод локтя (Elbow Method)')

    # Силуэтный анализ
    ax1[1].plot(K_range, silhouette_scores, 'rx-')
    ax1[1].set_xlabel('k (количество кластеров)')
    ax1[1].set_ylabel('Silhouette Score')
    ax1[1].set_title('Силуэтный анализ')

    plt.tight_layout()
    plt.show()


def plot_dendrogram_viz(data):
    """Строит дендрограмму для Agglomerative Clustering."""
    plt.figure(figsize=(12, 5))
    plt.title("Дендрограмма (Hierarchical Clustering Dendrogram)")
    # Используем метод ward для минимизации дисперсии
    dend = dendrogram(linkage(data, method='ward'))
    plt.xlabel("Индексы образцов")
    plt.ylabel("Расстояние")
    plt.show()


def plot_k_distance(data, k=5):
    """Строит график k-расстояний для подбора eps в DBSCAN."""
    neigh = NearestNeighbors(n_neighbors=k)
    nbrs = neigh.fit(data)
    distances, indices = nbrs.kneighbors(data)

    # Сортируем расстояния до k-го соседа
    distances = np.sort(distances[:, k - 1], axis=0)

    plt.figure(figsize=(10, 5))
    plt.plot(distances)
    plt.title(f"График k-расстояний (k={k}) для настройки DBSCAN")
    plt.xlabel("Точки, отсортированные по расстоянию")
    plt.ylabel(f"Расстояние до {k}-го соседа (eps)")
    plt.grid(True)
    plt.show()


plot_kmeans_optimization(X_scaled)

plot_dendrogram_viz(X_scaled)

plot_k_distance(X_scaled, k=14)

# 3. Обучение моделей с выбранными параметрами
# A. KMeans
kmeans_k = 3
kmeans = KMeans(n_clusters=kmeans_k, random_state=42, n_init=10)
kmeans_labels = kmeans.fit_predict(X_scaled)

# B. Agglomerative
agg_k = 3
agg = AgglomerativeClustering(n_clusters=agg_k, linkage='ward')
agg_labels = agg.fit_predict(X_scaled)

# C. DBSCAN
# eps выбирается по "изгибу" на графике k-distance.
# Для StandardScaler данных eps обычно в диапазоне 2.0 - 4.0 для многомерных данных.
# min_samples ставим равным размерности данных или чуть больше.
db_eps = 2.5
db_min_samples = 14  # Примерно равно количеству признаков
dbscan = DBSCAN(eps=db_eps, min_samples=db_min_samples)
dbscan_labels = dbscan.fit_predict(X_scaled)

# 4. Оценка качества
def calculate_metrics(name, labels, X, y_true):
    # Исключаем шум (-1) для внутренних метрик DBSCAN
    if -1 in labels:
        core_mask = labels != -1
        if np.sum(core_mask) < 2 or len(set(labels[core_mask])) < 2:
            return {
                "Алгоритм": name, "Кластеров": len(set(labels)),
                "Silhouette": 0, "Davies-Bouldin": 0, "Calinski-H": 0,
                "ARI": 0, "NMI": 0
            }
        X_eval = X[core_mask]
        labels_eval = labels[core_mask]
        y_eval = y_true[core_mask]
    else:
        X_eval = X
        labels_eval = labels
        y_eval = y_true

    n_clusters = len(set(labels_eval))

    return {
        "Алгоритм": name,
        "Кластеров": n_clusters,
        "Silhouette": round(silhouette_score(X_eval, labels_eval), 3),
        "Davies-Bouldin": round(davies_bouldin_score(X_eval, labels_eval), 3),
        "Calinski-H": round(calinski_harabasz_score(X_eval, labels_eval), 3),
        "ARI": round(adjusted_rand_score(y_eval, labels_eval), 3),
        "NMI": round(normalized_mutual_info_score(y_eval, labels_eval), 3)
    }


results = []
results.append(calculate_metrics("KMeans", kmeans_labels, X_scaled, y_true))
results.append(calculate_metrics("Agglomerative", agg_labels, X_scaled, y_true))
results.append(calculate_metrics("DBSCAN", dbscan_labels, X_scaled, y_true))

results_df = pd.DataFrame(results)
print("\n=== Итоговая таблица метрик ===")
print(results_df)

# Информация о шуме DBSCAN
n_noise = list(dbscan_labels).count(-1)
print(f"\nDBSCAN: Выбросов (шум) найдено: {n_noise} ({(n_noise / len(dbscan_labels)) * 100:.2f}%)")

# 5. Визуализация результатов
# PCA для 2D проекции
pca = PCA(n_components=2)
X_pca = pca.fit_transform(X_scaled)

# Создаем DataFrame для удобства построения графиков
viz_df = pd.DataFrame(X_pca, columns=['PC1', 'PC2'])
viz_df['KMeans'] = kmeans_labels
viz_df['Agglomerative'] = agg_labels
viz_df['DBSCAN'] = dbscan_labels

fig, axes = plt.subplots(1, 3, figsize=(18, 5))

# График KMeans
sns.scatterplot(data=viz_df, x='PC1', y='PC2', hue='KMeans', palette='viridis', ax=axes[0], s=50)
axes[0].set_title(f'KMeans (k={kmeans_k})')

# График Agglomerative
sns.scatterplot(data=viz_df, x='PC1', y='PC2', hue='Agglomerative', palette='viridis', ax=axes[1], s=50)
axes[1].set_title(f'Agglomerative (k={agg_k})')

# График DBSCAN
# Отдельно красим шум
unique_db = np.unique(dbscan_labels)
palette_db = sns.color_palette("deep", len(unique_db))
# Если есть шум (-1), делаем его черным или серым, но для простоты оставим стандартную палитру
sns.scatterplot(data=viz_df, x='PC1', y='PC2', hue='DBSCAN', palette='deep', ax=axes[2], s=50)
axes[2].set_title(f'DBSCAN (eps={db_eps}, min={db_min_samples})')

plt.tight_layout()
plt.show()

# 6. Дополнительно: Boxplots и Гистограммы
# Добавляем метки лучшей модели (например, KMeans) к исходным данным
X_final = X.copy()
X_final['Cluster'] = kmeans_labels

# Гистограмма размеров кластеров
plt.figure(figsize=(6, 4))
sns.countplot(x='Cluster', data=X_final, palette='viridis')
plt.title("Распределение размеров кластеров (KMeans)")
plt.show()

# Boxplot для анализа признаков (берем первые 3 признака для примера)
features_to_plot = X.columns[:3]
plt.figure(figsize=(15, 5))
for i, col in enumerate(features_to_plot):
    plt.subplot(1, 3, i + 1)
    sns.boxplot(x='Cluster', y=col, data=X_final, palette='viridis')
    plt.title(f'Распределение {col}')

plt.tight_layout()
plt.show()