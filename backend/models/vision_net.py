"""
Vision branch: Vision Transformer (ViT) image encoder.

Tries to load a pretrained torchvision ViT-B/16. If weights cannot be
downloaded (no internet access, offline machine, etc.) this falls back to a
small from-scratch ViT-style patch-embedding transformer so the application
never crashes and always has a working image encoder — clearly documented
as DEMO MODE for the vision branch.
"""
import torch
import torch.nn as nn
import torchvision.transforms as T

IMG_SIZE = 224
EMBED_DIM = 256


class MiniViT(nn.Module):
    """A small, from-scratch Vision Transformer used as an offline fallback
    when pretrained ImageNet weights are not downloadable. Same overall
    design as a real ViT: patchify -> linear projection -> [CLS] token ->
    positional embeddings -> transformer encoder -> pooled embedding."""

    def __init__(self, img_size=IMG_SIZE, patch_size=16, in_ch=3,
                 embed_dim=EMBED_DIM, depth=4, n_heads=4):
        super().__init__()
        n_patches = (img_size // patch_size) ** 2
        self.patch_embed = nn.Conv2d(in_ch, embed_dim, kernel_size=patch_size, stride=patch_size)
        self.cls_token = nn.Parameter(torch.zeros(1, 1, embed_dim))
        self.pos_embed = nn.Parameter(torch.zeros(1, n_patches + 1, embed_dim))
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=embed_dim, nhead=n_heads, dim_feedforward=embed_dim * 4,
            dropout=0.1, batch_first=True,
        )
        self.encoder = nn.TransformerEncoder(encoder_layer, num_layers=depth)
        self.norm = nn.LayerNorm(embed_dim)
        nn.init.trunc_normal_(self.pos_embed, std=0.02)
        nn.init.trunc_normal_(self.cls_token, std=0.02)

    def forward(self, x, return_attention=False):
        b = x.shape[0]
        x = self.patch_embed(x).flatten(2).transpose(1, 2)  # [B, N, D]
        cls = self.cls_token.expand(b, -1, -1)
        x = torch.cat([cls, x], dim=1) + self.pos_embed
        x = self.encoder(x)
        x = self.norm(x)
        cls_out = x[:, 0]
        if return_attention:
            # Simple saliency proxy: per-patch embedding norm as an
            # attention-style explanation map (not a true attention rollout).
            patch_scores = x[:, 1:].norm(dim=-1)
            return cls_out, patch_scores
        return cls_out


class VisionEncoder(nn.Module):
    """Wraps a pretrained torchvision ViT-B/16 when available, else MiniViT.
    Always exposes a `embed_dim`-sized output embedding."""

    def __init__(self, embed_dim=EMBED_DIM, pretrained=True):
        super().__init__()
        self.mode = "demo"
        self.embed_dim = embed_dim
        self.backbone = None
        self.proj = None

        if pretrained:
            try:
                import torchvision.models as tvm
                weights = tvm.ViT_B_16_Weights.IMAGENET1K_V1
                vit = tvm.vit_b_16(weights=weights)
                vit.heads = nn.Identity()
                self.backbone = vit
                self.proj = nn.Linear(768, embed_dim)
                self.mode = "pretrained"
            except Exception:
                self.backbone = None

        if self.backbone is None:
            self.backbone = MiniViT(embed_dim=embed_dim)
            self.mode = "demo"

    def forward(self, x):
        if self.mode == "pretrained":
            feats = self.backbone(x)
            return self.proj(feats)
        return self.backbone(x)

    @staticmethod
    def preprocess():
        return T.Compose([
            T.Resize((IMG_SIZE, IMG_SIZE)),
            T.ToTensor(),
            T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])
