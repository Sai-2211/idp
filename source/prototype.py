"""Review-II: educational additive-delay Arbiter PUF and logistic attack.
Requires NumPy + PyTorch (see ../requirements.txt). Run: python3 prototype.py
Synthetic fixed-delay devices; no FPGA, physical validation, RO or AI compensation.
"""
from pathlib import Path
import csv, json, time
import numpy as np
import torch
from torch import nn

OUT = Path(__file__).resolve().parent

def features(challenges):
    s = 1 - 2 * challenges.astype(np.int8)
    return np.column_stack((np.cumprod(s[:, ::-1], axis=1)[:, ::-1], np.ones(len(s))))

class LogisticRegression(nn.Module):
    """Attacker: one weighted score per challenge, with no hidden layers."""

    def __init__(self, feature_count):
        super().__init__()
        # features() already appends a constant 1 for the intercept, so there
        # must not be a second bias. Float64 matches the original NumPy model.
        self.linear = nn.Linear(feature_count, 1, bias=False,
                                device="cpu", dtype=torch.float64)
        nn.init.zeros_(self.linear.weight)

    def forward(self, x):
        return self.linear(x).squeeze(-1)


def fit_lr(x, y, steps=500):
    """Learn from known CRPs using PyTorch's automatic gradients and Adam."""
    inputs = torch.as_tensor(x, dtype=torch.float64, device="cpu")
    targets = torch.as_tensor(y, dtype=torch.float64, device="cpu")
    model = LogisticRegression(x.shape[1])
    # This combines the sigmoid probability calculation and binary loss.
    criterion = nn.BCEWithLogitsLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.05,
                                 betas=(0.9, 0.999), eps=1e-8, foreach=False)
    model.train()
    for _ in range(steps):
        optimizer.zero_grad(set_to_none=True)  # Clear the previous gradients.
        logits = model(inputs)                # Predict scores for training CRPs.
        loss = criterion(logits, targets)      # Compare with known response bits.
        # Same L2 penalty as before: exclude the final intercept coefficient.
        loss = loss + 0.5e-4 * model.linear.weight[:, :-1].square().sum()
        loss.backward()                       # PyTorch calculates the gradients.
        optimizer.step()                      # Adam updates attacker weights.
    model.eval()
    return model


def predict(model, x):
    """Predict unseen responses without changing the trained attacker."""
    model.eval()
    with torch.inference_mode():
        inputs = torch.as_tensor(x, dtype=torch.float64, device="cpu")
        # A score >= 0 corresponds to a probability >= 0.5.
        return (model(inputs) >= 0).numpy()

def main():
    # Fixed CPU execution makes this small viva demo easy to reproduce.
    torch.manual_seed(20260922)
    torch.set_num_threads(1)
    torch.use_deterministic_algorithms(True)
    rng = np.random.default_rng(20260922)
    n = 64; count = 16000
    c = rng.integers(0, 2, (count, n), dtype=np.int8)
    assert len(np.unique(c, axis=0)) == count, 'Duplicate challenges'
    x = features(c).astype(float)
    # Fixed weights per simulated device. Normalized arbitrary delay units.
    device_w = rng.normal(0, 1/np.sqrt(n+1), (3, n+1))
    responses = (x @ device_w.T >= 0).astype(np.int8)
    labels = {'Arbiter': responses[:,0], '3-XOR Arbiter': np.bitwise_xor.reduce(responses, axis=1)}
    train = slice(0, 10000); valid = slice(10000, 12000); test = slice(12000, 16000)
    rows = []
    for name,y in labels.items():
        for size in [1000, 5000, 10000]:
            start = time.perf_counter()
            model = fit_lr(x[:size], y[:size])
            seconds = time.perf_counter()-start
            pred = predict(model, x[test])
            accuracy = float(np.mean(pred == y[test]))
            majority = int(np.mean(y[:size]) >= .5)
            rows.append({'design':name,'train_crps':size,'validation_accuracy':float(np.mean(predict(model, x[valid])==y[valid])), 'test_accuracy':accuracy,'train_majority_test_accuracy':float(np.mean(y[test]==majority)),'train_seconds':seconds})
    # Population metrics are illustrative; 20 independently sampled SYNTHETIC devices.
    pop_w = rng.normal(0, 1/np.sqrt(n+1), (20,n+1))
    pop_r = (x[test]@pop_w.T >= 0).astype(np.int8)
    uniqueness = np.mean([np.mean(pop_r[:,i] != pop_r[:,j]) for i in range(20) for j in range(i+1,20)])
    # Independent additive Gaussian read noise only; NOT calibrated T/V variation.
    margins = x[test]@device_w[0]
    reference = margins >= 0
    noisy = margins[:,None] + rng.normal(0,.05,(len(margins),20))
    reliability = np.mean((noisy >= 0) == reference[:,None])
    summary = {'scope':'Synthetic additive-delay model only; no measured hardware or hybrid security result', 'seed':20260922, 'challenge_bits':n,'total_unique_crps':count,'train':10000,'validation':2000,'test':4000,'optimizer':'PyTorch Adam logistic regression; 500 full-batch steps; lr=.05, L2=1e-4 (no intercept penalty); no hyperparameter search', 'baseline_test_fraction_ones':float(labels['Arbiter'][test].mean()),'xor_test_fraction_ones':float(labels['3-XOR Arbiter'][test].mean()), 'simulated_devices':20,'synthetic_population_uniqueness':float(uniqueness),'synthetic_population_mean_bit_aliasing':float(pop_r.mean()),'illustrative_noise_std':.05,'illustrative_reliability_vs_noiseless_reference':float(reliability),'attacks':rows}
    summary.update({'framework': 'PyTorch', 'torch_version': torch.__version__,
                    'numpy_version': np.__version__, 'training_device': 'cpu',
                    'training_dtype': 'float64', 'torch_threads': torch.get_num_threads()})
    (OUT/'results.json').write_text(json.dumps(summary,indent=2))
    with (OUT/'attack_results.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
    with (OUT/'crps.csv').open('w',newline='') as f:
        w=csv.writer(f);w.writerow(['challenge_64_bits','arbiter_response','xor3_response','split'])
        for i in range(count):
            w.writerow([''.join(map(str,c[i])),labels['Arbiter'][i],labels['3-XOR Arbiter'][i], 'train' if i<10000 else 'validation' if i<12000 else 'test'])
    # Behavioral checks: fixed device is deterministic, feature convention and XOR correct.
    assert np.array_equal(features(np.array([[0,0],[0,1],[1,0],[1,1]])),[[1,1,1],[-1,-1,1],[-1,1,1],[1,-1,1]])
    assert np.array_equal((features(c[:50])@device_w[0]>=0).astype(int),labels['Arbiter'][:50])
    assert np.array_equal(labels['3-XOR Arbiter'],responses.sum(axis=1)%2)
    print(json.dumps(summary,indent=2))

if __name__=='__main__':
    main()
