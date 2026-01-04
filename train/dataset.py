import torch
from torch.utils.data import Dataset


class SyntheticSeqDataset(Dataset):
    """Generates random integer sequences for quick experiments.

    Each sample is a sequence of length `seq_len` with values in [1, vocab_size-1].
    The target is the input shifted by one position (next-token prediction).
    """

    def __init__(self, num_samples=1024, seq_len=32, vocab_size=1000):
        self.num_samples = num_samples
        self.seq_len = seq_len
        self.vocab_size = vocab_size

    def __len__(self):
        return self.num_samples

    def __getitem__(self, idx):
        seq = torch.randint(1, self.vocab_size, (self.seq_len,), dtype=torch.long)
        # target is next-token (shifted), last token target is 0 (padding/ignore)
        target = torch.roll(seq, -1)
        target[-1] = 0
        return seq, target
