from train.dataset import SyntheticSeqDataset


def test_dataset_len_and_shape():
    ds = SyntheticSeqDataset(num_samples=10, seq_len=16, vocab_size=100)
    x, y = ds[0]
    assert len(ds) == 10
    assert x.shape[0] == 16
    assert y.shape[0] == 16
