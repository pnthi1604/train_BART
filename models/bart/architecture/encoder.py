import torch
import torch.nn as nn
from .encoder_layer import BartEncoderLayer
from .config import BartConfig
from .utils import (
    create_encoder_atn_mask,
)
from .utils.init_weights import (
    _init_weights,
)

class BartEncoder(nn.Module):
    def __init__(
        self,
        config: BartConfig,
        custom_encoder_layer: nn.Module=None,
    ):
        super().__init__()
        
        self.dropout = nn.Dropout(config.dropout)
        self.layerdrop = config.encoder_layerdrop
        if custom_encoder_layer is None:
            self.layers = nn.ModuleList([
                BartEncoderLayer(config) for _ in range(config.encoder_layers)
            ])
        else:
            self.layers = nn.ModuleList([
                custom_encoder_layer(config) for _ in range(config.encoder_layers)
            ])
        self.layernorm_embedding = nn.LayerNorm(config.d_model)

        self.apply(lambda module: _init_weights(
            module=module,
            std=config.init_std,
        ))

    def forward(
        self,
        inputs_embeds: torch.Tensor,
        attention_mask: torch.Tensor,
        head_mask: torch.Tensor = None,
    ):
        hidden_states = inputs_embeds
        hidden_states = self.layernorm_embedding(hidden_states)
        hidden_states = self.dropout(hidden_states)

        if attention_mask is not None:
            attention_mask = create_encoder_atn_mask(
                attention_mask=attention_mask,
            )

        for idx, encoder_layer in enumerate(self.layers):
            if self.training:
                dropout_probability = torch.rand([])
                if dropout_probability < self.layerdrop:
                    continue
            layer_outputs = encoder_layer(
                hidden_states=hidden_states,
                attention_mask=attention_mask,
                layer_head_mask=(head_mask[idx] if head_mask is not None else None),
            )
            hidden_states = layer_outputs

        return hidden_states
    
__all__ = ["BartEncoder"]