import argparse
import os
import sys
import torch
from torch.utils.data import DataLoader
# Ensure local imports work when running script directly
sys.path.append(os.path.dirname(__file__))
from dataset import SyntheticSeqDataset
from model import TinyTransformerLM


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--batch-size", type=int, default=8)
    p.add_argument("--seq-len", type=int, default=32)
    p.add_argument("--vocab-size", type=int, default=1000)
    p.add_argument("--lr", type=float, default=1e-3)
    p.add_argument("--epochs", type=int, default=1)
    p.add_argument("--dry-run", action="store_true", help="Run one batch and exit")
    p.add_argument("--save-dir", type=str, default="checkpoints")
    p.add_argument("--log-dir", type=str, default="runs")
    p.add_argument("--checkpoint-interval", type=int, default=1, help="Save checkpoint every N epochs")
    return p.parse_args()


def train(cfg):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    ds = SyntheticSeqDataset(num_samples=256, seq_len=cfg.seq_len, vocab_size=cfg.vocab_size)
    dl = DataLoader(ds, batch_size=cfg.batch_size, shuffle=True)
    val_ds = SyntheticSeqDataset(num_samples=64, seq_len=cfg.seq_len, vocab_size=cfg.vocab_size)
    val_dl = DataLoader(val_ds, batch_size=cfg.batch_size, shuffle=False)
    model = TinyTransformerLM(vocab_size=cfg.vocab_size, max_len=cfg.seq_len).to(device)
    opt = torch.optim.Adam(model.parameters(), lr=cfg.lr)
    loss_fn = torch.nn.CrossEntropyLoss(ignore_index=0)

    # logging and checkpoint dirs
    os.makedirs(cfg.save_dir, exist_ok=True)
    os.makedirs(cfg.log_dir, exist_ok=True)
    try:
        from torch.utils.tensorboard import SummaryWriter
        writer = SummaryWriter(log_dir=cfg.log_dir)
    except Exception:
        writer = None

    for epoch in range(cfg.epochs):
        model.train()
        for i, (x, y) in enumerate(dl):
            x = x.to(device)
            y = y.to(device)
            logits = model(x)  # (batch, seq_len, vocab)
            loss = loss_fn(logits.view(-1, logits.size(-1)), y.view(-1))
            opt.zero_grad()
            loss.backward()
            opt.step()
            print(f"Epoch {epoch} iter {i} loss={loss.item():.4f}")
            if writer:
                writer.add_scalar("train/loss", loss.item(), epoch * len(dl) + i)
            if cfg.dry_run:
                if writer:
                    writer.flush()
                return

        # validation pass
        model.eval()
        val_loss = 0.0
        val_steps = 0
        with torch.no_grad():
            for x, y in val_dl:
                x = x.to(device)
                y = y.to(device)
                logits = model(x)
                loss = loss_fn(logits.view(-1, logits.size(-1)), y.view(-1))
                val_loss += loss.item()
                val_steps += 1
        val_loss = val_loss / max(1, val_steps)
        print(f"Epoch {epoch} validation loss={val_loss:.4f}")
        if writer:
            writer.add_scalar("val/loss", val_loss, epoch)

        # checkpoint
        if (epoch + 1) % cfg.checkpoint_interval == 0:
            ckpt_path = f"{cfg.save_dir}/ckpt_epoch_{epoch+1}.pt"
            torch.save({"model": model.state_dict(), "opt": opt.state_dict(), "epoch": epoch}, ckpt_path)
            print(f"Saved checkpoint: {ckpt_path}")
            if writer:
                writer.add_text("checkpoint", ckpt_path, epoch)

    if writer:
        writer.flush()


if __name__ == "__main__":
    cfg = parse_args()
    train(cfg)
