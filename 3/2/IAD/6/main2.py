from torchvision import datasets
import torchvision.transforms as T
import torch
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
from transformers import CLIPModel, CLIPProcessor
from sklearn.manifold import TSNE

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Используется: {device}")

model_id = "openai/clip-vit-base-patch32"
model = CLIPModel.from_pretrained(model_id).to(device)
processor = CLIPProcessor.from_pretrained(model_id)


# A--------------------------------------------------------------------
# Индексирование коллекции изображений

test_dataset = datasets.Flowers102(
    root="./data",
    split="test",
    download=True,
    transform=None
)

test_loader = torch.utils.data.DataLoader(
    dataset=test_dataset, batch_size=64, shuffle=False
)

class_names = test_dataset.classes
print(f"Классов: {len(class_names)}")
print(f"Примеры: {class_names[:5]}")

all_image_features = []
all_images_raw = []
all_labels_list = []

model.eval()
with torch.no_grad():
    for images, labels in test_loader:
        image_inputs = processor(
            images=list(images),
            return_tensors="pt",
            padding=True
        ).to(device)

        features = model.get_image_features(**image_inputs)
        features = features / features.norm(dim=-1, keepdim=True)

        all_image_features.append(features.cpu())
        all_images_raw.append(torch.stack([
            T.ToTensor()(img) for img in images
        ]))
        all_labels_list.append(labels)

all_image_features = torch.cat(all_image_features)
all_images_raw = torch.cat(all_images_raw)
all_labels_list = torch.cat(all_labels_list)

print(f"Проиндексировано изображений: {len(all_image_features)}")
print(f"Размерность эмбеддинга: {all_image_features.shape[1]}")

torch.save({
    "features": all_image_features,
    "labels": all_labels_list,
}, "image_index.pt")
print("Индекс сохранён в image_index.pt")


# B--------------------------------------------------------------------
# Функция поиска и визуализации результатов

def search_by_text(query, image_features, top_k=8):
    """Ищет top_k наиболее похожих изображений по текстовому запросу."""
    text_inputs = processor(
        text=[query],
        return_tensors="pt",
        padding=True
    ).to(device)

    with torch.no_grad():
        text_feat = model.get_text_features(**text_inputs)
        text_feat = text_feat / text_feat.norm(dim=-1, keepdim=True)

    similarity = (image_features @ text_feat.cpu().T).squeeze()
    top_indices = similarity.argsort(descending=True)[:top_k]
    top_scores = similarity[top_indices]

    return top_indices, top_scores


def visualize_search_results(query, indices, scores, images, labels, class_names):
    """Визуализирует результаты поиска изображений по тексту."""
    n = len(indices)
    fig, axes = plt.subplots(1, n, figsize=(2.5 * n, 3))
    if n == 1:
        axes = [axes]
    fig.suptitle(f'Запрос: "{query}"', fontsize=14, y=1.02)

    for i, (idx, score) in enumerate(zip(indices, scores)):
        img = images[idx].permute(1, 2, 0).numpy().clip(0, 1)
        axes[i].imshow(img)
        axes[i].set_title(
            f"{class_names[labels[idx]]}\n{score:.3f}",
            fontsize=9
        )
        axes[i].axis("off")

    plt.tight_layout()
    plt.savefig(f"search_{query[:30].replace(' ', '_')}.png", dpi=100, bbox_inches="tight")
    plt.show()


# C--------------------------------------------------------------------
# Тестирование системы поиска — не менее 6 запросов

# Запросы по классу (прямое название объекта)
queries_by_class = [
    "a photo of a sunflower",
    "a photo of a rose",
    "a photo of a daisy",
]

# Запросы по атрибуту (описание свойств без названия класса)
queries_by_attribute = [
    "a yellow flower with large petals",
    "a small white flower in a field",
    "a purple flower with thin petals",
]

print("\n" + "="*60)
print("ЧАСТЬ C: ТЕСТИРОВАНИЕ СИСТЕМЫ ПОИСКА")
print("="*60)

all_queries = queries_by_class + queries_by_attribute

for query in all_queries:
    print(f"\nЗапрос: \"{query}\"")
    indices, scores = search_by_text(query, all_image_features, top_k=8)
    print(f"Топ-3 результата: " +
          ", ".join([f"{class_names[all_labels_list[idx]]} ({scores[i]:.3f})"
                     for i, idx in enumerate(indices[:3])]))
    visualize_search_results(
        query, indices, scores,
        all_images_raw, all_labels_list, class_names
    )


# D--------------------------------------------------------------------
# Анализ качества поиска: Recall@K

def recall_at_k(class_names, image_features, labels, k=10):
    """
    Вычисляет Recall@K: доля классов, для которых хотя бы одно
    изображение правильного класса попало в топ-K результатов
    при запросе "a photo of a {class_name}".
    """
    recalls = {}
    for class_idx, class_name in enumerate(class_names):
        query = f"a photo of a {class_name}"
        top_indices, _ = search_by_text(query, image_features, top_k=k)
        top_labels = labels[top_indices].numpy()
        hit = int(class_idx in top_labels)
        recalls[class_name] = hit

    mean_recall = np.mean(list(recalls.values()))
    return recalls, mean_recall


print("\n" + "="*60)
print("ЧАСТЬ D: АНАЛИЗ КАЧЕСТВА ПОИСКА (Recall@K)")
print("="*60)

for k in [1, 5, 10]:
    recalls, mean_recall = recall_at_k(class_names, all_image_features, all_labels_list, k=k)
    print(f"Mean Recall@{k}: {mean_recall * 100:.1f}%")

# Детально для k=10
recalls_k10, mean_recall_k10 = recall_at_k(
    class_names, all_image_features, all_labels_list, k=10
)

print(f"\nRecall@10 по классам:")
for class_name, recall in recalls_k10.items():
    print(f"  {class_name:30s}: {'✓' if recall else '✗'}")
print(f"\nMean Recall@10: {mean_recall_k10 * 100:.1f}%")

# t-SNE визуализация эмбеддингов
print("\nСтроим t-SNE визуализацию...")

# Текстовые эмбеддинги для каждого класса (шаблон "a photo of a {}")
text_descriptions = [f"a photo of a {name}" for name in class_names]
text_inputs = processor(
    text=text_descriptions,
    return_tensors="pt",
    padding=True
).to(device)

with torch.no_grad():
    text_features = model.get_text_features(**text_inputs)
    text_features = text_features / text_features.norm(dim=-1, keepdim=True)

text_features_np = text_features.cpu().numpy()
image_features_np = all_image_features.numpy()

sample_size = min(2000, len(image_features_np))
sample_idx = np.random.choice(len(image_features_np), sample_size, replace=False)
image_sample = image_features_np[sample_idx]
label_sample = all_labels_list.numpy()[sample_idx]

combined = np.vstack([image_sample, text_features_np])
tsne = TSNE(n_components=2, random_state=42, perplexity=30)
combined_2d = tsne.fit_transform(combined)

image_2d = combined_2d[:sample_size]
text_2d = combined_2d[sample_size:]

plt.figure(figsize=(14, 11))
scatter = plt.scatter(
    image_2d[:, 0], image_2d[:, 1],
    c=label_sample, cmap="tab20",
    s=5, alpha=0.5, label="Изображения"
)

# первые 20 классов
for i, class_name in enumerate(class_names[:20]):
    plt.scatter(text_2d[i, 0], text_2d[i, 1],
                s=200, marker="*", color="black", zorder=5)
    plt.annotate(
        class_name,
        (text_2d[i, 0], text_2d[i, 1]),
        fontsize=8, fontweight="bold",
        xytext=(5, 5), textcoords="offset points"
    )

plt.colorbar(scatter)
plt.title("t-SNE: эмбеддинги изображений и текстовых описаний (CLIP)")
plt.legend()
plt.tight_layout()
plt.savefig("tsne_embeddings.png", dpi=100, bbox_inches="tight")
plt.show()
print("Сохранено: tsne_embeddings.png")