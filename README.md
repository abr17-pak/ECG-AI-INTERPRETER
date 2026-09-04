# ECG-AI Interpreter

An AI-assisted ECG interpretation system: accepts a 12-lead ECG image,
reconstructs the underlying waveform, performs signal-level measurement
(HR/PR/QRS/QT/QTc/ST), predicts clinically relevant patterns with a trained
ML model, explains the findings, and reports its own uncertainty and image
quality rather than guessing when it shouldn't.

**Research prototype — not a medical diagnostic device.**

## Status

| Component | Status |
|---|---|
| Signal preprocessing (filtering, baseline correction) | Implemented, tested |
| R-peak detection | Implemented, tested on synthetic signals — **not yet validated against MIT-BIH** |
| Interval measurement engine (HR/PR/QRS/QT/QTc/ST) | Implemented, tested |
| Image quality gate | Implemented, tested |
| Layout detection + grid removal + trace extraction | Implemented — v1 assumes a standard 3×4 layout, see `docs/methodology.md` |
| Calibration (px → ms/mV) | Placeholder constant, not yet automatic |
| Multi-label 1D CNN + training script | Implemented — **not yet trained** (PTB-XL not downloadable from the build sandbox) |
| Evaluation harness (F1/AUROC/AUPRC/confusion matrix) | Implemented, no results yet (needs a trained model) |
| Uncertainty / quality gate (green/yellow/red) | Implemented, tested end-to-end |
| Explanation engine (Ollama-optional) | Implemented |
| FastAPI backend | Implemented, tested end-to-end (see below) |
| Frontend | Implemented (single-page, talks to the API) |
| Automated test suite | 11 tests passing (`backend/tests/`) |

See `docs/limitations.md` for the honest, current gaps before you present this anywhere.

## Why the model isn't trained yet

This was built in a sandboxed environment that can only reach pypi/npm/github —
**physionet.org is not reachable**, so PTB-XL and MIT-BIH could not be
downloaded here. The training code is real and ready; you need to run it
yourself with network access to PhysioNet. See "Train the model" below.

## Quick start

### 1. Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Health check: `curl http://127.0.0.1:8000/api/health`

### 2. Frontend

Just open `frontend/index.html` in a browser (or serve it with any static
server). It talks to `http://127.0.0.1:8000` by default — override with
`window.ECG_API_BASE` if you deploy the backend elsewhere.

### 3. Try it without a trained model

The pipeline (image quality → layout → trace extraction → filtering →
measurements) works right now without any model — upload any 3×4-layout ECG
image and you'll get real measurements. The API will honestly report
`"model_trained": false` and skip the diagnosis section rather than fake one.

### 4. Train the model

```bash
# 1. Download PTB-XL yourself (physionet.org):
#    https://physionet.org/content/ptb-xl/1.0.1/
#    unzip into ml/data/ptbxl/

pip install -r ml/requirements.txt   # adds wfdb
pip install torch pandas scikit-learn

python -m ml.training.train --ptbxl_root ml/data/ptbxl --epochs 30
```

This saves the **best-validation-F1** checkpoint (not just the final epoch)
to `ml/checkpoints/best_model.pt`. The backend picks it up automatically on
next startup.

### 5. Run tests

```bash
cd backend
pip install pytest
PYTHONPATH=. pytest tests/ -v
```

## Repository layout

```
ecg-ai-interpreter/
├── frontend/               single-page UI, calls the FastAPI backend
├── backend/
│   ├── app/
│   │   ├── main.py         FastAPI app entrypoint
│   │   ├── api/             routes + response schema
│   │   ├── preprocessing/   signal filtering + image quality gate
│   │   ├── extraction/      layout detection, grid removal, trace digitization
│   │   ├── analysis/        R-peak detection, interval measurements
│   │   ├── models/          inference wrapper around the trained checkpoint
│   │   └── reporting/       uncertainty gate + explanation engine
│   └── tests/               11 passing tests against synthetic signals/images
├── ml/
│   ├── preprocessing/       PTB-XL loader (patient-level split)
│   ├── training/            model architecture + training script
│   ├── evaluation/          F1/AUROC/AUPRC/confusion-matrix metrics
│   └── checkpoints/         trained models land here
└── docs/
    ├── architecture.md
    ├── methodology.md       every filter/threshold parameter, declared
    ├── limitations.md
    └── model-card.md        template — fill in once you've actually trained
```

## Safety & privacy

- Every API response carries an explicit "research prototype, not a medical
  diagnostic device" disclaimer.
- Uploaded images are processed in memory for the duration of one request
  and are not written to disk or a database by this codebase.
- The system reports "unable to reliably analyze" (red state) rather than
  forcing a measurement or diagnosis when quality is too low — see
  `backend/app/reporting/quality_gate.py`.
