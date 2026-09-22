# AI-Enhanced Hybrid PUF: Review-II preparation

Prepared from your 14-page overview and the supplied review notice. The notice asks for approximately 20% completion, including requirement analysis, system design, component selection, and an initial prototype/module demonstrating feasibility. It does not specify a slide count or require a finished hybrid system.

**Status:** This package adds a runnable software prototype. It does not establish what your team completed previously. FPGA implementation, the RO module, full hybrid integration and AI reliability compensation remain future work. Confirm with your guide whether a simulation module satisfies your department's initial-prototype expectation.

## 1. Understand the project

A physically unclonable function (PUF) uses manufacturing differences to give a device a characteristic response to an input challenge. In an Arbiter PUF, signals race through two paths; a final arbiter reports which arrives first. A challenge chooses the routing. A challenge-response pair (CRP) is one input and its observed output.

A physical circuit may be difficult to duplicate, yet its input-output behavior can still be predicted. An attacker who learns that behavior can impersonate the device without manufacturing a physical copy. Our experiment studies this modeling problem and the competing need for repeatable responses.

**Defensible problem statement:** Design and evaluate a hybrid PUF candidate that reduces prediction by specified machine-learning attacks at stated data and compute budgets, while retaining repeatable device-specific responses and acceptable implementation cost.

This is an experimental research objective, not a promise of universal ML resistance. The final outcome can be a measured tradeoff, including a negative result explaining why a candidate fails.

## 2. Gaps in existing technology

| Gap | Consequence | What this project should measure |
|---|---|---|
| A conventional Arbiter PUF has a learnable additive-delay structure | Observed CRPs can enable software impersonation | Unseen-challenge attack accuracy as training data increases |
| XOR and other compositions are also targets of specialized attacks | More blocks do not automatically provide security | Structure-aware attacks in addition to generic LR/SVM/MLP |
| Readout noise and environmental changes can flip responses | A genuine device can fail verification | Bit-error rate over repeats and measured temperature/voltage conditions |
| Hardening costs area, time and sometimes reliability | A stronger candidate may be unsuitable for a small device | Security-reliability-cost comparison |
| Weak experimental protocols can overstate resistance | An undertrained attacker or noisy output can look secure | Separate train/validation/test data, multiple seeds, sufficient attack budgets and explicit noise levels |

Evidence: Rührmair et al. demonstrated modeling attacks on several PUF families. Sayadi et al. (2025 version) report a chosen-challenge attack against XOR Arbiter PUFs even without reliability information. These establish that XOR alone is not a security guarantee. References appear at the end.

The novelty is not simply 'using AI' or putting known PUF types together. A stronger contribution is a precisely specified architecture, a fair attack evaluation, and evidence of where the reliability/cost tradeoff improves.

## 3. Corrections needed in the current overview

1. **Replace 'resistant to machine-learning modeling attacks' with an objective until tested.** Suggested title: 'AI-Assisted Hybrid PUF: Design and Evaluation Against Modeling Attacks'.
2. **Specify the combiner.** 'Keyed non-linear combiner' is not yet an implementable circuit definition. State the input widths, exact function, timing, and key source. If an ordinary stored secret supplies the security, distinguish its contribution from the PUF's.
3. **A permutation is not itself a nonlinear security mechanism.** Define any additional nonlinear transformation mathematically, assume public architecture, and attack the resulting structure.
4. **Define how challenges select RO pairs.** A bank of m oscillators has at most m(m-1)/2 distinct unordered direct comparisons. Re-labelling pairs with many challenge bits does not create that many independent responses. Shared oscillators also create correlations.
5. **Give the AI layer a specific job.** Predicting a reliability score or selecting a measurement/repetition setting is easier to justify than claiming temperature and voltage alone can reconstruct arbitrary flipped response bits.
6. **Do not let AI silently replace the PUF.** A model that predicts the enrolled response from challenge bits can become a software clone. Define what remains secret and what an attacker can observe, including retries, acceptance decisions and helper data.
7. **Remove 'adaptive defense' as a solved contribution unless adaptation is actually implemented.** Periodic re-evaluation is not automatic attack adaptation.
8. **Do not claim physical unclonability, area, power, aging tolerance or environmental robustness from a synthetic simulator.** Report the limits separately.
9. **Treat 50% as a balanced-bit reference, not a universal security threshold.** Always include a majority-class baseline; show uncertainty and attacker tuning. A poor fixed classifier is not the best attacker.

## 4. Review-II requirements and evidence

| Review requirement | Concrete material to show tomorrow | Status in this package |
|---|---|---|
| Requirement analysis | Problem statement, scope, threat model, functional requirements and evaluation plan | Written below |
| System design | Proposed block flow and clearly marked implementation boundary | Written below |
| Component selection | Software choices and reasons; hardware selection criteria | Written below |
| Initial prototype/module | 64-stage additive-delay Arbiter simulator, CRP export and LR attack | Implemented and run |
| Feasibility evidence | Held-out baseline attack results and preliminary XOR comparison | Measured in simulation |

Approximately 20% refers to your institution's assessment, not an exact percentage proven by these files. Describe completed deliverables rather than inventing progress percentages.

### Functional requirements

- Accept a 64-bit challenge and return a one-bit response.
- Keep a simulated device's underlying delay parameters fixed across queries.
- Collect CRPs with device ID, split, seed and measurement conditions when applicable.
- Evaluate baseline and candidate designs on consistent challenge sets and attack budgets.
- Reproduce each run from recorded configuration and seeds.
- Eventually assess repeated measurements and compare an AI-assisted reliability method with a simple non-AI method.

### Quality and evaluation requirements

- First sanity check: demonstrate more than 90% baseline prediction accuracy under a documented noiseless simulation configuration. This is a prototype validation target, not a universal hardware requirement.
- Compare attacker performance with class-frequency baselines and report test size.
- Aim for balanced responses and inter-device Hamming distance near 50%; neither is a security proof.
- Choose a reliability acceptance target based on the final authentication protocol; report bit-level and whole-response behavior separately.
- Report inference time and model size; use synthesis reports for resource estimates and physical measurement for physical claims.

### Initial threat model

The attacker knows the design and public preprocessing but not a target device's fixed delay parameters. The initial experiment exposes random CRPs from one simulated device. Training data are disjoint from held-out challenges. This first module excludes physical probing, side channels and chosen/repeated challenge attacks. Add the latter two query strategies in later evaluations rather than claiming protection now.

### Architecture and module boundaries

Implemented module:

    64-bit challenge -> additive-delay Arbiter simulator -> response
                                                    |
                                                CRP dataset
                                                    |
                                  logistic attack -> unseen-challenge accuracy

Proposed candidate flow (not implemented):

    Challenge -> specified public preprocessing -> parallel Arbiter chains -> XOR --+
                -> specified RO-pair selection -> RO comparison --------------------+-> specified combiner -> response
    Temperature/voltage + permitted measurement metadata -> reliability controller
    Reliability controller -> measurement settings / internal repeats / acceptance flag

Baseline, XOR-only, RO-only and hybrid must remain independently testable. The precise hybrid combiner remains a design decision to validate; a block diagram alone is not a completed circuit specification. If trialing XOR as the first combiner, label it explicitly as a linear combination and evaluate its limitations.

### Component selection

| Component | Selection for this review | Reason / limit |
|---|---|---|
| Development platform | Laptop + Python 3 | Immediate reproducible simulation |
| Numerical library | NumPy | CRP generation and the additive-delay PUF model |
| ML framework | PyTorch | Logistic-regression attacker using a linear layer, binary cross-entropy and Adam |
| Initial PUF | 64-stage Arbiter model | Clear baseline with known modeling vulnerability |
| First comparison | Three-chain XOR Arbiter model | Small controlled composition, not full hybrid |
| Data | 16,000 unique synthetic challenges | 10,000 training, 2,000 validation, 4,000 test |
| Future attacks | Additional scikit-learn / PyTorch models or established PUF attack implementations | Generic plus structure-aware models; verify licensing and versions |
| Future hardware | Available departmental FPGA, subject to board confirmation | Check tool support, access to temperature monitoring, timing/routing control and communications |
| Future interface | Board USB/UART | Read CRPs without exporting internal component responses in the deployed interface |

Do not buy a board based on the overview's unverified prices. An Arbiter PUF depends on physical routing and delay; a functional RTL simulation alone does not show manufacturing entropy. FPGA placement/routing and prevention of RO optimization are implementation work, not automatic tool outcomes.

## 5. Actual prototype results

One fixed random seed; synthetic fixed Gaussian delay coefficients; noiseless attack dataset. All training sizes share the same independent 4,000-challenge test set. The optimizer and hyperparameters were fixed in advance; no test-set tuning was performed. Validation results are recorded but not used to select settings in this initial run.

| Training CRPs | Baseline Arbiter: simple LR | 3-XOR: same simple LR |
|---:|---:|---:|
| 1,000 | 96.88% | 55.15% |
| 5,000 | 99.12% | 55.55% |
| 10,000 | 99.38% | 54.75% |

At 10,000 training CRPs, the training-majority predictor achieves 56.10% on baseline test labels and 53.25% on XOR test labels. The XOR attack's 54.75% is not evidence of exactly random behavior or of resistance to stronger attacks. A linear classifier on the additive features is deliberately only an initial comparison; specialized XOR attacks can model the composition.

Additional illustrative checks: 20 synthetic devices yield mean inter-device Hamming distance 50.55%. Adding independent Gaussian read noise with standard deviation 0.05 in normalized delay units yields 98.59% agreement with noiseless baseline responses over 20 reads per test challenge. This is NOT a temperature/voltage experiment, a hardware measurement, or an AI improvement. Population means can hide per-device and per-challenge bias.

### How the simulator works

For challenge bits c_i, form s_i = 1 - 2c_i. The additive-delay feature phi_i is the product of s_j from stage i through the last stage; append a constant bias feature. Compute delay difference d = w dot phi. Output 1 if d >= 0, otherwise 0. Device weights w are sampled once and held fixed. This is a simplified educational model consistent with the additive-delay form, not a transistor-level or calibrated FPGA model.

The attack sees challenge-derived features and response labels; it does not receive the hidden simulated device weights. Logistic regression learns its own coefficients. Using the appropriate features is essential: an attack on raw challenge bits alone could understate baseline vulnerability.

### Reproduce the demonstration

Install the pinned NumPy and PyTorch dependencies from the repository root:

    python3 -m venv .venv
    .venv/bin/python -m pip install -r requirements.txt
    .venv/bin/python source/prototype.py

On Windows, use `.venv\Scripts\python.exe` in place of `.venv/bin/python`. The recorded environment uses Python 3.13. PyTorch performs logistic-regression training and prediction; NumPy performs PUF simulation. The model uses one linear score, BCEWithLogitsLoss, automatic gradients and Adam for 500 steps on CPU in float64 precision. The intercept is the existing constant feature and is excluded from L2 regularization. This framework change preserves the original experiment and does not add a neural network with hidden layers. Training time includes model setup and varies by host.

Outputs: `results.json`, `attack_results.csv`, and `crps.csv`. Results are deterministic apart from timing and minor numerical variation. The script checks challenge uniqueness, a known feature-transform example, deterministic responses and XOR parity. It contains no FPGA communication and no full-hybrid or compensation module.

Demo sequence: explain one challenge and response; run the script; show the train/test counts; point to 99.38% baseline attack accuracy; then show the limited XOR comparison and explain the next stronger attack needed. Read and understand the code before presenting it as part of your team's work; follow your institution's rules on AI assistance.

## 6. Suggested 10-slide Review-II structure

1. **Title and objective:** Design and evaluate an AI-assisted hybrid PUF candidate.
2. **Existing system:** Arbiter signal race, challenge and response, software impersonation risk.
3. **Gap and problem statement:** Modeling vulnerability, reliability and implementation cost.
4. **Requirements and threat model:** What the attacker sees; how results will be evaluated.
5. **Proposed architecture:** Draw the flow above; distinguish implemented and planned modules.
6. **Component selection:** Explain Python/NumPy/PyTorch, 64 stages, XOR comparison and conditional FPGA path.
7. **Implemented initial module:** Show the simulator, CRP schema and dataset splits.
8. **Preliminary results:** Use the measured table; state single-seed, synthetic-data limitations.
9. **Remaining work and risks:** RO integration, exact combiner, stronger attacks and reliability model.
10. **Roadmap and conclusion:** Feasibility demonstrated for simulation/data/attack pipeline; hybrid benefit remains to be established.

Opening you can adapt: 'Our project investigates device authentication using physically unclonable functions. A device may be difficult to physically copy, but attackers can still learn its responses. In this review, we present our requirements, proposed architecture, component choices and an initial simulation that demonstrates this modeling vulnerability. Next, we will evaluate whether a hybrid design improves the tradeoff between attack resistance, repeatability and cost.'

## 7. Roadmap after this review

| Stage | Work | Completion evidence |
|---|---|---|
| Week 1 | Freeze scope, application, threat model and literature comparison | Requirements and experiment specification approved by guide |
| Week 2 | Validate baseline across device seeds; expand CRPs toward 50k-100k | Reproducible baseline attack curves and dataset checks |
| Weeks 3-4 | Implement RO model and explicitly specified hybrid candidate | Unit-level behavior plus baseline/XOR/RO/hybrid comparisons |
| Week 5 | Tune MLP/SVM and add structure-aware XOR attack; document compute budget | Strongest attack per design with repeated runs |
| Week 6 | Introduce justified noise/environment model; acquire physical data if possible | Repeatability curves and documented calibration limits |
| Week 7 | Add a small reliability controller; compare with fixed majority voting or stable-challenge selection | BER, rejection rate, latency and leakage tradeoff |
| Weeks 8-9 | If hardware is required, implement and measure on available FPGA; start board/tool setup earlier | Resource/timing reports, measured CRPs and physical repeatability |
| Week 10 | Final comparisons, authentication demonstration, report and presentation | Traceable results and honest claims |

Adjust this schedule to the actual submission date and board availability. If hardware is mandatory, confirm access now and begin placement/routing feasibility early. If only one board is available, do not call repeated reconfigurations independent manufactured chips; label instance variation separately from inter-chip uniqueness.

## 8. Improvements likely to strengthen assessment

- **Ablation study:** baseline -> XOR -> RO contribution -> specified obfuscation/combination -> AI controller. Quantify what each addition changes.
- **AI versus non-AI comparison:** a small reliability model must beat a simple alternative at a matched read/latency budget. If it does not, explain why.
- **Stronger attack evaluation:** use architecture-aware attacks, multiple initializations, training-size curves and a fixed unseen test set.
- **Authentication demonstration:** enroll a device, issue fresh challenges, compare genuine and attacker responses, and measure false rejection/acceptance under a stated protocol. Avoid reusing CRPs in a way that permits trivial replay.
- **Transparent uncertainty:** multiple synthetic device seeds, error bars and clear separation of simulated and physical measurements.
- **Cost-aware result:** graph prediction accuracy, reliability and resources together. A defensible tradeoff is more valuable than extra unexplained blocks.

Do not add blockchain, more AI models or arbitrary scrambling solely to increase complexity. Prioritize controlled experiments and an explanation you can defend.

## 9. Likely review questions

**What is new?** 'Our planned contribution is the specified hybrid architecture and a controlled security/reliability comparison. We are not claiming to have invented XOR or RO PUFs.'

**Where is AI?** 'The modeling attacker is implemented now. A separate lightweight reliability controller is planned; it is not yet demonstrated.'

**Why does baseline LR work?** 'The additive-delay model is a linear threshold in challenge-derived parity features, so a classifier can estimate its decision boundary.'

**Does 54.75% prove security?** 'No. It is one simple attack on one simulated XOR instance. Stronger structure-aware attacks and multiple runs are required.'

**What does the prototype prove?** 'We can generate a reproducible PUF-like dataset and demonstrate baseline modeling vulnerability. It does not prove physical unclonability or hybrid security.'

**How will you assess reliability?** 'Repeat identical challenges, compare against enrolled reference responses, and measure bit errors across declared conditions. Synthetic noise and measured environmental data will be reported separately.'

**What if the hybrid is attacked successfully?** 'We will report the attack and analyze the tradeoff. A credible evaluation is a valid result; security cannot be asserted in advance.'

## 10. Priority order for tonight

1. Understand and rerun the supplied prototype; check that you can explain features, hidden device weights and held-out data.
2. Prepare the ten-slide sequence with a visible implemented/planned distinction.
3. Include the five required review deliverables rather than only background slides.
4. Keep local copies of the code, CSV and results for an offline demonstration.
5. Rehearse a 5-7 minute explanation and the questions above.
6. Confirm hardware expectations and the actual remaining calendar with your guide.

## Sources

- User-provided project overview, AI_Enhanced_Hybrid_PUF_Project_Presentation_WhatsApp.pdf, pages 2-13; supplied Review-II notice.
- Rührmair et al., Modeling Attacks on Physical Unclonable Functions (2010): https://eprint.iacr.org/2010/251
- Sayadi et al., Breaking XOR Arbiter PUFs with Chosen Challenge Attack (2025 revision): https://arxiv.org/abs/2312.01256
- pypuf documentation, Arbiter PUFs and Compositions: https://pypuf.readthedocs.io/en/latest/simulation/arbiter_puf.html
- Wisiol and Pirnay, XOR Arbiter PUFs have Systematic Response Bias (2019): https://eprint.iacr.org/2019/1091

The recommendations and candidate architecture decisions above are engineering proposals for this project, not results demonstrated by these references.
