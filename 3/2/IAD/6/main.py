from torchvision import datasets
import torch
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
from transformers import CLIPModel, CLIPProcessor
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay


device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def pil_collate_fn(batch):
    """Collate-функция для датасетов с PIL-изображениями (transform=None)."""
    images = [item[0] for item in batch]
    labels = torch.tensor([item[1] for item in batch])
    return images, labels


def test_model(model):
    image = Image.open("example.jpg").convert("RGB")
    descriptions = [
        "a photo of a cat",
        "a photo of a dog",
        "a photo of a car",
    ]

    inputs = processor(
        text=descriptions,
        images=image,
        return_tensors="pt",
        padding=True
    ).to(device)

    with torch.no_grad():
        outputs = model(**inputs)

    similarity = outputs.logits_per_image.squeeze()
    for desc, sim in zip(descriptions, similarity):
        print(f"{sim:.3f} {desc}")

    #26.903 a photo of a cat
    #21.983 a photo of a dog
    #18.259 a photo of a car


def get_text_features(model, processor, descriptions, device):
    """Вычисляет нормализованные текстовые эмбеддинги."""
    text_inputs = processor(
        text=descriptions,
        return_tensors="pt",
        padding=True
    ).to(device)

    with torch.no_grad():
        outputs = model.text_model(**{
            k: v for k, v in text_inputs.items() if k in ("input_ids", "attention_mask")
        })
        text_features = outputs.pooler_output
        text_features = model.text_projection(text_features)

    text_features = text_features / text_features.norm(dim=-1, keepdim=True)
    return text_features


def get_image_features(model, processor, images, device):
    """Вычисляет нормализованные визуальные эмбеддинги."""
    image_inputs = processor(
        images=list(images),
        return_tensors="pt",
        padding=True
    ).to(device)

    with torch.no_grad():
        outputs = model.vision_model(**{
            k: v for k, v in image_inputs.items() if k == "pixel_values"
        })
        image_features = outputs.pooler_output
        image_features = model.visual_projection(image_features)

    image_features = image_features / image_features.norm(dim=-1, keepdim=True)
    return image_features


def evaluate_with_template(model, processor, test_loader, class_names, template, device):
    """Вычисляет zero-shot accuracy для одного шаблона промпта."""
    descriptions = [template.format(name) for name in class_names]
    text_features = get_text_features(model, processor, descriptions, device)

    all_preds = []
    all_labels = []

    model.eval()
    with torch.no_grad():
        for images, labels in test_loader:
            image_features = get_image_features(model, processor, images, device)

            similarity = image_features @ text_features.T
            preds = similarity.argmax(dim=-1)

            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())

    all_preds = np.array(all_preds)
    all_labels = np.array(all_labels)
    accuracy = np.mean(all_preds == all_labels)
    return accuracy, all_preds, all_labels


def evaluate_ensemble(model, processor, test_loader, class_names, templates, device):
    """Вычисляет zero-shot accuracy с ансамблированием нескольких промптов."""
    all_template_features = []
    for template in templates:
        descriptions = [template.format(name) for name in class_names]
        features = get_text_features(model, processor, descriptions, device)
        all_template_features.append(features)

    stacked = torch.stack(all_template_features)
    ensemble_features = stacked.mean(dim=0)
    ensemble_features = ensemble_features / ensemble_features.norm(dim=-1, keepdim=True)

    all_preds = []
    all_labels = []
    all_similarities = []

    model.eval()
    with torch.no_grad():
        for images, labels in test_loader:
            image_features = get_image_features(model, processor, images, device)

            similarity = image_features @ ensemble_features.T
            preds = similarity.argmax(dim=-1)

            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())
            all_similarities.append(similarity.cpu().numpy())

    all_preds = np.array(all_preds)
    all_labels = np.array(all_labels)
    all_similarities = np.vstack(all_similarities)
    accuracy = np.mean(all_preds == all_labels)
    return accuracy, all_preds, all_labels, all_similarities


def visualize_top_errors(test_dataset, all_preds, all_labels, all_similarities, class_names, n=8):
    """Находит и визуализирует топ ошибок CLIP (с наибольшей уверенностью)."""
    error_mask = all_preds != all_labels
    error_indices = np.where(error_mask)[0]

    if len(error_indices) == 0:
        print("Ошибок не найдено!")
        return

    error_confidences = all_similarities[error_indices].max(axis=-1)
    sorted_order = np.argsort(error_confidences)[::-1]
    top_error_indices = error_indices[sorted_order[:n]]

    def get_hypothesis(true_class, pred_class):
        hypotheses = [
            f"CLIP мог перепутать '{true_class}' с '{pred_class}' из-за схожего "
            f"визуального облика или редкого представления в обучающих данных CLIP.",
            f"Текстовое описание '{pred_class}' могло быть лучше представлено "
            f"в интернет-текстах, на которых обучался CLIP.",
            f"Возможно, изображение содержит нетипичный ракурс или освещение, "
            f"что затруднило распознавание '{true_class}'.",
            f"'{true_class}' и '{pred_class}' могут иметь схожие цвета или форму лепестков, "
            f"что вводит CLIP в заблуждение при zero-shot классификации.",
        ]
        import hashlib
        idx = int(hashlib.md5(f"{true_class}{pred_class}".encode()).hexdigest(), 16) % len(hypotheses)
        return hypotheses[idx]

    cols = 4
    rows = (n + cols - 1) // cols
    fig, axes = plt.subplots(rows, cols, figsize=(cols * 4, rows * 5.5))
    axes = axes.flatten()

    for plot_idx, data_idx in enumerate(top_error_indices):
        img, label = test_dataset[data_idx]
        true_class = class_names[label]
        pred_class = class_names[all_preds[data_idx]]
        confidence = all_similarities[data_idx].max()

        ax = axes[plot_idx]
        img_np = np.array(img)
        ax.imshow(img_np)
        ax.set_title(
            f"Истинный: {true_class}\nПредсказан: {pred_class}\nСходство: {confidence:.3f}",
            fontsize=8, color="black", pad=4
        )
        ax.axis("off")

        hypothesis = get_hypothesis(true_class, pred_class)
        ax.text(
            0.5, -0.05, hypothesis,
            transform=ax.transAxes,
            fontsize=6, ha="center", va="top",
            wrap=True, color="gray",
            bbox=dict(boxstyle="round,pad=0.2", fc="lightyellow", alpha=0.7)
        )

    for i in range(len(top_error_indices), len(axes)):
        axes[i].axis("off")

    plt.suptitle("Топ ошибок CLIP (наибольшая уверенность при неверном предсказании)",
                 fontsize=12, fontweight="bold")
    plt.tight_layout()
    plt.savefig("top_clip_errors.png", dpi=120, bbox_inches="tight")
    plt.show()
    print("Сохранено: top_clip_errors.png")


if __name__ == '__main__':
    # A--------------------------------------------------------------------
    test_dataset = datasets.Flowers102(root='./data', split='test',
                                       download=True, transform=None)

    # pil_collate_fn нужен потому что transform=None — изображения остаются PIL,
    # а стандартный DataLoader не умеет складывать их в батч
    test_loader = torch.utils.data.DataLoader(
        dataset=test_dataset, batch_size=64, shuffle=False,
        collate_fn=pil_collate_fn
    )

    model_id = "openai/clip-vit-base-patch32"
    model = CLIPModel.from_pretrained(model_id).to(device)
    processor = CLIPProcessor.from_pretrained(model_id)

    class_names = test_dataset.classes

    # B--------------------------------------------------------------------
    base_template = "a photo of a {}"
    accuracy, all_preds, all_labels = evaluate_with_template(
        model, processor, test_loader, class_names, base_template, device
    )

    print(f"Zero-shot accuracy: {accuracy*100:.2f}%")

    cm = confusion_matrix(all_labels, all_preds)
    disp = ConfusionMatrixDisplay(cm)

    n_classes = len(class_names)
    figsize = (max(10, n_classes * 0.5), max(10, n_classes * 0.5))
    fig, ax = plt.subplots(figsize=figsize)

    disp.plot(ax=ax, xticks_rotation=45, colorbar=False)

    ax.xaxis.label.set_visible(False)
    ax.yaxis.label.set_visible(False)

    plt.title("Confusion Matrix (CLIP zero-shot)")
    plt.tight_layout()
    plt.show()

    for i, class_name in enumerate(class_names):
        mask = all_labels == i
        if mask.sum() == 0:
            continue
        class_acc = np.mean(all_preds[mask] == all_labels[mask])
        print(f"{class_name:30s}: {class_acc * 100:.1f}%")

    # C--------------------------------------------------------------------
    single_templates = [
        "{}",
        "a photo of a {}",
        "a photograph of a {}",
        "a {} flower in a garden",
        "a close-up photo of a {} flower",
    ]

    print("\n" + "="*60)
    print("ЧАСТЬ C: ЭКСПЕРИМЕНТЫ С ПРОМПТАМИ")
    print("="*60)
    print(f"{'Шаблон':<45} {'Accuracy':>10}")
    print("-"*60)

    results = {}
    for template in single_templates:
        acc, _, _ = evaluate_with_template(
            model, processor, test_loader, class_names, template, device
        )
        results[template] = acc
        print(f"{template:<45} {acc*100:>9.2f}%")

    worst_template = min(results, key=results.get)
    best_template = max(results, key=results.get)

    ensemble_templates = [
        "a photo of a {}",
        "a photograph of a {}",
        "an image of a {}",
        "a picture of a {}",
        "a {} in a photo",
    ]
    acc_ensemble, preds_ens, labels_ens, sims_ens = evaluate_ensemble(
        model, processor, test_loader, class_names, ensemble_templates, device
    )

    print("-"*60)
    print("\nИТОГОВАЯ ТАБЛИЦА:")
    print(f"{'Шаблон':<35} {'Accuracy':>10}")
    print("-"*50)
    print(f"{'Худший одиночный шаблон':<35} {results[worst_template]*100:>9.2f}%")
    print(f"{'Лучший одиночный шаблон':<35} {results[best_template]*100:>9.2f}%")
    print(f"{'Ансамбль (5 шаблонов)':<35} {acc_ensemble*100:>9.2f}%")

    print("\nВизуализация топ ошибок CLIP...")
    visualize_top_errors(
        test_dataset, preds_ens, labels_ens, sims_ens, class_names, n=8
    )