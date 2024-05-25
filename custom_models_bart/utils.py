import torch

def freeze_model(model, freeze_start_with_names=[]):
    for module in model.modules():
        for name, param in module.named_parameters():
            for freeze_name in freeze_start_with_names:
                if name.startswith(freeze_name, 0):
                    param.requires_grad = False
    return model

def un_freeze_model(model, un_freeze_start_with_names=[]):
    for module in model.modules():
        for name, param in module.named_parameters():
            for un_freeze_name in un_freeze_start_with_names:
                if name.startswith(un_freeze_name, 0):
                    param.requires_grad = True
    return model

def first_fine_tune_bart_with_random_encoder(config, model):
    model = freeze_model(
        model=model,
        freeze_start_with_names=[
            "bart_model",
        ]
    )
    
    model = un_freeze_model(
        model=model,
        un_freeze_start_with_names=[
            "bart_model.encoder.layers.0.self_attn.",
            "bart_model.encoder.embed_positions.weight",
        ]
    )

    return model

def second_fine_tune_bart_with_random_encoder(config, model):
    return model

# load model state dict
def load_model(checkpoint, model):
    if torch.cuda.is_available():
        state = torch.load(checkpoint)
    else:
        state = torch.load(checkpoint, map_location=torch.device('cpu'))
    model.load_state_dict(state["model_state_dict"])
    return model

__all__ = ["first_fine_tune_bart_with_random_encoder", "second_fine_tune_bart_with_random_encoder", "load_model", "freeze_model", "un_freeze_model"]