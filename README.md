# ECG-AI Interpreter

An AI-assisted ECG interpretation system: accepts a 12-lead ECG image, reconstructs the underlying waveform, performs signal-level measurement (HR/PR/QRS/QT/QTc/ST), classifies clinically relevant patterns with a trained multi-label model, explains its findings, and reports its own uncertainty and image quality rather than guessing when it shouldn't.

**Research prototype — not a medical diagnostic device.**

## What makes this different from "send the image to an LLM"

The trained model never sees the image. It only ever sees a reconstructed, filtered, calibrated 12-lead numeric signal — whether that signal came from PTB-XL (during training) or from digitizing an uploaded photo (during inference) is invisible to it. An LLM (Ollama, optional) is used *only* to phrase already-computed findings in plain language, and is explicitly forbidden from introducing any diagnosis it wasn't given.

## Pipeline

See `docs/architecture.md` for the full diagram and `docs/methodology.md` for every declared filter/threshold parameter.

## Results

Trained on **PTB-XL** (PhysioNet), 21,837 real clinical 12-lead ECGs from 18,885 patients, with the official patient-level stratified split (no patient appears in both train and test). Evaluated on the held-out test fold (2,203 ECGs, never seen during training):

| Metric | Value |
|---|---|
| Macro AUROC | **0.9169** |
| Macro AUPRC | 0.8426 |
| Macro F1 | 0.6088 |

| Class | F1 | Precision | Recall | AUROC |
|---|---|---|---|---|
| normal | 0.8388 | 0.7859 | 0.8994 | 0.9293 |
| conduction_abnormality | 0.7527 | 0.7389 | 0.7671 | 0.9175 |
| st_t_abnormality | 0.7197 | 0.6036 | 0.8910 | 0.9302 |
| other_abnormality | 0.7330 | 0.7205 | 0.7459 | 0.8906 |
| atrial_fibrillation | 0.0000 | — | — | n/a |

**Known gap:** `atrial_fibrillation` received zero test examples — PTB-XL encodes AF as a rhythm statement, not a diagnostic superclass, and this build's label mapping only covers diagnostic superclasses. This is a labeling bug, not a model failure; see `docs/model-card.md` for the full writeup.

## Quick start

### Backend
```bash
cd backend
pip install -r requirements.txt
export PYTHONPATH=..          # Windows: set PYTHONPATH=..;%PYTHONPATH%
uvicorn app.main:app --host 127.0.0.1 --port 8000
```
Health check: `curl http://127.0.0.1:8000/api/health`

### Frontend
```bash
cd frontend
python -m http.server 5500
```
Open `http://127.0.0.1:5500` in a browser. It talks to `http://127.0.0.1:8000` by default.

### Train it yourself
```bash
# Download PTB-XL from https://physionet.org/content/ptb-xl/1.0.1/
# and place it under ml/data/ptbxl/ so ptbxl_database.csv is directly inside.

pip install -r ml/requirements.txt
python -m ml.training.train --ptbxl_root ml/data/ptbxl --epochs 30
python -m ml.evaluation.evaluate --ptbxl_root ml/data/ptbxl --checkpoint ml/checkpoints/best_model.pt
```

### Tests
```bash
cd backend
pytest tests/ -v   # 11 tests, all passing, run against synthetic signals/images
```

## Repository layout

## Safety & privacy

- Every API response carries an explicit "research prototype, not a medical diagnostic device" disclaimer.
- Uploaded images are processed in memory per-request only — never written to disk or a database.
- The system returns "unable to reliably analyze" rather than forcing a measurement when quality is too low.

## Limitations

See `docs/limitations.md` for the full, honest list — including that R-peak detection hasn't yet been validated against MIT-BIH beat annotations, and image calibration currently uses an assumed constant rather than automatic grid-spacing detection.

## License

MIT — see `LICENSE`.
