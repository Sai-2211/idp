# Review-II preparation package

Start with REVIEW_2_GUIDE.md. It contains the analysis, requirements, architecture, component choices, ten-slide outline, roadmap and review questions.

Run `python3 prototype.py` with NumPy installed. No other Python packages are required.

Files:
- prototype.py: runnable educational simulation and logistic-regression attack.
- crps.csv: 16,000 unique synthetic challenge-response records with fixed train/validation/test splits.
- attack_results.csv: measured attack results.
- results.json: configuration, limitations and measured metrics.
- REVIEW_2_GUIDE.md: presentation preparation guide.

All measurements are synthetic. The full hybrid, physical hardware and AI reliability controller have not been implemented in this package. The XOR comparison uses ordinary logistic regression, not a specialized XOR attack. Timing depends on the host.
