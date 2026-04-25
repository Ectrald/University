import os
os.environ['NCCL_P2P_DISABLE'] = '1'
os.environ['NCCL_IB_DISABLE'] = '1'
import torch
import torchvision.models as tv_models
import albumentations as A
from albumentations.pytorch import ToTensorV2
from torch.utils.data import Dataset, DataLoader
import os
import numpy as np
from PIL import Image
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import matplotlib.pyplot as plt
from tqdm import tqdm

# Device
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# Global variables
IMAGE_ROOT_TRAIN = "./images/train"
IMAGE_ROOT_VAL   = "./images/val"
IMAGE_ROOT_TEST  = "./images/test"
MASK_ROOT_TRAIN  = "./ground_truth/train"
MASK_ROOT_VAL    = "./ground_truth/val"
MASK_ROOT_TEST   = "./ground_truth/test"

CLASS_NAMES = [
    "Background", "Outdoor structures", "Buildings",
    "Paved ground", "Non-paved ground", "Train tracks",
    "Plants", "Wheeled vehicles", "Water", "People",
]

IMAGE_SIZE  = 384
BATCH_SIZE  = 4
NUM_WORKERS = 4
NUM_CLASSES = 10

n_gpus = torch.cuda.device_count()

# Transform + augmentation
transform_train = A.Compose([
    A.HorizontalFlip(p=0.5),
    A.RandomBrightnessContrast(p=0.3),
    A.Normalize(mean=(0.485, 0.456, 0.406),
                std=(0.229, 0.224, 0.225)),
    ToTensorV2(),
])
transform_val = A.Compose([
    A.Normalize(mean=(0.485, 0.456, 0.406),
                std=(0.229, 0.224, 0.225)),
    ToTensorV2(),
])


# Dataset
class SegmentationDataset(Dataset):
    def __init__(self, images_paths, masks_paths, transform=None, img_size=IMAGE_SIZE):
        self.transform = transform
        self.images = []
        self.masks = []

        resize = A.Resize(img_size, img_size)

        for img_path, mask_path in tqdm(zip(images_paths, masks_paths),
                                        total=len(images_paths),
                                        desc="Загрузка датасета в RAM"):
            img = np.array(Image.open(img_path).convert("RGB"))
            mask = np.array(Image.open(mask_path))

            if mask.ndim == 3:
                mask = mask[:, :, 0]

            transformed = resize(image=img, mask=mask)
            self.images.append(transformed['image'])
            self.masks.append(np.clip(transformed['mask'], 0, NUM_CLASSES - 1))

    def __len__(self):
        return len(self.images)

    def __getitem__(self, idx):
        image = self.images[idx]
        mask  = self.masks[idx]

        if self.transform:
            transformed = self.transform(image=image, mask=mask)
            image = transformed['image']
            mask  = transformed['mask'].long()

        return image, mask


def create_segmentation_dataset(images_root, masks_root, transform=None):

    valid_exts = ('.jpg', '.png')
    all_files  = sorted([
        f for f in os.listdir(images_root)
        if f.lower().endswith(valid_exts)
    ])

    img_paths, msk_paths = [], []
    for f in all_files:
        img_p = os.path.join(images_root, f)
        # Маска всегда PNG с тем же базовым именем
        base  = os.path.splitext(f)[0]
        msk_p = os.path.join(masks_root, base + '.png')
        if os.path.exists(msk_p):
            img_paths.append(img_p)
            msk_paths.append(msk_p)
        else:
            print(f"[Предупреждение] Маска не найдена для '{f}', пропускаем.")

    return SegmentationDataset(img_paths, msk_paths, transform)


def get_loaders(train_dataset, val_dataset, test_dataset, batch_size, num_workers):
    train_loader = DataLoader(train_dataset, batch_size=batch_size,
                              shuffle=True,  num_workers=num_workers)
    val_loader   = DataLoader(val_dataset,   batch_size=batch_size,
                              shuffle=False, num_workers=num_workers)
    test_loader  = DataLoader(test_dataset,  batch_size=batch_size,
                              shuffle=False, num_workers=num_workers)
    return train_loader, val_loader, test_loader


# UNet model
class UNet(nn.Module):
    # 2 conv layers block
    class _TwoConvLayers(nn.Module):
        def __init__(self, in_channels, out_channels):
            super().__init__()
            self.model = nn.Sequential(
                nn.Conv2d(in_channels,  out_channels, kernel_size=3, padding=1, bias=False),
                nn.ReLU(),
                nn.BatchNorm2d(out_channels),
                nn.Conv2d(out_channels, out_channels, kernel_size=3, padding=1, bias=False),
                nn.ReLU(),
                nn.BatchNorm2d(out_channels),
            )
        def forward(self, x):
            return self.model(x)

    # encoder block
    class _EncoderBlock(nn.Module):
        def __init__(self, in_channels, out_channels):
            super().__init__()
            self.block    = UNet._TwoConvLayers(in_channels, out_channels)
            self.max_pool = nn.MaxPool2d(kernel_size=2, stride=2)
        def forward(self, x):
            x = self.block(x)
            y = self.max_pool(x)
            return y, x

    # decoder block
    class _DecoderBlock(nn.Module):
        def __init__(self, in_channels, out_channels):
            super().__init__()
            self.transpose = nn.ConvTranspose2d(in_channels, out_channels,
                                                kernel_size=2, stride=2)
            self.block     = UNet._TwoConvLayers(in_channels, out_channels)
        def forward(self, x, y):
            x = self.transpose(x)
            u = torch.cat((x, y), dim=1)
            return self.block(u)

    def __init__(self, in_channels=3, out_channels=NUM_CLASSES):
        super().__init__()
        self.enc_block1 = self._EncoderBlock(in_channels, 64)
        self.enc_block2 = self._EncoderBlock(64,  128)
        self.enc_block3 = self._EncoderBlock(128, 256)
        self.enc_block4 = self._EncoderBlock(256, 512)
        self.bottleneck = self._TwoConvLayers(512, 1024)
        self.dec_block1 = self._DecoderBlock(1024, 512)
        self.dec_block2 = self._DecoderBlock(512,  256)
        self.dec_block3 = self._DecoderBlock(256,  128)
        self.dec_block4 = self._DecoderBlock(128,   64)
        self.out        = nn.Conv2d(64, out_channels, kernel_size=1)

    def forward(self, x):
        x, y1 = self.enc_block1(x)
        x, y2 = self.enc_block2(x)
        x, y3 = self.enc_block3(x)
        x, y4 = self.enc_block4(x)
        x = self.bottleneck(x)
        x = self.dec_block1(x, y4)
        x = self.dec_block2(x, y3)
        x = self.dec_block3(x, y2)
        x = self.dec_block4(x, y1)
        return self.out(x)


# Blocks and ResNet18
class _TwoConv(nn.Module):
    def __init__(self, in_ch, out_ch):
        super().__init__()
        self.block = nn.Sequential(
            nn.Conv2d(in_ch,  out_ch, kernel_size=3, padding=1, bias=False),
            nn.ReLU(inplace=True),
            nn.BatchNorm2d(out_ch),
            nn.Conv2d(out_ch, out_ch, kernel_size=3, padding=1, bias=False),
            nn.ReLU(inplace=True),
            nn.BatchNorm2d(out_ch),
        )
    def forward(self, x):
        return self.block(x)


class _DecoderBlockPretrained(nn.Module):
    def __init__(self, in_ch, skip_ch, out_ch):
        super().__init__()
        self.up   = nn.ConvTranspose2d(in_ch, out_ch, kernel_size=2, stride=2)
        self.conv = _TwoConv(out_ch + skip_ch, out_ch)

    def forward(self, x, skip):
        x = self.up(x)
        x = torch.cat([x, skip], dim=1)
        return self.conv(x)


class UNetResNet18(nn.Module):
    def __init__(self, out_channels=NUM_CLASSES, pretrained=True):
        super().__init__()

        # Encoder
        weights = tv_models.ResNet18_Weights.DEFAULT if pretrained else None
        resnet  = tv_models.resnet18(weights=weights)

        self.enc1 = nn.Sequential(resnet.conv1, resnet.bn1, resnet.relu)
        self.pool = resnet.maxpool
        self.enc2 = resnet.layer1
        self.enc3 = resnet.layer2
        self.enc4 = resnet.layer3

        # Bottleneck
        self.bottleneck = resnet.layer4

        # Decoder
        self.dec1 = _DecoderBlockPretrained(512, 256, 256)
        self.dec2 = _DecoderBlockPretrained(256, 128, 128)
        self.dec3 = _DecoderBlockPretrained(128,  64,  64)
        self.dec4 = _DecoderBlockPretrained( 64,  64,  64)

        self.final_up = nn.Upsample(scale_factor=2, mode='bilinear',
                                    align_corners=True)
        self.out = nn.Conv2d(64, out_channels, kernel_size=1)

    def forward(self, x):
        y1 = self.enc1(x)
        x  = self.pool(y1)
        y2 = self.enc2(x)
        y3 = self.enc3(y2)
        y4 = self.enc4(y3)
        x  = self.bottleneck(y4)

        x = self.dec1(x,  y4)
        x = self.dec2(x,  y3)
        x = self.dec3(x,  y2)
        x = self.dec4(x,  y1)
        x = self.final_up(x)

        return self.out(x)

    def get_param_groups(self):
        encoder_params = (
            list(self.enc1.parameters()) +
            list(self.enc2.parameters()) +
            list(self.enc3.parameters()) +
            list(self.enc4.parameters()) +
            list(self.bottleneck.parameters())
        )
        decoder_params = (
            list(self.dec1.parameters()) +
            list(self.dec2.parameters()) +
            list(self.dec3.parameters()) +
            list(self.dec4.parameters()) +
            list(self.final_up.parameters()) +
            list(self.out.parameters())
        )
        return encoder_params, decoder_params


# Loss
class SoftDiceLoss(nn.Module):
    def __init__(self, smooth=1):
        super().__init__()
        self.smooth = smooth

    def forward(self, logits, targets):
        num   = targets.size(0)
        probs = torch.sigmoid(logits)
        m1    = probs.reshape(num, -1)
        m2    = targets.reshape(num, -1)
        inter = m1 * m2
        score = 2 * (inter.sum(1) + self.smooth) / (m1.sum(1) + m2.sum(1) + self.smooth)
        return 1 - score.sum() / num


# Metrics
def compute_iou_per_class(pred, target, num_classes):
    ious   = []
    pred   = pred.view(-1)
    target = target.view(-1)
    for cls in range(num_classes):
        p     = pred   == cls
        t     = target == cls
        inter = (p & t).sum().item()
        union = (p | t).sum().item()
        ious.append(inter / union if union > 0 else float('nan'))
    return np.array(ious)


def compute_dice_per_class(pred, target, num_classes, smooth=1e-6):
    dices  = []
    pred   = pred.view(-1)
    target = target.view(-1)
    for cls in range(num_classes):
        p     = (pred   == cls).float()
        t     = (target == cls).float()
        inter = (p * t).sum().item()
        denom = p.sum().item() + t.sum().item()
        dices.append((2 * inter + smooth) / (denom + smooth) if denom > 0 else float('nan'))
    return np.array(dices)


def count_parameters(model):
    total     = sum(p.numel() for p in model.parameters())
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    return total, trainable


# Save / load
def save_weights(model, path="model.pth"):
    model_to_save = model.module if isinstance(model, nn.DataParallel) else model
    torch.save(model_to_save.state_dict(), path)
    print(f"Weights saved → {path}")


def load_weights(model, path="model.pth"):
    model_to_load = model.module if isinstance(model, nn.DataParallel) else model
    model_to_load.load_state_dict(torch.load(path, map_location=device))
    model.eval()
    print(f"Weights loaded from '{path}'")


# Train
def train(model, device, train_loader, val_loader, num_epochs,
          optimizer=None):

    if optimizer is None:
        optimizer = optim.AdamW(model.parameters(), lr=5e-4)

    ce_loss   = nn.CrossEntropyLoss()
    dice_loss = SoftDiceLoss()
    history   = {'train_loss': [], 'val_loss': [], 'val_miou': [], 'val_dice': []}

    for epoch in range(num_epochs):

        model.train()
        train_loss_sum = 0.0

        for img, mask in train_loader:
            img, mask = img.to(device), mask.to(device)
            predict   = model(img)
            mask      = mask.long()

            mask_one_hot = F.one_hot(mask, num_classes=NUM_CLASSES) \
                            .permute(0, 3, 1, 2).float()

            l1   = ce_loss(predict, mask)
            l2   = dice_loss(predict, mask_one_hot)
            loss = l1 + l2

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            train_loss_sum += loss.item()


        train_loss_mean = train_loss_sum / len(train_loader)

        model.eval()
        val_loss_sum = 0
        iou_list     = []
        dice_list    = []
        with torch.no_grad():
            for img, mask in val_loader:
                img, mask = img.to(device), mask.to(device)
                predict   = model(img)

                mask_one_hot = F.one_hot(mask, num_classes=NUM_CLASSES) \
                    .permute(0, 3, 1, 2).float()
                v_l1   = ce_loss(predict, mask)
                v_l2   = dice_loss(predict, mask_one_hot)
                v_loss = v_l1 + v_l2
                val_loss_sum += v_loss.item()

                preds_classes = predict.argmax(dim=1)
                iou_list.append(compute_iou_per_class(preds_classes.cpu(), mask.cpu(), NUM_CLASSES))
                dice_list.append(compute_dice_per_class(preds_classes.cpu(), mask.cpu(), NUM_CLASSES))

        val_loss = val_loss_sum / len(val_loader)
        val_miou = float(np.nanmean(np.stack(iou_list,  axis=0)))
        val_dice = float(np.nanmean(np.stack(dice_list, axis=0)))

        history['train_loss'].append(train_loss_mean)
        history['val_loss'].append(val_loss)
        history['val_miou'].append(val_miou)
        history['val_dice'].append(val_dice)

        print(f"Epoch {epoch + 1:03d}/{num_epochs} | "
              f"Train Loss: {train_loss_mean:.4f} | "
              f"Val Loss: {val_loss:.4f} | "
              f"Val mIoU: {val_miou:.4f} | "
              f"Val Dice: {val_dice:.4f} |")

    return history


# Graphics
def plot_training_curves(history, save_path="training_curves.png"):
    epochs = range(1, len(history['train_loss']) + 1)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))

    ax1.plot(epochs, history['train_loss'], marker='o', color='steelblue',
             linewidth=2, markersize=5, label='Train Loss')
    ax1.plot(epochs, history['val_loss'], marker='s', color='firebrick',
             linewidth=2, markersize=5, label='Val Loss')
    ax1.set_title("Loss per Epoch", fontsize=14, fontweight='bold')
    ax1.set_xlabel("Epoch")
    ax1.set_ylabel("Loss")
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    ax2.plot(epochs, history['val_miou'], marker='s', color='darkorange',
             linewidth=2, markersize=5, label='Val mIoU')
    ax2.plot(epochs, history['val_dice'], marker='^', color='forestgreen',
             linewidth=2, markersize=5, label='Val Dice')
    ax2.set_title("Validation Metrics per Epoch", fontsize=14, fontweight='bold')
    ax2.set_xlabel("Epoch")
    ax2.set_ylabel("Score")
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.show()
    print(f"Training curves saved → {save_path}")


# Visualize
def denormalize(tensor, mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225)):
    img = tensor.cpu().numpy().transpose(1, 2, 0)
    img = img * np.array(std) + np.array(mean)
    return (np.clip(img, 0, 1) * 255).astype(np.uint8)


def visualize_predictions(model, device, loader, num_images=6,
                           save_path="predictions.png", split_name="Validation"):
    model.eval()
    images, true_masks, pred_masks = [], [], []

    with torch.no_grad():
        for imgs, masks in loader:
            for i in range(imgs.size(0)):
                if len(images) >= num_images:
                    break
                logits    = model(imgs[i].unsqueeze(0).to(device))
                pred_mask = logits.argmax(dim=1).squeeze(0).cpu()
                images.append(imgs[i])
                true_masks.append(masks[i].cpu())
                pred_masks.append(pred_mask)
            if len(images) >= num_images:
                break

    n   = len(images)
    fig, axes = plt.subplots(n, 3, figsize=(12, 4 * n))
    cmap_kw = dict(cmap='tab10', vmin=0, vmax=NUM_CLASSES - 1)

    for col, title in enumerate(["Original Image", "Ground Truth Mask", "Predicted Mask"]):
        axes[0, col].set_title(title, fontsize=13, fontweight='bold', pad=8)

    for row in range(n):
        axes[row, 0].imshow(denormalize(images[row])); axes[row, 0].axis('off')
        axes[row, 1].imshow(true_masks[row].numpy(), **cmap_kw); axes[row, 1].axis('off')
        axes[row, 2].imshow(pred_masks[row].numpy(), **cmap_kw); axes[row, 2].axis('off')

    plt.suptitle(f"{split_name} Set — Segmentation Results", fontsize=15,
                 fontweight='bold', y=1.01)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.show()
    print(f"Prediction grid saved → {save_path}")


# Evaluate — универсальная функция для val и test лоадеров
def evaluate_on_loader(model, device, loader, split_name="Validation"):
    model.eval()
    iou_list, dice_list = [], []

    with torch.no_grad():
        for imgs, masks in loader:
            imgs  = imgs.to(device)
            preds = model(imgs).argmax(dim=1).cpu()
            iou_list.append(compute_iou_per_class(preds, masks.cpu(), NUM_CLASSES))
            dice_list.append(compute_dice_per_class(preds, masks.cpu(), NUM_CLASSES))

    iou_per_class = np.nanmean(np.stack(iou_list,  axis=0), axis=0)  # [NUM_CLASSES]
    dice_per_class= np.nanmean(np.stack(dice_list, axis=0), axis=0)
    mean_iou      = float(np.nanmean(iou_per_class))
    mean_dice     = float(np.nanmean(dice_per_class))

    print(f"\n{'='*45}")
    print(f"  {split_name} evaluation")
    print(f"  Mean IoU   : {mean_iou:.4f}")
    print(f"  Mean Dice  : {mean_dice:.4f}")
    print(f"{'='*45}\n")

    return mean_iou, mean_dice, iou_per_class


# Comparison table — теперь с колонками val и test, и 10 классами датасета
def print_comparison_table(results):
    has_test = any('miou_test' in r for r in results)

    header = (f"{'Модель':<30} {'Параметры (всего)':>18} "
              f"{'Параметры (обуч.)':>18} {'Эпох':>6} {'mIoU (val)':>11}")
    if has_test:
        header += f" {'mIoU (test)':>11}"
    sep_len = 87 + (12 if has_test else 0)

    print("\n" + "=" * sep_len)
    print(header)
    print("-" * sep_len)
    for r in results:
        line = (f"{r['name']:<30} {r['params_total']:>18,} "
                f"{r['params_train']:>18,} {r['epochs']:>6} {r['miou_val']:>11.4f}")
        if has_test:
            line += f" {r.get('miou_test', float('nan')):>11.4f}"
        print(line)
    print("=" * sep_len)

    # Per-class IoU table
    print(f"\n{'Класс':<25}", end="")
    for r in results:
        print(f"  {'IoU val':>10}  {'IoU test':>10}" if has_test
              else f"  {'IoU val':>10}", end="")
        # one header per model
        break

    print(f"\n{'Класс':<25}", end="")
    for r in results:
        col_w = 22 if has_test else 12
        print(f"  {r['name'][:col_w - 2]:<{col_w}}", end="")
    print()
    print("-" * (25 + (24 if has_test else 14) * len(results)))

    for cls_idx, cls_name in enumerate(CLASS_NAMES):
        print(f"{cls_name:<25}", end="")
        for r in results:
            val_iou  = r['iou_per_class_val'][cls_idx]
            val_str  = f"{val_iou:.4f}" if not np.isnan(val_iou) else "  —   "
            if has_test:
                test_iou = r.get('iou_per_class_test', [float('nan')] * NUM_CLASSES)[cls_idx]
                test_str = f"{test_iou:.4f}" if not np.isnan(test_iou) else "  —   "
                print(f"  {val_str:>10}  {test_str:>10}", end="")
            else:
                print(f"  {val_str:>10}", end="")
        print()
    print()


# Error analysis
def visualize_error_analysis(model, device, loader, num_images=6,
                              save_path="error_analysis.png", split_name="Validation"):
    model.eval()
    samples = []

    with torch.no_grad():
        for imgs, masks in loader:
            for i in range(imgs.size(0)):
                logits    = model(imgs[i].unsqueeze(0).to(device))
                pred_mask = logits.argmax(dim=1).squeeze(0).cpu()
                true_mask = masks[i].cpu()

                iou     = compute_iou_per_class(pred_mask.unsqueeze(0),
                                                true_mask.unsqueeze(0), NUM_CLASSES)
                img_miou = float(np.nanmean(iou))
                samples.append((imgs[i], true_mask, pred_mask, img_miou))

    samples.sort(key=lambda x: x[3])
    worst = samples[:num_images]

    fig, axes = plt.subplots(num_images, 4, figsize=(16, 4 * num_images))
    col_titles = ["Original Image", "Ground Truth Mask",
                  "Predicted Mask",  "Error Map"]
    for col, title in enumerate(col_titles):
        axes[0, col].set_title(title, fontsize=12, fontweight='bold', pad=8)

    cmap_kw = dict(cmap='tab10', vmin=0, vmax=NUM_CLASSES - 1)

    for row, (img_t, true_mask, pred_mask, miou) in enumerate(worst):
        error_map = (pred_mask != true_mask).float().numpy()

        axes[row, 0].imshow(denormalize(img_t))
        axes[row, 0].set_ylabel(f"mIoU={miou:.3f}", fontsize=10)
        axes[row, 0].axis('off')

        axes[row, 1].imshow(true_mask.numpy(), **cmap_kw)
        axes[row, 1].axis('off')

        axes[row, 2].imshow(pred_mask.numpy(), **cmap_kw)
        axes[row, 2].axis('off')

        axes[row, 3].imshow(error_map, cmap='Reds', vmin=0, vmax=1)
        axes[row, 3].axis('off')

    plt.suptitle(f"Error Analysis — {split_name} Set — Worst Predictions by mIoU",
                 fontsize=15, fontweight='bold', y=1.01)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.show()
    print(f"Error analysis saved → {save_path}")


# Test — теперь маски есть, поэтому считаем метрики и сохраняем предсказания
def evaluate_and_save_test_predictions(model, device, test_loader,
                                       output_dir="./test_predictions"):
    """
    Запускает инференс на тестовой выборке:
      - вычисляет mIoU и Dice (маски теперь доступны)
      - сохраняет предсказанные маски как PNG в output_dir
    """
    os.makedirs(output_dir, exist_ok=True)
    model.eval()

    iou_list, dice_list = [], []
    img_counter = 0

    print(f"Running test inference → saving masks to '{output_dir}' ...")
    with torch.no_grad():
        for imgs, masks in test_loader:
            imgs  = imgs.to(device)
            preds = model(imgs).argmax(dim=1).cpu()

            iou_list.append(compute_iou_per_class(preds, masks.cpu(), NUM_CLASSES))
            dice_list.append(compute_dice_per_class(preds, masks.cpu(), NUM_CLASSES))

            for i in range(preds.size(0)):
                pred_mask = preds[i].numpy().astype(np.uint8)
                Image.fromarray(pred_mask).save(
                    os.path.join(output_dir, f"pred_{img_counter:04d}.png")
                )
                img_counter += 1

    iou_per_class = np.nanmean(np.stack(iou_list,  axis=0), axis=0)
    mean_iou      = float(np.nanmean(iou_per_class))
    mean_dice     = float(np.nanmean(np.stack(dice_list, axis=0)))

    print(f"\n{'='*45}")
    print(f"  Test evaluation")
    print(f"  Mean IoU   : {mean_iou:.4f}")
    print(f"  Mean Dice  : {mean_dice:.4f}")
    print(f"{'='*45}\n")
    print(f"Test inference complete. {img_counter} masks saved → '{output_dir}'")

    return mean_iou, mean_dice, iou_per_class


if __name__ == '__main__':

    train_dataset = create_segmentation_dataset(
        IMAGE_ROOT_TRAIN, MASK_ROOT_TRAIN, transform=transform_train
    )
    val_dataset = create_segmentation_dataset(
        IMAGE_ROOT_VAL, MASK_ROOT_VAL, transform=transform_val
    )
    # Тестовая выборка теперь тоже имеет маски — используем тот же класс
    test_dataset = create_segmentation_dataset(
        IMAGE_ROOT_TEST, MASK_ROOT_TEST, transform=transform_val
    )

    train_loader, val_loader, test_loader = get_loaders(
        train_dataset, val_dataset, test_dataset,
        batch_size=BATCH_SIZE, num_workers=NUM_WORKERS
    )

    NUM_EPOCHS = 50

    # --- UNet с нуля ---
    model_scratch = UNet(in_channels=3, out_channels=NUM_CLASSES)
    if n_gpus > 1:
        print(f"Запуск DataParallel на {n_gpus} GPU")
        model_scratch = nn.DataParallel(model_scratch)
    model_scratch = model_scratch.to(device)

    history_scratch = train(
        model_scratch, device, train_loader, val_loader,
        num_epochs=NUM_EPOCHS
    )
    save_weights(model_scratch, path="unet_scratch.pth")
    # load_weights(model_scratch, path="unet_scratch.pth")

    plot_training_curves(history_scratch, save_path="curves_scratch.png")
    visualize_predictions(model_scratch, device, val_loader,
                          num_images=6, save_path="predictions_scratch_val.png",
                          split_name="Validation")

    miou_s_val,  dice_s_val,  iou_cls_s_val  = evaluate_on_loader(
        model_scratch, device, val_loader,  split_name="Validation"
    )
    miou_s_test, dice_s_test, iou_cls_s_test = evaluate_on_loader(
        model_scratch, device, test_loader, split_name="Test"
    )
    total_s, train_s = count_parameters(model_scratch)

    # --- UNet + ResNet18 encoder ---
    model_pretrained = UNetResNet18(out_channels=NUM_CLASSES, pretrained=True)
    if n_gpus > 1:
        print(f"Запуск DataParallel на {n_gpus} GPU")
        model_pretrained = nn.DataParallel(model_pretrained)
    model_pretrained = model_pretrained.to(device)

    model_internal = (model_pretrained.module
                      if isinstance(model_pretrained, nn.DataParallel)
                      else model_pretrained)

    enc_params, dec_params = model_internal.get_param_groups()
    optimizer_pretrained = optim.AdamW([
        {'params': enc_params, 'lr': 1e-4},
        {'params': dec_params, 'lr': 1e-3},
    ])

    history_pretrained = train(
        model_pretrained, device, train_loader, val_loader,
        num_epochs=NUM_EPOCHS,
        optimizer=optimizer_pretrained
    )
    save_weights(model_pretrained, path="unet_resnet18.pth")
    # load_weights(model_pretrained, path="unet_resnet18.pth")

    plot_training_curves(history_pretrained, save_path="curves_pretrained.png")
    visualize_predictions(model_pretrained, device, val_loader,
                          num_images=6, save_path="predictions_pretrained_val.png",
                          split_name="Validation")

    miou_p_val,  dice_p_val,  iou_cls_p_val  = evaluate_on_loader(
        model_pretrained, device, val_loader,  split_name="Validation"
    )
    miou_p_test, dice_p_test, iou_cls_p_test = evaluate_on_loader(
        model_pretrained, device, test_loader, split_name="Test"
    )
    total_p, train_p = count_parameters(model_pretrained)

    # Таблица сравнения с val и test метриками
    print_comparison_table([
        {
            'name':              'UNet с нуля',
            'params_total':      total_s,
            'params_train':      train_s,
            'epochs':            NUM_EPOCHS,
            'miou_val':          miou_s_val,
            'miou_test':         miou_s_test,
            'iou_per_class_val': iou_cls_s_val,
            'iou_per_class_test':iou_cls_s_test,
        },
        {
            'name':              'UNet + ResNet18 encoder',
            'params_total':      total_p,
            'params_train':      train_p,
            'epochs':            NUM_EPOCHS,
            'miou_val':          miou_p_val,
            'miou_test':         miou_p_test,
            'iou_per_class_val': iou_cls_p_val,
            'iou_per_class_test':iou_cls_p_test,
        },
    ])

    # Error analysis на val и test
    visualize_error_analysis(model_scratch, device, val_loader,
                             num_images=6, save_path="errors_scratch_val.png",
                             split_name="Validation")
    visualize_error_analysis(model_scratch, device, test_loader,
                             num_images=6, save_path="errors_scratch_test.png",
                             split_name="Test")

    visualize_error_analysis(model_pretrained, device, val_loader,
                             num_images=6, save_path="errors_pretrained_val.png",
                             split_name="Validation")
    visualize_error_analysis(model_pretrained, device, test_loader,
                             num_images=6, save_path="errors_pretrained_test.png",
                             split_name="Test")

    # Сохранение предсказаний на тесте (лучшая модель — pretrained)
    evaluate_and_save_test_predictions(
        model_pretrained, device, test_loader,
        output_dir="./test_predictions"
    )