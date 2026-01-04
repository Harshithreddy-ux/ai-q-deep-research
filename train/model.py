import torch
import torch.nn as nn


class TinyTransformerLM(nn.Module):
    def __init__(self, vocab_size=1000, d_model=128, nhead=4, num_layers=2, dim_feedforward=256, dropout=0.1, max_len=512):
        super().__init__()
        self.token_emb = nn.Embedding(vocab_size, d_model, padding_idx=0)
        self.pos_emb = nn.Embedding(max_len, d_model)
        encoder_layer = nn.TransformerEncoderLayer(d_model=d_model, nhead=nhead, dim_feedforward=dim_feedforward, dropout=dropout)
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        self.ln = nn.LayerNorm(d_model)
        self.head = nn.Linear(d_model, vocab_size)

    def forward(self, x):
        # x: (batch, seq_len)
        b, s = x.shape
        pos = torch.arange(s, device=x.device).unsqueeze(0).expand(b, s)
        x = self.token_emb(x) + self.pos_emb(pos)
        # transformer expects (seq_len, batch, d_model)
        x = x.transpose(0, 1)
        x = self.transformer(x)  # (seq_len, batch, d_model)
        x = x.transpose(0, 1)  # (batch, seq_len, d_model)
        x = self.ln(x)
        logits = self.head(x)
        return logits
