# Review-II preparation package

Start with [REVIEW_2_GUIDE.md](REVIEW_2_GUIDE.md) for the analysis, requirements, architecture, component choices, ten-slide outline, roadmap and review questions.

From the repository root, install and run:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python source/prototype.py
```

From inside this `source` folder, use `../.venv/bin/python prototype.py` after installation. On Windows use the environment's `Scripts/python.exe`.

Files:
- `prototype.py`: NumPy PUF simulation and PyTorch logistic-regression training/inference.
- `crps.csv`: 16,000 unique synthetic challenge-response records with fixed train/validation/test splits.
- `attack_results.csv`: six measured attack results (two designs, three training sizes).
- `results.json`: configuration, framework versions, limitations and metrics.
- `REVIEW_2_GUIDE.md`: presentation preparation guide.

The PUF calculation, fixed device parameters, challenge generation, XOR combination and splits are unchanged by the PyTorch migration. The attack remains logistic regression: one linear score, binary cross-entropy loss, and Adam updates. The fixed seed and CPU execution make the experiment repeatable; timing varies. Rerunning overwrites the result files next to the script.

For your viva: “NumPy models the PUF. PyTorch learns an attack model from CRPs using automatic differentiation and Adam. We keep unseen challenges separate to measure prediction accuracy.”

All measurements are synthetic. The full hybrid, physical hardware and AI reliability controller have not been implemented. The XOR comparison uses ordinary logistic regression, not a specialized XOR attack.
