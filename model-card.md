# Model Card — ECG Multi-Label Classifier

**Status: not yet trained.** This card is a template to fill in once `python -m ml.training.train` has been run against real PTB-XL data and a checkpoint exists at `ml/checkpoints/best_model.pt`. Do not present filled-in numbers anywhere (demo, slides, README) until they come from an actual evaluation run.

## Intended use
- Research / educational prototype for automated ECG signal analysis.
- Intended to assist, not replace, clinician interpretation.

## Non-intended use
- Not validated or cleared as a medical device.
- Not intended for autonomous clinical decision-making.
- Not intended for use on pediatric ECGs, paced rhythms, or non-standard lead placements unless separately validated for those populations.

## Training data
- **Dataset:** PTB-XL v1.0.1 (PhysioNet), 21,837 12-lead ECGs from 18,885 patients.
- **Split:** official PTB-XL `strat_fold` (folds 1–8 train / 9 validation / 10 test), which is already patient-stratified.
- **Labels:** simplified 5-class multi-label set mapped from PTB-XL diagnostic superclasses (`normal`, `atrial_fibrillation`, `conduction_abnormality`, `st_t_abnormality`, `other_abnormality`) — see `SUPERCLASS_MAP` in `ml/preprocessing/ptbxl_dataset.py`. This is a deliberately reduced label set for a first training pass, not the full 71-statement PTB-XL ontology.

## Preprocessing
See `docs/methodology.md`.

## Model architecture
Baseline 1D CNN (`ECG1DCNN` in `ml/training/model.py`): 5 conv blocks (channels 32→64→128→128→256) with batch norm, ReLU, max pooling, global average pooling, and a 2-layer dense head. ~[parameter count: fill in from `sum(p.numel() for p in model.parameters())` once instantiated]. Multi-label output via sigmoid (not softmax) — an ECG can carry more than one finding simultaneously.

## Training procedure
- Loss: `BCEWithLogitsLoss` with per-class `pos_weight` computed from training-set class frequency (class-weighted, not naive oversampling).
- Optimizer: Adam.
- Best checkpoint selected by validation macro F1, not final epoch.

## Evaluation metrics
| Metric | Value |
|---|---|
| Test ECGs | 2203 |
| Macro F1 | 0.6088 (see note below — one label had zero examples) |
| Macro Precision | 0.5698 |
| Macro Recall | 0.6607 |
| Macro AUROC | 0.9169 |
| Macro AUPRC | 0.8426 |

**Per-class breakdown:**

| Class | F1 | Precision | Recall | AUROC |
|---|---|---|---|---|
| normal | 0.8388 | 0.7859 | 0.8994 | 0.9293 |
| conduction_abnormality | 0.7527 | 0.7389 | 0.7671 | 0.9175 |
| st_t_abnormality | 0.7197 | 0.6036 | 0.8910 | 0.9302 |
| other_abnormality | 0.7330 | 0.7205 | 0.7459 | 0.8906 |
| atrial_fibrillation | 0.0000 | 0.0000 | 0.0000 | n/a — zero test examples (see limitation below) |

## Known limitations
- Trained and evaluated only on PTB-XL — a single-country, single-era dataset. Performance on other populations/equipment is unknown until separately tested.
- The image → waveform pipeline (grid removal, layout detection, calibration) is separately fallible; a "correct" model prediction on a poorly-digitized image is not evidence the end-to-end system works.
- Model outputs are probabilities from a classifier, not calibrated diagnostic confidence. "94% probability" is not the same claim as "94% accurate."
- No fairness/subgroup analysis has been performed.
- - The `atrial_fibrillation` label received zero positive examples in training or test data. PTB-XL encodes AF as a rhythm statement rather than a diagnostic superclass, and this build's label mapping (`SUPERCLASS_MAP` in `ml/preprocessing/ptbxl_dataset.py`) only covers diagnostic superclasses. This is a known labeling gap, not a model failure — the four other classes above have real support and real, reported scores.


## Ethical considerations
Do not deploy for autonomous triage or diagnosis. Any real-world pilot should include clinician review of every output before it reaches a patient-facing decision.
