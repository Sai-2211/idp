"""Review-II: educational additive-delay Arbiter PUF and logistic attack.
Requires Python 3 + NumPy. Run: python3 prototype.py
Synthetic fixed-delay devices; no FPGA, physical validation, RO or AI compensation.
"""
from pathlib import Path
import csv, json, time
import numpy as np

OUT = Path(__file__).resolve().parent

def features(challenges):
    s = 1 - 2 * challenges.astype(np.int8)
    return np.column_stack((np.cumprod(s[:, ::-1], axis=1)[:, ::-1], np.ones(len(s))))

def fit_lr(x, y, steps=500):
    # Full-batch Adam minimizes binary cross entropy, L2=1e-4 (no bias penalty).
    w = np.zeros(x.shape[1]); m = w.copy(); v = w.copy()
    for t in range(1, steps + 1):
        z = np.clip(x @ w, -40, 40)
        p = 1 / (1 + np.exp(-z))
        reg = 1e-4*w; reg[-1] = 0
        g = x.T @ (p-y) / len(y) + reg
        m = .9*m + .1*g; v = .999*v + .001*g*g
        w -= .05 * (m/(1-.9**t)) / (np.sqrt(v/(1-.999**t)) + 1e-8)
    return w

def main():
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
            w = fit_lr(x[:size], y[:size])
            seconds = time.perf_counter()-start
            pred = x[test]@w >= 0
            accuracy = float(np.mean(pred == y[test]))
            majority = int(np.mean(y[:size]) >= .5)
            rows.append({'design':name,'train_crps':size,'validation_accuracy':float(np.mean((x[valid]@w >= 0)==y[valid])), 'test_accuracy':accuracy,'train_majority_test_accuracy':float(np.mean(y[test]==majority)),'train_seconds':seconds})
    # Population metrics are illustrative; 20 independently sampled SYNTHETIC devices.
    pop_w = rng.normal(0, 1/np.sqrt(n+1), (20,n+1))
    pop_r = (x[test]@pop_w.T >= 0).astype(np.int8)
    uniqueness = np.mean([np.mean(pop_r[:,i] != pop_r[:,j]) for i in range(20) for j in range(i+1,20)])
    # Independent additive Gaussian read noise only; NOT calibrated T/V variation.
    margins = x[test]@device_w[0]
    reference = margins >= 0
    noisy = margins[:,None] + rng.normal(0,.05,(len(margins),20))
    reliability = np.mean((noisy >= 0) == reference[:,None])
    summary = {'scope':'Synthetic additive-delay model only; no measured hardware or hybrid security result', 'seed':20260922, 'challenge_bits':n,'total_unique_crps':count,'train':10000,'validation':2000,'test':4000,'optimizer':'Fixed 500-step Adam logistic regression; lr=.05, L2=1e-4; no hyperparameter search', 'baseline_test_fraction_ones':float(labels['Arbiter'][test].mean()),'xor_test_fraction_ones':float(labels['3-XOR Arbiter'][test].mean()), 'simulated_devices':20,'synthetic_population_uniqueness':float(uniqueness),'synthetic_population_mean_bit_aliasing':float(pop_r.mean()),'illustrative_noise_std':.05,'illustrative_reliability_vs_noiseless_reference':float(reliability),'attacks':rows}
    (OUT/'results.json').write_text(json.dumps(summary,indent=2))
    with (OUT/'attack_results.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
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
