from transformers import BartModel, BartConfig
import torch.nn as nn
from .utils import load_model

class CustomBartModelWithEmbedding(nn.Module):
    def __init__(
        self,
        config: BartConfig,
        tokenizer_src,
        tokenizer_tgt,
        checkpoint=None
    ):
        super().__init__()
        self.config = config
        
        # vocab size
        self.src_vocab_size = tokenizer_src.get_vocab_size()
        self.tgt_vocab_size = tokenizer_tgt.get_vocab_size()
        
        # Encoder Embedding
        self.inputs_embeds = nn.Embedding(
            num_embeddings=self.src_vocab_size,
            embedding_dim=self.config.d_model
        )
        
        # Decoder Embedding
        self.decoder_inputs_embeds = nn.Embedding(
            num_embeddings=self.tgt_vocab_size,
            embedding_dim=self.config.d_model
        )

        # Initialize weights embeddings
        self.inputs_embeds.apply(self.initialize_weights)
        self.decoder_inputs_embeds.apply(self.initialize_weights)
        
        # Bart model
        self.bart_model = BartModel(config)
        if checkpoint:
            self.bart_model = load_model(
                model=self.bart_model,
                checkpoint=checkpoint
            )
            
        # Predict
        self.out = nn.Linear(self.config.d_model, tokenizer_tgt.get_vocab_size())
        
    def forward(
        self,
        input_ids,
        attention_mask,
        decoder_input_ids,
        decoder_attention_mask,
    ):
        inputs_embeds = self.inputs_embeds(input_ids)
        decoder_inputs_embeds = self.decoder_inputs_embeds(decoder_input_ids)
        outputs = self.bart_model(
            inputs_embeds=inputs_embeds,
            attention_mask=attention_mask,
            decoder_inputs_embeds=decoder_inputs_embeds,
            decoder_attention_mask=decoder_attention_mask,
        )
        last_hidden_state = outputs.last_hidden_state
        logits = self.out(last_hidden_state)
        return logits
    
    def initialize_weights(self, layer):
        if isinstance(layer, nn.Embedding):
            nn.init.normal_(layer.weight, mean=0, std=self.config.init_std)
    
    def get_encoder_out(
        self,
        input_ids,
        attention_mask
    ):
        inputs_embeds = self.inputs_embeds(input_ids)
        return self.bart_model.encoder(
            inputs_embeds=inputs_embeds,
            attention_mask=attention_mask,
        )
    
    def get_decoder_out(
        self,
        input_ids,
        attention_mask,
        encoder_hidden_states,
        encoder_attention_mask
    ):
        inputs_embeds = self.decoder_inputs_embeds(input_ids)
        return self.bart_model.decoder(
            inputs_embeds=inputs_embeds,
            attention_mask=attention_mask,
            encoder_hidden_states=encoder_hidden_states,
            encoder_attention_mask=encoder_attention_mask
        )
    
__all__ = ["CustomBartModelWithEmbedding"]