"""
Multimodal fusion: combines the image embedding (Vision Transformer) and
the sensor embedding (Sensor Feature Network) using cross-attention, then
predicts a hazard category through a prediction head.

    IMAGE -> ViT -> visual embedding  \
                                        -> cross-attention fusion -> head -> hazard
    SENSOR -> Sensor Net -> sensor embedding /
"""
import torch
import torch.nn as nn

HAZARD_CATEGORIES = [
    "NORMAL",
    "AIR_POLLUTION",
    "FLOOD_RISK",
    "HEAVY_RAIN",
    "LOW_VISIBILITY",
    "SMOKE_FIRE_RISK",
    "EXTREME_ENVIRONMENTAL_CONDITION",
]

RISK_LEVELS = ["NORMAL", "LOW", "MODERATE", "HIGH", "CRITICAL"]


class CrossAttentionFusion(nn.Module):
    """Each modality attends to the other, producing a fused representation
    plus an interpretable image-vs-sensor importance split."""

    def __init__(self, embed_dim=256, n_heads=4):
        super().__init__()
        self.img_to_sensor_attn = nn.MultiheadAttention(embed_dim, n_heads, batch_first=True)
        self.sensor_to_img_attn = nn.MultiheadAttention(embed_dim, n_heads, batch_first=True)
        self.norm_img = nn.LayerNorm(embed_dim)
        self.norm_sensor = nn.LayerNorm(embed_dim)
        self.gate = nn.Sequential(nn.Linear(embed_dim * 2, 2), nn.Softmax(dim=-1))
        self.fuse = nn.Sequential(
            nn.Linear(embed_dim * 2, embed_dim),
            nn.ReLU(),
            nn.LayerNorm(embed_dim),
        )

    def forward(self, img_embed, sensor_embed):
        img_seq = img_embed.unsqueeze(1)
        sensor_seq = sensor_embed.unsqueeze(1)

        img_attended, _ = self.img_to_sensor_attn(img_seq, sensor_seq, sensor_seq)
        sensor_attended, _ = self.sensor_to_img_attn(sensor_seq, img_seq, img_seq)

        img_out = self.norm_img(img_embed + img_attended.squeeze(1))
        sensor_out = self.norm_sensor(sensor_embed + sensor_attended.squeeze(1))

        concat = torch.cat([img_out, sensor_out], dim=-1)
        importance = self.gate(concat)  # [B, 2] -> (image_weight, sensor_weight)
        fused = self.fuse(concat)
        return fused, importance


class HazardPredictionHead(nn.Module):
    def __init__(self, embed_dim=256, n_classes=len(HAZARD_CATEGORIES)):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(embed_dim, 128),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(128, n_classes),
        )

    def forward(self, fused):
        return self.net(fused)


class MultimodalHazardModel(nn.Module):
    """Full pipeline: Vision Transformer + Sensor Network + Cross-Attention
    Fusion + Hazard Prediction Head."""

    def __init__(self, vision_encoder, sensor_encoder, embed_dim=256):
        super().__init__()
        self.vision_encoder = vision_encoder
        self.sensor_encoder = sensor_encoder
        self.fusion = CrossAttentionFusion(embed_dim)
        self.head = HazardPredictionHead(embed_dim)

    def forward(self, image_tensor=None, sensor_tensor=None):
        batch = sensor_tensor.shape[0] if sensor_tensor is not None else image_tensor.shape[0]
        device = sensor_tensor.device if sensor_tensor is not None else image_tensor.device
        embed_dim = self.fusion.fuse[0].out_features

        img_embed = (self.vision_encoder(image_tensor) if image_tensor is not None
                     else torch.zeros(batch, embed_dim, device=device))
        sensor_embed = (self.sensor_encoder(sensor_tensor) if sensor_tensor is not None
                         else torch.zeros(batch, embed_dim, device=device))

        fused, importance = self.fusion(img_embed, sensor_embed)
        logits = self.head(fused)
        return logits, importance


def risk_level_for(hazard: str, confidence: float) -> str:
    if hazard == "NORMAL":
        return "NORMAL" if confidence > 0.6 else "LOW"
    if confidence >= 0.9:
        return "CRITICAL"
    if confidence >= 0.75:
        return "HIGH"
    if confidence >= 0.55:
        return "MODERATE"
    return "LOW"
