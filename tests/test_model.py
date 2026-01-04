import torch
from train.model import TinyTransformerLM


def test_model_forward():
    model = TinyTransformerLM(vocab_size=128, d_model=64, num_layers=1, max_len=32)
    x = torch.randint(1, 128, (2, 32), dtype=torch.long)
    logits = model(x)
    assert logits.shape == (2, 32, 128)
