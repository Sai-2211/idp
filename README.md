# IDP — AI-Enhanced Hybrid PUF

Review-II preparation and an educational PUF simulation prototype.

## Start here

- [Review guide, architecture, roadmap and viva questions](review2/REVIEW_2_GUIDE.md)
- [Prototype](review2/prototype.py)
- [Measured attack results](review2/attack_results.csv)
- [Configuration and metrics](review2/results.json)
- [Synthetic challenge-response dataset](review2/crps.csv)
- [Downloadable preparation package](Review_2_Preparation.zip)

## Run

Requires Python 3 and NumPy.

```sh
python3 -m pip install -r requirements.txt
python3 review2/prototype.py
```

## Scope

This initial module simulates a 64-stage Arbiter PUF, generates 16,000 unique challenges and runs an educational logistic-regression attack. It also provides a preliminary three-chain XOR comparison.

All results are synthetic. The full hybrid, Ring-Oscillator module, FPGA implementation and AI reliability controller are future work. Low accuracy from one simple attack is not proof of security.
