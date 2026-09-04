# ECG-AI Interpreter

An AI-assisted ECG interpretation system: accepts a 12-lead ECG image, reconstructs the underlying waveform, performs signal-level measurement (HR/PR/QRS/QT/QTc/ST), classifies clinically relevant patterns with a trained multi-label model, explains its findings, and reports its own uncertainty and image quality rather than guessing when it shouldn't.

**Research prototype — not a medical diagnostic device.**

## What makes this different from "send the image to an LLM"

The trained model never sees the image. It only ever sees a reconstructed, filtered, calibrated 12-lead numeric signal — whether that signal came from PTB-XL (during training) or from digitizing an uploaded photo (during inference) is invisible to it. An LLM (Ollama, optional) is used *only* to phrase already-computed findings in plain language, and is explicitly forbidden from introducing any diagnosis it wasn't given.

## Pipeline
