import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import transforms, models, datasets
from torch.utils.data import DataLoader
from torch.nn.utils import spectral_norm
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import mlflow
import mlflow.pytorch
from mlflow.models.signature import infer_signature
import tempfile
import os

# ──────────────────────────────────────────────────────────────────────────────
# Neural Style Transfer
# ──────────────────────────────────────────────────────────────────────────────

imagenet_mean = [0.485, 0.456, 0.406]
imagenet_std  = [0.229, 0.224, 0.225]

def load_image(image_path, size=256):
    img = Image.open(image_path).convert('RGB')
    transform = transforms.Compose([
        transforms.Resize((size, size)),
        transforms.ToTensor(),
        transforms.Normalize(imagenet_mean, imagenet_std),
    ])
    return transform(img).unsqueeze(0)

def denormalize(tensor):
    """Обратная нормализация ImageNet для отображения изображения."""
    mean = torch.tensor(imagenet_mean).view(3, 1, 1)
    std  = torch.tensor(imagenet_std).view(3, 1, 1)
    img  = tensor.clone().squeeze(0).cpu()
    img  = img * std + mean
    return img.clamp(0, 1).permute(1, 2, 0).numpy()

def get_features(image, model, layers):
    idx_to_name = {v: k for k, v in layers.items()}
    max_idx     = max(idx_to_name.keys())
    features    = {}
    x = image
    for i, layer in enumerate(model):
        x = layer(x)
        if i in idx_to_name:
            features[idx_to_name[i]] = x
        if i == max_idx:
            break
    return features

def content_loss(generated_features, content_features):
    return F.mse_loss(generated_features, content_features)

def gram_matrix(features):
    b, c, h, w = features.shape
    F_ = features.view(b, c, h * w)
    G  = torch.bmm(F_, F_.transpose(1, 2))
    return G / (c * h * w)

def style_loss(generated_features, style_features):
    G_gen   = gram_matrix(generated_features)
    G_style = gram_matrix(style_features)
    return F.mse_loss(G_gen, G_style)

def run_nst(
    content_path="content.jpg",
    style_path="style.jpg",
    image_size=256,
    num_steps=300,
    alpha=1,
    beta=1e5,
    lr=1.0,
    lbfgs_max_iter=20,
    experiment_name="NST",
):
    torch.manual_seed(42)
    torch.cuda.manual_seed_all(42)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark     = False

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Используется устройство: {device}")

    mlflow.set_experiment(experiment_name)

    with mlflow.start_run(run_name="nst_run"):
        mlflow.log_params({
            "image_size":     image_size,
            "num_steps":      num_steps,
            "alpha":          alpha,
            "beta":           beta,
            "lr":             lr,
            "lbfgs_max_iter": lbfgs_max_iter,
            "optimizer":      "LBFGS",
            "content_layer":  "conv4_2",
            "style_layers":   "conv1_1,conv2_1,conv3_1,conv4_1,conv5_1",
            "device":         str(device),
        })

        vgg = models.vgg19(weights=models.VGG19_Weights.DEFAULT).features.to(device)
        for param in vgg.parameters():
            param.requires_grad = False
        vgg.eval()

        content_img = load_image(content_path, size=image_size).to(device)
        style_img   = load_image(style_path,   size=image_size).to(device)

        style_layers = {
            'conv1_1': 0,
            'conv2_1': 5,
            'conv3_1': 10,
            'conv4_1': 19,
            'conv5_1': 28,
        }
        content_layers = {'conv4_2': 21}
        all_layers = {**style_layers, **content_layers}

        style_weights = {
            'conv1_1': 1.0,
            'conv2_1': 0.8,
            'conv3_1': 0.5,
            'conv4_1': 0.3,
            'conv5_1': 0.1,
        }

        with torch.no_grad():
            content_features = get_features(content_img, vgg, all_layers)
            style_features   = get_features(style_img,   vgg, all_layers)

        generated = content_img.clone().requires_grad_(True)
        optimizer = torch.optim.LBFGS([generated], lr=lr, max_iter=lbfgs_max_iter)

        mean_t = torch.tensor(imagenet_mean, device=device).view(1, 3, 1, 1)
        std_t  = torch.tensor(imagenet_std,  device=device).view(1, 3, 1, 1)

        snapshots = []

        def closure():
            optimizer.zero_grad()
            gen_features = get_features(generated, vgg, all_layers)

            c_loss = content_loss(gen_features['conv4_2'], content_features['conv4_2'])

            s_loss = 0
            for layer in style_layers:
                s_loss += style_weights[layer] * style_loss(
                    gen_features[layer], style_features[layer]
                )

            total = alpha * c_loss + beta * s_loss
            total.backward()
            closure.last_losses = (total, c_loss, s_loss)
            return total

        for step in range(num_steps):
            optimizer.step(closure)

            with torch.no_grad():
                generated.data = (generated.data * std_t + mean_t).clamp(0, 1)
                generated.data = (generated.data - mean_t) / std_t

            if step % 50 == 0:
                total_loss, c_loss, s_loss = closure.last_losses
                print(f"Step {step}: total={total_loss.item():.4f}, "
                      f"content={c_loss.item():.4f}, style={s_loss.item():.4f}")

                mlflow.log_metrics({
                    "total_loss":   total_loss.item(),
                    "content_loss": c_loss.item(),
                    "style_loss":   s_loss.item(),
                }, step=step)

                snapshots.append((step, denormalize(generated.detach())))

        snapshots.append((num_steps, denormalize(generated.detach())))

        # Визуализация прогресса
        fig, axes = plt.subplots(1, len(snapshots), figsize=(4 * len(snapshots), 4))
        for ax, (step, img) in zip(axes, snapshots):
            ax.imshow(img)
            ax.set_title(f"Шаг {step}")
            ax.axis('off')
        plt.tight_layout()
        progress_path = "nst_progress.png"
        plt.savefig(progress_path, dpi=150)
        plt.show()
        mlflow.log_artifact(progress_path)

        # Сохранение финального изображения
        final_img_np = (snapshots[-1][1] * 255).astype(np.uint8)
        final_pil = Image.fromarray(final_img_np)
        final_path = "nst_result.png"
        final_pil.save(final_path)
        mlflow.log_artifact(final_path)

        # Финальные метрики
        total_loss, c_loss, s_loss = closure.last_losses
        mlflow.log_metrics({
            "final_total_loss":   total_loss.item(),
            "final_content_loss": c_loss.item(),
            "final_style_loss":   s_loss.item(),
        })

        print(f"NST run завершён. Результат сохранён в {final_path}")


# ──────────────────────────────────────────────────────────────────────────────
# DCGAN
# ──────────────────────────────────────────────────────────────────────────────

class Generator(nn.Module):
    def __init__(self, latent_dim=100, img_channels=3):
        super().__init__()
        self.net = nn.Sequential(
            nn.ConvTranspose2d(latent_dim, 512, 4, 1, 0, bias=False),
            nn.BatchNorm2d(512),
            nn.ReLU(True),
            nn.ConvTranspose2d(512, 256, 4, 2, 1, bias=False),
            nn.BatchNorm2d(256),
            nn.ReLU(True),
            nn.ConvTranspose2d(256, 128, 4, 2, 1, bias=False),
            nn.BatchNorm2d(128),
            nn.ReLU(True),
            nn.ConvTranspose2d(128, 64, 4, 2, 1, bias=False),
            nn.BatchNorm2d(64),
            nn.ReLU(True),
            nn.ConvTranspose2d(64, img_channels, 4, 2, 1, bias=False),
            nn.Tanh(),
        )

    def forward(self, z):
        return self.net(z)


class Discriminator(nn.Module):
    def __init__(self, img_channels=3):
        super().__init__()
        self.net = nn.Sequential(
            spectral_norm(nn.Conv2d(img_channels, 64, 4, 2, 1, bias=False)),
            nn.LeakyReLU(0.2, inplace=True),
            spectral_norm(nn.Conv2d(64, 128, 4, 2, 1, bias=False)),
            nn.BatchNorm2d(128),
            nn.LeakyReLU(0.2, inplace=True),
            spectral_norm(nn.Conv2d(128, 256, 4, 2, 1, bias=False)),
            nn.BatchNorm2d(256),
            nn.LeakyReLU(0.2, inplace=True),
            spectral_norm(nn.Conv2d(256, 512, 4, 2, 1, bias=False)),
            nn.BatchNorm2d(512),
            nn.LeakyReLU(0.2, inplace=True),
            spectral_norm(nn.Conv2d(512, 1, 4, 1, 0, bias=False)),
        )

    def forward(self, img):
        return self.net(img).view(-1)


def weights_init(m):
    if isinstance(m, (nn.Conv2d, nn.ConvTranspose2d)):
        nn.init.normal_(m.weight, 0.0, 0.02)
    elif isinstance(m, nn.BatchNorm2d):
        nn.init.normal_(m.weight, 1.0, 0.02)
        nn.init.zeros_(m.bias)


def denorm_gan(tensor):
    """Обратная нормализация из [-1, 1] в [0, 1]."""
    return (tensor * 0.5 + 0.5).clamp(0, 1)


def show_grid(images, title, nrow=4, save=True):
    images = denorm_gan(images).cpu()
    fig, axes = plt.subplots(nrow, nrow, figsize=(8, 8))
    for i, ax in enumerate(axes.flat):
        if i < images.size(0):
            ax.imshow(images[i].permute(1, 2, 0).numpy())
        ax.axis('off')
    fig.suptitle(title)
    plt.tight_layout()
    path = f"{title.replace(' ', '_')}.png"
    if save:
        plt.savefig(path, dpi=150)
    plt.show()
    return path


def compute_fid(generator, dataloader, latent_dim, device, num_samples=10_000):
    try:
        from torchmetrics.image.fid import FrechetInceptionDistance

        fid = FrechetInceptionDistance(feature=2048).to(device)

        def prepare_for_fid(images):
            images = denorm_gan(images)
            images = F.interpolate(images, size=(75, 75), mode='bilinear', align_corners=False)
            return (images * 255).byte()

        samples_seen = 0
        for real_images, _ in dataloader:
            real_images = real_images.to(device)
            fid.update(prepare_for_fid(real_images), real=True)
            samples_seen += real_images.size(0)
            if samples_seen >= num_samples:
                break

        generator.eval()
        samples_seen = 0
        with torch.no_grad():
            while samples_seen < num_samples:
                z = torch.randn(128, latent_dim, 1, 1, device=device)
                fake_images = generator(z)
                fid.update(prepare_for_fid(fake_images), real=False)
                samples_seen += fake_images.size(0)

        return fid.compute().item()

    except ImportError:
        print("torchmetrics не установлен, FID пропущен.")
        return None


def run_dcgan(
    num_epochs=50,
    latent_dim=100,
    batch_size=128,
    lr_g=2e-4,
    lr_d=2e-4,
    beta1=0.5,
    label_smooth=0.9,
    fid_samples=10_000,
    experiment_name="DCGAN",
):
    torch.manual_seed(42)
    torch.cuda.manual_seed_all(42)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark     = False

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Используется устройство: {device}")

    mlflow.set_experiment(experiment_name)

    with mlflow.start_run(run_name="dcgan_run"):
        mlflow.log_params({
            "num_epochs":   num_epochs,
            "latent_dim":   latent_dim,
            "batch_size":   batch_size,
            "lr_g":         lr_g,
            "lr_d":         lr_d,
            "beta1":        beta1,
            "label_smooth": label_smooth,
            "dataset":      "CIFAR10",
            "image_size":   64,
            "device":       str(device),
        })

        # Теги для удобной фильтрации в MLflow UI
        mlflow.set_tags({
            "model_type":  "GAN",
            "architecture": "DCGAN",
        })

        transform = transforms.Compose([
            transforms.Resize(64),
            transforms.CenterCrop(64),
            transforms.ToTensor(),
            transforms.Normalize([0.5, 0.5, 0.5], [0.5, 0.5, 0.5]),
        ])

        dataset    = datasets.CIFAR10(root='data', train=True, download=True, transform=transform)
        dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True,
                                num_workers=2, pin_memory=True)

        generator     = Generator(latent_dim=latent_dim).to(device)
        discriminator = Discriminator().to(device)
        generator.apply(weights_init)
        discriminator.apply(weights_init)

        criterion = nn.BCEWithLogitsLoss()

        opt_G = torch.optim.Adam(generator.parameters(),     lr=lr_g, betas=(beta1, 0.999))
        opt_D = torch.optim.Adam(discriminator.parameters(), lr=lr_d, betas=(beta1, 0.999))

        fixed_noise = torch.randn(16, latent_dim, 1, 1, device=device)

        history = {'loss_D': [], 'loss_G': [], 'D_x': [], 'D_G_z': []}

        for epoch in range(num_epochs):
            epoch_loss_D = 0.0
            epoch_loss_G = 0.0
            epoch_D_x    = 0.0
            epoch_D_G_z  = 0.0

            for real_images, _ in dataloader:
                batch_size_  = real_images.size(0)
                real_images  = real_images.to(device)

                real_labels = torch.full((batch_size_,), label_smooth, device=device)
                fake_labels = torch.zeros(batch_size_, device=device)

                z           = torch.randn(batch_size_, latent_dim, 1, 1, device=device)
                fake_images = generator(z)

                d_real    = discriminator(real_images)
                d_fake    = discriminator(fake_images.detach())
                loss_real = criterion(d_real, real_labels)
                loss_fake = criterion(d_fake, fake_labels)
                loss_D    = loss_real + loss_fake

                opt_D.zero_grad()
                loss_D.backward()
                opt_D.step()

                z           = torch.randn(batch_size_, latent_dim, 1, 1, device=device)
                fake_images = generator(z)
                d_fake_for_G = discriminator(fake_images)
                loss_G       = criterion(d_fake_for_G, torch.ones(batch_size_, device=device))

                opt_G.zero_grad()
                loss_G.backward()
                opt_G.step()

                epoch_loss_D += loss_D.item()
                epoch_loss_G += loss_G.item()
                epoch_D_x    += torch.sigmoid(d_real).mean().item()
                epoch_D_G_z  += torch.sigmoid(d_fake_for_G).mean().item()

            n = len(dataloader)
            history['loss_D'].append(epoch_loss_D / n)
            history['loss_G'].append(epoch_loss_G / n)
            history['D_x'].append(epoch_D_x / n)
            history['D_G_z'].append(epoch_D_G_z / n)

            print(f"Epoch [{epoch+1}/{num_epochs}] "
                  f"loss_D={history['loss_D'][-1]:.4f}  "
                  f"loss_G={history['loss_G'][-1]:.4f}  "
                  f"D(x)={history['D_x'][-1]:.3f}  "
                  f"D(G(z))={history['D_G_z'][-1]:.3f}")

            mlflow.log_metrics({
                "loss_D": history['loss_D'][-1],
                "loss_G": history['loss_G'][-1],
                "D_x":    history['D_x'][-1],
                "D_G_z":  history['D_G_z'][-1],
            }, step=epoch + 1)

            if (epoch + 1) % 5 == 0:
                with torch.no_grad():
                    fake = generator(fixed_noise)
                grid_path = show_grid(fake, f"Эпоха {epoch+1}")
                mlflow.log_artifact(grid_path)

        # Графики обучения
        epochs_range = range(1, num_epochs + 1)

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))

        ax1.plot(epochs_range, history['loss_D'], label='loss_D')
        ax1.plot(epochs_range, history['loss_G'], label='loss_G')
        ax1.set_xlabel('Эпоха')
        ax1.set_ylabel('Loss')
        ax1.set_title('Потери генератора и дискриминатора')
        ax1.legend()

        ax2.plot(epochs_range, history['D_x'],   label='D(x)')
        ax2.plot(epochs_range, history['D_G_z'], label='D(G(z))')
        ax2.set_xlabel('Эпоха')
        ax2.set_ylabel('Вероятность')
        ax2.set_title('Оценки дискриминатора')
        ax2.legend()

        plt.tight_layout()
        training_plot_path = "dcgan_training.png"
        plt.savefig(training_plot_path, dpi=150)
        plt.show()
        mlflow.log_artifact(training_plot_path)

        # Финальная сетка 4×4
        generator.eval()
        with torch.no_grad():
            final_fake = generator(torch.randn(16, latent_dim, 1, 1, device=device))
        final_grid_path = show_grid(final_fake, "Финальные сгенерированные изображения")
        mlflow.log_artifact(final_grid_path)

        # FID
        fid_score = compute_fid(generator, dataloader, latent_dim, device, num_samples=fid_samples)
        if fid_score is not None:
            print(f"FID: {fid_score:.2f}  (n={fid_samples})")
            mlflow.log_metric("fid", fid_score)

        # Сохранение моделей как артефактов MLflow
        dummy_z   = torch.randn(1, latent_dim, 1, 1, device=device)
        with torch.no_grad():
            dummy_out = generator(dummy_z)
        signature = infer_signature(
            dummy_z.cpu().numpy(),
            dummy_out.cpu().numpy(),
        )
        mlflow.pytorch.log_model(
            generator,
            artifact_path="generator",
            signature=signature,
        )
        mlflow.pytorch.log_model(
            discriminator,
            artifact_path="discriminator",
        )

        # Интерполяция в латентном пространстве
        generator.eval()
        z1 = torch.randn(1, latent_dim, 1, 1, device=device)
        z2 = torch.randn(1, latent_dim, 1, 1, device=device)
        alphas = torch.linspace(0, 1, steps=10)
        with torch.no_grad():
            images = [generator((1 - a) * z1 + a * z2) for a in alphas]

        fig, axes = plt.subplots(1, 10, figsize=(20, 2))
        for ax, img in zip(axes, images):
            ax.imshow(denorm_gan(img).squeeze(0).permute(1, 2, 0).cpu().numpy())
            ax.axis('off')
        plt.suptitle("Интерполяция в латентном пространстве")
        plt.tight_layout()
        interp_path = "dcgan_interpolation.png"
        plt.savefig(interp_path, dpi=150)
        plt.show()
        mlflow.log_artifact(interp_path)

        print(f"DCGAN run завершён. MLflow UI: mlflow ui")


if __name__ == '__main__':
    run_nst()
    run_dcgan()
