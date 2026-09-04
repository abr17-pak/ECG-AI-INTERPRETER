# Limitations

**This is a research prototype, not a medical diagnostic device.** Results are AI-generated and should not be used as a substitute for professional medical interpretation.

## Known, current limitations of this build

1. **No trained model exists yet in this environment.** PhysioNet (physionet.org) is not reachable from the sandbox this was built in, so PTB-XL/MIT-BIH could not be downloaded here. The API correctly reports `model_trained: false` and shows no diagnosis rather than fabricating one — this is intentional, not a bug to route around.
2. **R-peak detection is unvalidated.** The algorithm runs and produces plausible-looking output on synthetic signals, but has not been scored against annotated beat data (e.g. MIT-BIH). Treat all derived intervals (HR, PR, QRS, QT/QTc, rhythm classification) as unverified until that validation is done.
3. **Image calibration is a placeholder.** Pixel-to-millimeter conversion currently uses an assumed constant, not automatic grid-spacing or calibration-pulse detection. Absolute voltage/timing values extracted from photographed ECGs should be treated as rough estimates only.
4. **Layout detection assumes a standard 3×4 grid.** Any ECG image with a different lead layout (rhythm strips, 6×2 layouts, non-standard vendors) will either be misread or rejected — it will not be silently "figured out."
5. **The image-extraction pipeline has not been tested on the "ugly ECG" suite** described in the build plan (rotated, low-light, cropped, noisy, wrong-document images). Build that test suite (Phase 17) before trusting behavior on real-world photographs.
6. **No synthetic-image training data has been generated yet** (Phase 18 — rendering PTB-XL waveforms onto realistic ECG paper images) — this would meaningfully strengthen the image → signal reconstruction step but doesn't exist in this build.
7. **Privacy:** the backend does not persist uploaded images or analysis results by default (in-memory only, per request). No persistence layer exists in this build at all — if you add a "save report" feature, treat it as a new, explicit, separately-reviewed opt-in, not a default.
8. **No fairness or subgroup evaluation** has been performed, and none can be until there's a trained model to evaluate.

## What "done" looks like before treating this as demo-ready
- R-peak detector validated against MIT-BIH beat annotations, with sensitivity/PPV reported.
- A model actually trained on PTB-XL with real (not placeholder) metrics in the model card.
- Grid-spacing/calibration-pulse auto-detection wired in and validated on real photographed ECGs.
- The 10-image robustness test suite (Phase 17) run and documented.
