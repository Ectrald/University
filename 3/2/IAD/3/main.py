import torch
import torch.nn as nn
from torch.nn import Sequential
from torchvision import datasets
import torchvision.models as models
from torchvision.transforms import v2 as transforms, InterpolationMode
from torch.utils.data import DataLoader, Subset
import numpy as np
import matplotlib.pyplot as plt
from enum import Enum
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay

# Трансформ - предобработка каждого изображения перед загружкой в датасет
# simple_transform = transforms.Compose([
#     transforms.Resize((224, 224)),
#     transforms.ToTensor()
# ])

# блок подсчета значениЙ нормализации
# mean = 0.
# std = 0.
# n_samples = 0.
#
# for imgs, _ in train_loader:
#     # imgs.shape = [100, 3, 128, 128], значения 0.0-1.0
#     batch_mean = imgs.mean([0, 2, 3])  # среднее по батчу: [3] (R,G,B)
#     batch_std = imgs.std([0, 2, 3])  # std по батчу: [3]
#
#     mean += batch_mean * imgs.size(0)  # взвешенное суммирование
#     std += batch_std * imgs.size(0)
#     n_samples += imgs.size(0)
#
# mean /= n_samples  # финальное среднее
# std /= n_samples  # финальное std
#
# print(f"Mean: {mean.tolist()}")
# print(f"Std:  {std.tolist()}")

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

train_transform = transforms.Compose(
        [transforms.ToImage(),
         transforms.Resize((224, 224), interpolation=InterpolationMode.BICUBIC, antialias=True),
         #Геометрическая аугментация
         transforms.RandomHorizontalFlip(p=0.5),
         transforms.RandomResizedCrop(size=(224, 224), scale=(0.08, 1.0), antialias=True),
         transforms.RandomRotation(degrees=15),
         # Цветовая аугментация
         transforms.ColorJitter(brightness=0.3, contrast=0.3, saturation=0.2, hue=0.05),
         transforms.ToDtype(torch.float32, scale=True),
         transforms.Normalize((0.4301987886428833, 0.457500696182251, 0.45386970043182373),
                              (0.2544321119785309, 0.25077781081199646, 0.26713091135025024))
         ])

test_transform = transforms.Compose([
        transforms.ToImage(),
        transforms.Resize((224, 224), interpolation=InterpolationMode.BICUBIC, antialias=True),
        transforms.ToDtype(torch.float32, scale=True),
        transforms.Normalize((0.4301987886428833, 0.457500696182251, 0.45386970043182373),
                             (0.2544321119785309, 0.25077781081199646, 0.26713091135025024))
    ])

train_transform_imagenet = transforms.Compose(
        [transforms.ToImage(),
         transforms.Resize((224, 224), interpolation=InterpolationMode.BICUBIC, antialias=True),
         #Геометрическая аугментация
         transforms.RandomHorizontalFlip(p=0.5),
         transforms.RandomResizedCrop(size=(224, 224), scale=(0.08, 1.0), antialias=True),
         transforms.RandomRotation(degrees=15),
         # Цветовая аугментация
         transforms.ColorJitter(brightness=0.3, contrast=0.3, saturation=0.2, hue=0.05),
         transforms.ToDtype(torch.float32, scale=True),
         transforms.Normalize([0.485,0.456,0.406],
                              [0.229,0.224,0.225])
         ])

test_transform_imagenet = transforms.Compose([
        transforms.ToImage(),
        transforms.Resize((224, 224), interpolation=InterpolationMode.BICUBIC, antialias=True),
        transforms.ToDtype(torch.float32, scale=True),
        transforms.Normalize([0.485, 0.456, 0.406],
                         [0.229, 0.224, 0.225])
    ])

def data_preprocessing(train_root: str, test_root: str, train_transform, test_transform, batch_size, num_workers):
    # Создание тензоров из папки
    train_dataset_full = datasets.ImageFolder(root=train_root, transform=train_transform)
    val_dataset_full = datasets.ImageFolder(root=train_root, transform=test_transform)
    indices = list(range(len(train_dataset_full)))
    np.random.seed(42)
    np.random.shuffle(indices)

    split = int(0.8 * len(indices))
    train_indices = indices[:split]
    val_indices = indices[split:]

    train_subset = Subset(train_dataset_full, train_indices)
    val_subset = Subset(val_dataset_full, val_indices)
    test_dataset = datasets.ImageFolder(root=test_root, transform=test_transform)

    # лоадеры для датасета
    train_loader = DataLoader(dataset=train_subset, batch_size=batch_size, shuffle=True, num_workers=num_workers)
    val_loader = DataLoader(dataset=val_subset, batch_size=batch_size, shuffle=False, num_workers=num_workers)
    test_loader = DataLoader(dataset=test_dataset, batch_size=batch_size, shuffle=False, num_workers=num_workers)

    return train_loader, test_loader, val_loader


def create_cnn():
    class CNN(nn.Module):
        def __init__(self):
            super(CNN, self).__init__()
            self.layer1 = nn.Sequential(
                nn.Conv2d(in_channels=3, out_channels=32, kernel_size=5, stride=1, padding=2, bias=False),
                nn.BatchNorm2d(num_features=32),
                nn.ReLU(inplace=True),
                nn.MaxPool2d(kernel_size=2, stride=2),
            )
            self.layer2 = nn.Sequential(
                nn.Conv2d(in_channels=32, out_channels=64, kernel_size=3, stride=1, padding=1, bias=False),
                nn.BatchNorm2d(num_features=64),
                nn.ReLU(inplace=True),
                nn.MaxPool2d(kernel_size=2, stride=2),
            )
            self.dropout2d = nn.Dropout2d(p=0.25)
            self.adaptive_pool = nn.AdaptiveAvgPool2d((7, 7))
            self.fc1 = nn.Linear(64 * 7 * 7, 512)
            self.bn_fc = nn.BatchNorm1d(512)
            self.relu = nn.ReLU(inplace=True)
            self.dropout = nn.Dropout(p=0.5)
            self.fc2 = nn.Linear(512, 6)

        def forward(self, x):
            x = self.layer1(x)
            x = self.layer2(x)

            x = self.adaptive_pool(x)
            x = self.dropout2d(x)

            x = torch.flatten(x, 1)

            x = self.fc1(x)
            x = self.bn_fc(x)
            x = self.relu(x)
            x = self.dropout(x)

            out = self.fc2(x)

            return out

    model = CNN()
    return model

class TrainMode(Enum):
    SCRATCH = 'scratch'
    FT_FROZEN = 'ft_frozen'
    FT_FULL = 'ft_full'

def train_model(model, train_loader, val_loader, num_epochs, learning_rate, mode):
    model = model.to(device)

    criterion = nn.CrossEntropyLoss()
    if mode == TrainMode.SCRATCH:
        optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate, weight_decay=5e-4)

    if mode == TrainMode.FT_FROZEN:
        optimizer = torch.optim.Adam(
            filter(lambda p: p.requires_grad, model.parameters()),
            lr=learning_rate,
            weight_decay=5e-4
        )

    if mode == TrainMode.FT_FULL:
        head_params = model.fc.parameters()
        backbone_params = [p for name, p in model.named_parameters() if "fc" not in name]
        optimizer = torch.optim.Adam([
            {'params': backbone_params, 'lr': 1e-4},
            {'params': head_params, 'lr': 1e-3},
        ])

    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='max', factor=0.5, patience=2)

    train_losses = []
    val_accuracies = []

    best_val_acc = 0.0
    early_stop_patience = 4
    patience_counter = 0


    save_path = f"best_{model.__class__.__name__}_{mode.value}.pth"


    for epoch in range(num_epochs):
        model.train()
        running_loss = 0.0

        for batch_idx, (inputs, targets) in enumerate(train_loader):
            inputs, targets = inputs.to(device), targets.to(device)
            optimizer.zero_grad()

            outputs = model(inputs)
            loss = criterion(outputs, targets)

            loss.backward()

            optimizer.step()

            running_loss += loss.item() * inputs.size(0)

        epoch_loss = running_loss / len(train_loader.dataset)
        train_losses.append(epoch_loss)

        model.eval()
        correct = 0
        total = 0
        with torch.no_grad():
            for inputs, targets in val_loader:
                inputs, targets = inputs.to(device), targets.to(device)
                outputs = model(inputs)

                _, predicted = torch.max(outputs.data, 1)
                total += targets.size(0)
                correct += (predicted == targets).sum().item()

        val_acc = 100.0 * correct / total
        val_accuracies.append(val_acc)

        print(f"[{model.__class__.__name__}] Эпоха [{epoch + 1}/{num_epochs}], Train Loss: {epoch_loss:.4f}, Val Acc: {val_acc:.2f}%")

        scheduler.step(val_acc)
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            patience_counter = 0
            torch.save(model.state_dict(), save_path)
        else:
            patience_counter += 1
            if patience_counter >= early_stop_patience:
                print(
                    f"Early Stopping! Модель больше не может улучшить скор за последние {early_stop_patience} эпох(-и).")
                break
    return train_losses, val_accuracies, save_path

def evaluate_model(model, test_loader, weights_path):
    model.to(device)
    model.load_state_dict(torch.load(weights_path, weights_only=True))
    model.eval()
    correct = 0
    total = 0
    with torch.no_grad():
        for inputs, targets in test_loader:
            inputs, targets = inputs.to(device), targets.to(device)
            outputs = model(inputs)
            _, predicted = torch.max(outputs.data, 1)
            total += targets.size(0)
            correct += (predicted == targets).sum().item()
    return 100.0 * correct / total

def create_model_ft(mode, num_classes = 6):
    model_ft_frozen = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
    if mode == TrainMode.FT_FROZEN:
        for param in model_ft_frozen.parameters():
            param.requires_grad = False

    num_ftrs = model_ft_frozen.fc.in_features

    model_ft_frozen.fc = Sequential(
        nn.Linear(num_ftrs, 512),
        nn.BatchNorm1d(512),
        nn.ReLU(inplace=True),
        nn.Dropout(p=0.5),
        nn.Linear(512, num_classes),
    )

    return model_ft_frozen


def visualize_filters(weights_path: str = "best_ResNet_ft_full.pth",
                              max_filters: int = 64,
                              save_path: str = "ft_full_conv1_filters.png"):
    """
    Визуализирует фильтры первого сверточного слоя (conv1) модели ResNet18 FT_FULL.

    Параметры
    ----------
    weights_path : str
        Путь к файлу с сохранёнными весами модели (.pth).
    max_filters : int
        Максимальное число фильтров для отображения (не более 64).
    save_path : str
        Куда сохранить итоговое изображение. Передайте None, чтобы не сохранять.
    """
    model = create_model_ft(TrainMode.FT_FULL)
    state_dict = torch.load(weights_path, map_location="cpu", weights_only=True)
    model.load_state_dict(state_dict)
    model.eval()

    # conv1: shape = [64, 3, 7, 7]  (out_channels, in_channels, H, W)
    first_conv = model.conv1
    filters = first_conv.weight.detach().cpu()  # [64, 3, 7, 7]
    print(f"[visualize] conv1.weight.shape = {filters.shape}")

    n_filters = min(max_filters, filters.shape[0])
    filters = filters[:n_filters]  # берём первые n_filters фильтров

    f_min = filters.flatten(1).min(dim=1).values[:, None, None, None]
    f_max = filters.flatten(1).max(dim=1).values[:, None, None, None]
    filters_norm = (filters - f_min) / (f_max - f_min + 1e-8)  # [N, 3, 7, 7]

    ncols = 8
    nrows = (n_filters + ncols - 1) // ncols

    fig, axes = plt.subplots(nrows, ncols,
                             figsize=(ncols * 1.4, nrows * 1.4))
    fig.suptitle(
        f"ResNet18 FT_FULL — фильтры conv1  ({n_filters} из {first_conv.weight.shape[0]})\n"
        f"Размер ядра: {first_conv.kernel_size}  |  Веса: {weights_path}",
        fontsize=11, y=1.01
    )

    axes_flat = axes.flatten() if nrows > 1 else [axes] if ncols == 1 else axes.flatten()

    for idx, ax in enumerate(axes_flat):
        if idx < n_filters:
            # Переводим [3, H, W] → [H, W, 3] для imshow
            img = filters_norm[idx].permute(1, 2, 0).numpy()
            ax.imshow(img, interpolation="nearest")
            ax.set_title(f"#{idx}", fontsize=7, pad=2)
        ax.axis("off")

    plt.tight_layout()

    if save_path is not None:
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
        print(f"[visualize] Изображение сохранено → {save_path}")

    plt.show()


def visualize_activation_maps(weights_path: str = "best_ResNet_ft_full.pth",
                              test_root: str = "seg_test/seg_test",
                              n_images: int = 3,
                              n_channels: int = 16,
                              save_dir: str = "."):
    """
    Визуализирует карты активаций модели ResNet18 FT_FULL для нескольких тестовых изображений.

    Параметры
    ----------
    weights_path : str
        Путь к файлу с весами модели.
    test_root : str
        Путь к тестовой выборке (структура ImageFolder).
    n_images : int
        Сколько изображений отобразить (функция ищет правильно и неправильно
        классифицированные примеры из разных классов).
    n_channels : int
        Сколько каналов (карт) показать для каждого слоя (8 или 16).
    save_dir : str
        Папка для сохранения PNG-файлов. Передайте None, чтобы не сохранять.
    """
    import math
    import os

    # ── 1. Модель ────────────────────────────────────────────────────────────
    model = create_model_ft(TrainMode.FT_FULL)
    state_dict = torch.load(weights_path, map_location="cpu", weights_only=True)
    model.load_state_dict(state_dict)
    model.eval()

    # ── 2. Хуки для извлечения активаций layer1 и layer3 ────────────────────
    # layer1 — ранние признаки (края, текстуры)
    # layer3 — глубокие семантические признаки
    activations = {}

    def hook_fn(name):
        def hook(module, inp, output):
            activations[name] = output.detach().cpu()

        return hook

    h1 = model.layer1.register_forward_hook(hook_fn("layer1"))
    h3 = model.layer3.register_forward_hook(hook_fn("layer3"))

    # ── 3. Загружаем тестовую выборку ────────────────────────────────────────
    test_dataset = datasets.ImageFolder(root=test_root, transform=test_transform_imagenet)
    class_names = test_dataset.classes  # список имён классов

    # Собираем по одному примеру на класс (перебираем датасет один раз)
    class_to_sample = {}  # class_idx → (tensor, label, raw_pil)
    raw_dataset = datasets.ImageFolder(root=test_root)  # без нормализации — для отображения
    to_tensor = transforms.Compose([
        transforms.ToImage(),
        transforms.Resize((224, 224), interpolation=InterpolationMode.BICUBIC, antialias=True),
        transforms.ToDtype(torch.float32, scale=True),
    ])

    for idx in range(len(test_dataset)):
        img_tensor, label = test_dataset[idx]
        if label not in class_to_sample:
            raw_img, _ = raw_dataset[idx]  # PIL Image
            class_to_sample[label] = (img_tensor, label, to_tensor(raw_img))
        if len(class_to_sample) >= len(class_names):
            break

    # ── 4. Прямой проход и разбивка на правильные / неправильные ─────────────
    correct_samples = []  # (img_tensor, label, display_tensor, pred)
    incorrect_samples = []

    for label, (img_tensor, lbl, disp_tensor) in class_to_sample.items():
        with torch.no_grad():
            logits = model(img_tensor.unsqueeze(0))
        pred = logits.argmax(dim=1).item()
        entry = (img_tensor, lbl, disp_tensor, pred)
        if pred == lbl:
            correct_samples.append(entry)
        else:
            incorrect_samples.append(entry)

    # Формируем итоговый список: сначала неправильные, потом правильные
    selected = (incorrect_samples + correct_samples)[:n_images]
    if len(selected) < n_images:
        print(f"[visualize] Внимание: найдено только {len(selected)} образцов (запрошено {n_images}).")

    # ── 5. Для каждого изображения рисуем карты активаций ───────────────────
    for sample_idx, (img_tensor, true_label, disp_tensor, pred_label) in enumerate(selected):
        # Прямой проход с хуками
        with torch.no_grad():
            model(img_tensor.unsqueeze(0))

        verdict = "✓ верно" if pred_label == true_label else "✗ неверно"
        true_name = class_names[true_label]
        pred_name = class_names[pred_label]
        title_base = (f"Класс: {true_name}  |  Предсказание: {pred_name}  [{verdict}]")

        for layer_name in ("layer1", "layer3"):
            feat = activations[layer_name]  # [1, C, H, W]
            feat = feat.squeeze(0)  # [C, H, W]

            n_show = min(n_channels, feat.shape[0])
            ncols = 8
            nrows = math.ceil(n_show / ncols) + 1  # +1 строка для оригинала

            fig = plt.figure(figsize=(ncols * 1.5, nrows * 1.5))
            fig.suptitle(
                f"ResNet18 FT_FULL — активации «{layer_name}»\n{title_base}",
                fontsize=10, y=1.01
            )

            # ── первая ячейка: исходное изображение ──────────────────────────
            ax0 = fig.add_subplot(nrows, ncols, 1)
            disp_np = disp_tensor.permute(1, 2, 0).numpy()
            disp_np = np.clip(disp_np, 0, 1)
            ax0.imshow(disp_np)
            ax0.set_title("Оригинал", fontsize=7)
            ax0.axis("off")

            # ── остальные ячейки: каналы активаций ───────────────────────────
            for ch_idx in range(n_show):
                ax = fig.add_subplot(nrows, ncols, ch_idx + 2)
                act_map = feat[ch_idx].numpy()  # [H, W]

                # Нормализация карты в [0, 1]
                a_min, a_max = act_map.min(), act_map.max()
                if a_max > a_min:
                    act_map = (act_map - a_min) / (a_max - a_min)

                ax.imshow(act_map, cmap="viridis", interpolation="nearest")
                ax.set_title(f"ch{ch_idx}", fontsize=6, pad=1)
                ax.axis("off")

            # Скрываем пустые ячейки
            total_cells = nrows * ncols
            for empty in range(n_show + 2, total_cells + 1):
                fig.add_subplot(nrows, ncols, empty).axis("off")

            plt.tight_layout()

            if save_dir is not None:
                fname = os.path.join(
                    save_dir,
                    f"activations_img{sample_idx}_{layer_name}_{verdict[2:]}.png"
                )
                plt.savefig(fname, dpi=150, bbox_inches="tight")
                print(f"[visualize] Сохранено → {fname}")

            plt.show()

    # Удаляем хуки, чтобы не засорять модель
    h1.remove()
    h3.remove()


def visualize_grad_cam(weights_path: str = "best_ResNet_ft_full.pth",
                       test_root: str = "seg_test/seg_test",
                       n_correct: int = 4,
                       n_incorrect: int = 4,
                       save_dir: str = "."):
    """
    Grad-CAM для модели ResNet18 FT_FULL: накладывает тепловую карту на исходное
    изображение для n_correct правильно и n_incorrect неправильно
    классифицированных примеров из разных классов.

    Параметры
    ----------
    weights_path : str
        Путь к файлу с весами модели.
    test_root : str
        Путь к тестовой выборке (структура ImageFolder).
    n_correct : int
        Число правильно классифицированных изображений (желательно из разных классов).
    n_incorrect : int
        Число неправильно классифицированных изображений.
    save_dir : str
        Папка для сохранения результатов. None — не сохранять.
    """
    import torch.nn.functional as F
    import os
    import math

    # ── 1. Модель ──────────────────────────────────────────────────────────────
    model = create_model_ft(TrainMode.FT_FULL)
    state_dict = torch.load(weights_path, map_location="cpu", weights_only=True)
    model.load_state_dict(state_dict)
    model.eval()

    # ── 2. Регистрируем хуки на последний сверточный слой (layer4) ────────────
    # ResNet18: layer4[-1].conv2 — последний conv перед global avg pool
    target_layer = model.layer4[-1].conv2

    gradients = {}
    activations_gc = {}

    def save_activation_gc(module, inp, output):
        activations_gc["target"] = output  # НЕ detach — нужен граф для backward

    def save_gradient_gc(module, grad_input, grad_output):
        gradients["target"] = grad_output[0].detach().cpu()

    fwd_hook = target_layer.register_forward_hook(save_activation_gc)
    bwd_hook = target_layer.register_full_backward_hook(save_gradient_gc)

    # ── 3. Датасет: две версии одного файла ───────────────────────────────────
    # norm_dataset  — нормализованные тензоры для модели
    # disp_dataset  — [0,1] тензоры для отображения
    norm_dataset = datasets.ImageFolder(root=test_root, transform=test_transform_imagenet)
    disp_transform = transforms.Compose([
        transforms.ToImage(),
        transforms.Resize((224, 224), interpolation=InterpolationMode.BICUBIC, antialias=True),
        transforms.ToDtype(torch.float32, scale=True),
    ])
    disp_dataset = datasets.ImageFolder(root=test_root, transform=disp_transform)
    class_names = norm_dataset.classes

    # ── 4. Набираем нужное кол-во верных / неверных из разных классов ─────────
    correct_by_class = {}  # class_idx → (norm_tensor, disp_tensor, label, pred)
    incorrect_samples = []

    for idx in range(len(norm_dataset)):
        if (len(correct_by_class) >= n_correct and
                len(incorrect_samples) >= n_incorrect):
            break

        norm_img, label = norm_dataset[idx]
        disp_img, _ = disp_dataset[idx]

        # Прямой проход (без torch.no_grad, чтобы backward работал позже)
        output = model(norm_img.unsqueeze(0))
        pred = output.argmax(dim=1).item()

        if pred == label:
            if label not in correct_by_class and len(correct_by_class) < n_correct:
                correct_by_class[label] = (norm_img, disp_img, label, pred)
        else:
            if len(incorrect_samples) < n_incorrect:
                incorrect_samples.append((norm_img, disp_img, label, pred))

    samples = list(correct_by_class.values()) + incorrect_samples
    total = len(samples)
    if total == 0:
        print("[grad_cam] Не удалось найти ни одного подходящего изображения.")
        fwd_hook.remove();
        bwd_hook.remove()
        return
    print(f"[grad_cam] Найдено {len(correct_by_class)} верных и "
          f"{len(incorrect_samples)} неверных образцов.")

    # ── 5. Вычисляем Grad-CAM и строим графики ────────────────────────────────
    ncols = 4
    nrows = math.ceil(total / ncols)
    fig, axes = plt.subplots(nrows, ncols,
                             figsize=(ncols * 3.5, nrows * 3.5))
    fig.suptitle("ResNet18 FT_FULL — Grad-CAM  (layer4[-1].conv2)",
                 fontsize=13, y=1.01)
    axes_flat = axes.flatten() if total > 1 else [axes]

    for i, (norm_img, disp_img, true_label, pred_label) in enumerate(samples):
        # — Прямой проход (сохраняет активации через хук) —
        model.zero_grad()
        output = model(norm_img.unsqueeze(0))  # [1, num_classes]
        pred_score = output[0, pred_label]  # скор предсказанного класса

        # — Обратный проход (сохраняет градиенты через хук) —
        pred_score.backward()

        # — Grad-CAM —
        grads = gradients["target"]  # [1, C, H, W]
        acts = activations_gc["target"].detach().cpu()  # [1, C, H, W]

        weights_cam = grads.mean(dim=(2, 3), keepdim=True)  # GAP по H,W → [1, C, 1, 1]
        cam = (weights_cam * acts).sum(dim=1, keepdim=True)  # [1, 1, H, W]
        cam = F.relu(cam)

        H, W = disp_img.shape[1], disp_img.shape[2]
        cam = F.interpolate(cam, size=(H, W), mode="bilinear", align_corners=False)
        cam = cam.squeeze().numpy()  # [H, W]
        cam = (cam - cam.min()) / (cam.max() - cam.min() + 1e-8)

        # — Отображение —
        disp_np = disp_img.permute(1, 2, 0).numpy()
        disp_np = np.clip(disp_np, 0, 1)

        verdict = "✓ верно" if pred_label == true_label else "✗ неверно"
        true_name = class_names[true_label]
        pred_name = class_names[pred_label]

        ax = axes_flat[i]
        ax.imshow(disp_np)
        im = ax.imshow(cam, cmap="jet", alpha=0.45)
        ax.set_title(
            f"Истинный: {true_name}\nПред.: {pred_name}  [{verdict}]",
            fontsize=8, color="green" if pred_label == true_label else "red"
        )
        ax.axis("off")
        plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)

    # Скрываем незаполненные ячейки
    for j in range(total, len(axes_flat)):
        axes_flat[j].axis("off")

    plt.tight_layout()

    if save_dir is not None:
        fname = os.path.join(save_dir, "grad_cam_ft_full.png")
        plt.savefig(fname, dpi=150, bbox_inches="tight")
        print(f"[grad_cam] Сохранено → {fname}")

    plt.show()

    fwd_hook.remove()
    bwd_hook.remove()


def analyze_errors(weights_path="best_ResNet_ft_full.pth", test_root="seg_test/seg_test", batch_size=32, num_workers=4):
    """
    Строит матрицу ошибок и выводит топ-3 частых ошибок для модели FT_FULL.
    """
    print(f"\n[Анализ ошибок] Загрузка модели FT_FULL из {weights_path}...")

    # Загружаем тестовый датасет для получения данных и названий классов
    test_dataset = datasets.ImageFolder(root=test_root, transform=test_transform_imagenet)
    test_loader = DataLoader(dataset=test_dataset, batch_size=batch_size, shuffle=False, num_workers=num_workers)
    class_names = test_dataset.classes

    # Создаем и загружаем модель
    model = create_model_ft(TrainMode.FT_FULL)
    model.load_state_dict(torch.load(weights_path, map_location=device, weights_only=True))
    model.to(device)
    model.eval()

    all_preds = []
    all_labels = []

    print("[Анализ ошибок] Сбор предсказаний на тестовой выборке...")
    with torch.no_grad():
        for x_batch, y_batch in test_loader:
            x_batch = x_batch.to(device)
            logits = model(x_batch)
            preds = logits.argmax(dim=1)
            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(y_batch.numpy())

    # --- 1. Построение матрицы ошибок ---
    cm = confusion_matrix(all_labels, all_preds)
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=class_names)

    fig, ax = plt.subplots(figsize=(10, 10))
    disp.plot(ax=ax, xticks_rotation=45, cmap='Blues')
    plt.title("Confusion Matrix (ResNet18 FT_FULL)")
    plt.tight_layout()
    plt.show()

    # --- 2. Поиск топ-3 частых ошибок ---
    errors = []
    for i in range(len(class_names)):
        for j in range(len(class_names)):
            if i != j:  # Игнорируем правильные предсказания (диагональ)
                count = cm[i, j]
                if count > 0:
                    errors.append((count, class_names[i], class_names[j]))

    # Сортируем ошибки по убыванию количества
    errors.sort(key=lambda x: x[0], reverse=True)

    print("\n" + "=" * 50)
    print("ТОП-3 НАИБОЛЕЕ ЧАСТЫЕ ОШИБКИ КЛАССИФИКАЦИИ:")
    print("=" * 50)
    for idx in range(min(3, len(errors))):
        count, true_class, pred_class = errors[idx]
        print(f"{idx + 1}. Истинный класс: '{true_class}' | Модель предсказала: '{pred_class}' | Ошибок: {count}")
    print("=" * 50 + "\n")

if __name__ == "__main__":
    from multiprocessing import freeze_support
    freeze_support()
    current_mode = TrainMode.SCRATCH
    print(f"Device: {device}")
    n = int(input("""
    1 - Обучение модели
    2 - Проверка модели
    3 - Fine tune с замороженными весами
    4 - Проверка ft_frozen
    5 - Fine tune
    6 - Проверка ft
    7 - Таблица сравнения
    8 - Анализ
    """))
    match n:
        case 1:
            current_mode = TrainMode.SCRATCH
            train_loader, test_loader, val_loader = data_preprocessing(train_root="seg_train/seg_train",
                                                                       test_root="seg_test/seg_test",
                                                                       train_transform=train_transform,
                                                                       test_transform=test_transform,
                                                                       batch_size=32,
                                                                       num_workers=4)
            model = create_cnn()
            print("Cтарт обучения")
            train_losses, val_accuracies, weights_path = train_model(model, train_loader, val_loader, num_epochs=15,
                                                                     learning_rate=0.001, mode = current_mode)

            test_acc = evaluate_model(model, test_loader, weights_path)
            print("Итоговая точность:" + str(test_acc))
        case 2:
            model = create_cnn()
            train_loader, test_loader, val_loader = data_preprocessing(train_root="seg_train/seg_train",
                                                                       test_root="seg_test/seg_test",
                                                                       train_transform=train_transform,
                                                                       test_transform=test_transform,
                                                                       batch_size=32,
                                                                       num_workers=4)
            test_acc = evaluate_model(model, test_loader, weights_path="best_CNN_scratch.pth")
            print("Итоговая точность:" + str(test_acc))
        case 3:
            current_mode = TrainMode.FT_FROZEN
            train_loader, test_loader, val_loader = data_preprocessing(train_root="seg_train/seg_train",
                                                                       test_root="seg_test/seg_test",
                                                                       train_transform=train_transform_imagenet,
                                                                       test_transform=test_transform_imagenet,
                                                                       batch_size=32,
                                                                       num_workers=4)
            model = create_model_ft(current_mode)
            print("Cтарт обучения")
            train_losses, val_accuracies, weights_path = train_model(model, train_loader, val_loader, num_epochs=15,
                                                                     learning_rate=0.001, mode=current_mode)

            test_acc = evaluate_model(model, test_loader, weights_path)
            print("Итоговая точность:" + str(test_acc))
        case 4:
            current_mode = TrainMode.FT_FROZEN
            train_loader, test_loader, val_loader = data_preprocessing(train_root="seg_train/seg_train",
                                                                       test_root="seg_test/seg_test",
                                                                       train_transform=train_transform_imagenet,
                                                                       test_transform=test_transform_imagenet,
                                                                       batch_size=32,
                                                                       num_workers=4)
            model = create_model_ft(current_mode)
            test_acc = evaluate_model(model, test_loader, weights_path="best_ResNet_ft_frozen.pth")
            print("Итоговая точность:" + str(test_acc))
        case 5:
            current_mode = TrainMode.FT_FULL
            train_loader, test_loader, val_loader = data_preprocessing(train_root="seg_train/seg_train",
                                                                       test_root="seg_test/seg_test",
                                                                       train_transform=train_transform_imagenet,
                                                                       test_transform=test_transform_imagenet,
                                                                       batch_size=32,
                                                                       num_workers=4)
            model = create_model_ft(current_mode)
            print("Cтарт обучения")
            train_losses, val_accuracies, weights_path = train_model(model, train_loader, val_loader, num_epochs=15,
                                                                     learning_rate=0.001, mode=current_mode)

            test_acc = evaluate_model(model, test_loader, weights_path)
            print("Итоговая точность:" + str(test_acc))
        case 6:
            current_mode = TrainMode.FT_FULL
            train_loader, test_loader, val_loader = data_preprocessing(train_root="seg_train/seg_train",
                                                                       test_root="seg_test/seg_test",
                                                                       train_transform=train_transform_imagenet,
                                                                       test_transform=test_transform_imagenet,
                                                                       batch_size=32,
                                                                       num_workers=4)
            model = create_model_ft(current_mode)
            test_acc = evaluate_model(model, test_loader, weights_path="best_ResNet_ft_full.pth")
            print("Итоговая точность:" + str(test_acc))
        case 7:
            model_ft_frozen = create_model_ft(TrainMode.FT_FROZEN)
            model_ft_full = create_model_ft(TrainMode.FT_FULL)
            model = create_cnn()

            train_loader_ft, test_loader_ft, val_loader_ft = data_preprocessing(train_root="seg_train/seg_train",
                                                                       test_root="seg_test/seg_test",
                                                                       train_transform=train_transform_imagenet,
                                                                       test_transform=test_transform_imagenet,
                                                                       batch_size=32,
                                                                       num_workers=4)
            train_loader, test_loader, val_loader = data_preprocessing(train_root="seg_train/seg_train",
                                                                       test_root="seg_test/seg_test",
                                                                       train_transform=train_transform,
                                                                       test_transform=test_transform,
                                                                       batch_size=32,
                                                                       num_workers=4)
            # Оценка Test accuracy
            test_acc_scratch = evaluate_model(model, test_loader, weights_path="best_CNN_scratch.pth")
            test_acc_ft_frozen = evaluate_model(model_ft_frozen, test_loader_ft,
                                                weights_path="best_ResNet_ft_frozen.pth")
            test_acc_ft_full = evaluate_model(model_ft_full, test_loader_ft, weights_path="best_ResNet_ft_full.pth")

            # Оценка Val accuracy
            val_acc_scratch = evaluate_model(model, val_loader, weights_path="best_CNN_scratch.pth")
            val_acc_ft_frozen = evaluate_model(model_ft_frozen, val_loader_ft, weights_path="best_ResNet_ft_frozen.pth")
            val_acc_ft_full = evaluate_model(model_ft_full, val_loader_ft, weights_path="best_ResNet_ft_full.pth")

            # Подсчет обучаемых параметров
            trainable_params_scratch = sum(p.numel() for p in model.parameters() if p.requires_grad)
            trainable_params_frozen = sum(p.numel() for p in model_ft_frozen.parameters() if p.requires_grad)
            trainable_params_ft = sum(p.numel() for p in model_ft_full.parameters() if p.requires_grad)

            # Отрисовка таблицы
            print("-" * 145)
            print(
                f"| {'Модель':<10} | {'Режим':<36} | {'Число обучаемых параметров':<26} | {'Время обучения':<15} | {'Эпох до сходимости':<18} | {'Val accuracy':<12} | {'Test accuracy':<13} |")
            print("-" * 145)
            print(
                f"| {'CNN':<10} | {'С нуля':<36} | {trainable_params_scratch:<26} | {'...':<15} | {'...':<18} | {val_acc_scratch:>11.2f}% | {test_acc_scratch:>12.2f}% |")
            print(
                f"| {'ResNet18':<10} | {'Предобученная с замороженными слоями':<36} | {trainable_params_frozen:<26} | {'...':<15} | {'...':<18} | {val_acc_ft_frozen:>11.2f}% | {test_acc_ft_frozen:>12.2f}% |")
            print(
                f"| {'ResNet18':<10} | {'Fine-tuning':<36} | {trainable_params_ft:<26} | {'...':<15} | {'...':<18} | {val_acc_ft_full:>11.2f}% | {test_acc_ft_full:>12.2f}% |")
            print("-" * 145)
        case 8:
            visualize_filters()
            visualize_activation_maps()
            visualize_grad_cam()
            analyze_errors()
        case _:
            print("Invalid input")







