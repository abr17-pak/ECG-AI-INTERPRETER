# Architecture

```
                 USER UPLOADS ECG IMAGE
                          |
                          v
              +-----------------------+
              | IMAGE QUALITY GATE    |  backend/app/preprocessing/image_quality.py
              +-----------+-----------+
                          |
                          v
              +-----------------------+
              | LEAD LAYOUT DETECTION |  backend/app/extraction/layout.py
              +-----------+-----------+
                          |
                          v
              +-----------------------+
              | GRID REMOVAL +        |  backend/app/extraction/grid_and_trace.py
              | TRACE EXTRACTION      |
              +-----------+-----------+
                          |
                          v
              +-----------------------+
              | CALIBRATION           |  pixels_to_signal() in grid_and_trace.py
              | (px -> ms, px -> mV)  |  (placeholder constant; see docs/methodology.md)
              +-----------+-----------+
                          |
                          v
              +-----------------------+
              | SIGNAL PREPROCESSING  |  backend/app/preprocessing/signal_processing.py
              | (baseline, notch,     |
              |  bandpass, normalize) |
              +-----------+-----------+
                          |
                          v
              +-----------------------+
              | R-PEAK DETECTION +    |  backend/app/analysis/r_peaks.py
              | MEASUREMENT ENGINE    |  backend/app/analysis/intervals.py
              | (HR/PR/QRS/QT/QTc/ST) |  backend/app/analysis/measurement_engine.py
              +-----------+-----------+
                          |
                          v
              +-----------------------+
              | TRAINED ML MODEL      |  backend/app/models/inference.py
              | (multi-label 1D CNN)  |  ml/training/model.py
              +-----------+-----------+
                          |
                          v
              +-----------------------+
              | UNCERTAINTY / QUALITY |  backend/app/reporting/quality_gate.py
              | GATE (green/yellow/   |
              | red)                  |
              +-----------+-----------+
                          |
                          v
              +-----------------------+
              | EXPLANATION ENGINE    |  backend/app/reporting/explanation.py
              | (structured findings  |
              |  + optional Ollama    |
              |  phrasing only)       |
              +-----------+-----------+
                          |
                          v
                  FINAL ECG REPORT
                  (FastAPI JSON -> frontend/index.html)
```

## Why the image and the model are decoupled

The trained model consumes a 12-lead numeric signal, not an image. Whether that
signal came from PTB-XL (for training) or from digitizing an uploaded photo (for
inference) is invisible to the model — the image is only an input *format*. This
means the model's quality is evaluated once, on PTB-XL, independent of how good
the image pipeline is; the two failure modes (bad extraction vs. bad
classification) stay separable and debuggable independently.

## Why Ollama is not the diagnostic brain

`backend/app/reporting/explanation.py` builds a fixed structured JSON payload
(measurements + model probabilities only) and instructs the LLM to phrase it,
explicitly forbidding it from introducing any label not already present in
`model_findings`. If Ollama is unreachable or unconfigured, the system falls
back to a deterministic template — the report never depends on an LLM being
available.
