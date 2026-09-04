# Methodology

## Signal preprocessing
- Baseline wander removal: cascaded median filters (200ms then 600ms windows, scaled to the signal's sampling rate). Chosen over a naive high-pass filter specifically to avoid distorting ST-segment morphology.
- Mains noise: IIR notch filter at 50 Hz (Q=30). Change `NOTCH_FREQ_HZ` to 60 Hz for US-recorded source ECGs.
- Bandpass: 3rd-order Butterworth, 0.5–40 Hz.
- Normalization: zero-mean, unit-variance per lead.

All parameters are declared as constants in `backend/app/preprocessing/signal_processing.py` — nothing is a hidden magic number.

## R-peak detection
Pan-Tompkins-style: derivative → squaring → 150ms moving-window integration → adaptive multi-pass thresholding (tries 35%, 25%, 15%, 8% of the max integrated value until ≥2 peaks are found) → refinement by snapping to the local raw-signal maximum within ±100ms.

**This has not yet been validated against annotated beat data.** Before trusting it: run it against MIT-BIH beat annotations and report sensitivity / positive predictive value / detection error, per the build plan (Phase 4, Step 14). No such validation numbers exist yet — do not present any until they're actually computed.

## Interval measurements
- PR: P-wave onset (first inflection ~80–220ms before QRS onset with sufficient amplitude) to QRS onset. Returns "not measurable" if no P-wave candidate clears the amplitude threshold.
- QRS: onset-to-offset via local derivative flattening around the R peak.
- QT/QTc: T-wave end estimated via a tangent-method approximation (max downslope point, extrapolated to baseline). QTc uses **Fridericia's correction by default** (less rate-sensitive at extremes than Bazett); the correction formula used is always reported alongside the number.
- ST deviation: measured at J-point + 60ms relative to the PQ-segment isoelectric baseline.

Every measurement function returns `(value_or_None, note)`. A `None` with an explanatory note is a first-class output, not an error state to be hidden.

## Image → waveform extraction
1. Image quality gate (resolution, blur via Laplacian variance, contrast, exposure, edge density) produces a 0–100 score before any extraction is attempted.
2. Layout: currently assumes a standard 3×4 panel grid (I/aVR/V1/V4 … III/aVF/V3/V6) via even image splitting. **This is the declared v1 fallback** — it will misread any non-standard layout. A production version should detect panel boundaries from whitespace/ruling rather than assuming even splits; that requires layout-labeled training images this build does not yet have.
3. Ink isolation: HSV-based (dark OR saturated pixels), grid-line suppression via directional morphological opening (removes long straight horizontal/vertical runs).
4. Column-wise centroid extraction converts the remaining ink mask to a 1D pixel-space trace, with a per-column confidence score based on ink-cluster tightness.
5. Calibration: currently uses an **assumed** pixels-per-mm constant (`ASSUMED_PX_PER_MM` in `backend/app/api/analyze.py`) rather than automatic grid-spacing detection. `backend/app/extraction/layout.py` includes a `detect_grid_spacing` autocorrelation helper as a starting point for real calibration — it is not yet wired into the main pipeline. Until it is, treat absolute mV values from image uploads as approximate.

## What is NOT yet validated
- R-peak detector sensitivity/PPV against ground truth
- Image-extraction accuracy against known waveforms
- The trained classifier's real-world performance (no model has been trained in this environment — PhysioNet is unreachable from this sandbox; see `ml/preprocessing/ptbxl_dataset.py`)

Report these honestly in any demo or writeup. "Not yet measured" is the correct thing to say until it's been measured.
