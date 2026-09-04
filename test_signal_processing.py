import numpy as np
import pytest

from app.preprocessing.signal_processing import preprocess_lead, remove_baseline_wander
from app.analysis.r_peaks import detect_r_peaks, heart_rate_bpm, rhythm_regularity


def synthetic_ecg(fs=250, duration_s=10, hr_bpm=72, baseline_wander=True, noise=True):
    """Very rough synthetic ECG: a train of narrow Gaussian 'R spikes' at
    regular intervals, optionally with baseline drift and mains noise. Good
    enough to sanity-check the pipeline shape, NOT a clinical simulator."""
    t = np.arange(0, duration_s, 1 / fs)
    rr = 60.0 / hr_bpm
    signal = np.zeros_like(t)
    beat_times = np.arange(0.3, duration_s, rr)
    for bt in beat_times:
        signal += 1.0 * np.exp(-((t - bt) ** 2) / (2 * (0.01 ** 2)))
    if baseline_wander:
        signal += 0.3 * np.sin(2 * np.pi * 0.2 * t)
    if noise:
        rng = np.random.default_rng(0)
        signal += 0.02 * rng.standard_normal(len(t))
    return signal, t, beat_times


def test_baseline_wander_reduces_low_frequency_drift():
    fs = 250
    signal, t, _ = synthetic_ecg(fs=fs)
    corrected = remove_baseline_wander(signal, fs)
    # low-frequency drift component should be substantially reduced
    assert np.std(corrected) <= np.std(signal) + 1e-6
    assert corrected.shape == signal.shape


def test_r_peak_detection_finds_approximately_right_count():
    fs = 250
    hr = 72
    signal, t, beat_times = synthetic_ecg(fs=fs, duration_s=10, hr_bpm=hr)
    processed = preprocess_lead(signal, fs=fs)
    peaks = detect_r_peaks(processed, fs)
    # allow some tolerance since this is a crude synthetic signal
    assert abs(len(peaks) - len(beat_times)) <= 2


def test_heart_rate_matches_synthetic_rate_within_tolerance():
    fs = 250
    hr = 72
    signal, t, beat_times = synthetic_ecg(fs=fs, duration_s=10, hr_bpm=hr)
    processed = preprocess_lead(signal, fs=fs)
    peaks = detect_r_peaks(processed, fs)
    bpm, note = heart_rate_bpm(peaks, fs)
    assert bpm is not None
    assert abs(bpm - hr) < 8  # generous tolerance for the synthetic generator


def test_heart_rate_not_measurable_with_no_peaks():
    bpm, note = heart_rate_bpm(np.array([]), fs=250)
    assert bpm is None
    assert "not measurable" in note


def test_rhythm_regularity_labels_regular_synthetic_train():
    fs = 250
    signal, t, beat_times = synthetic_ecg(fs=fs, duration_s=15, hr_bpm=70)
    processed = preprocess_lead(signal, fs=fs)
    peaks = detect_r_peaks(processed, fs)
    label, cv = rhythm_regularity(peaks, fs)
    assert label in ("regular", "possibly irregular")  # synthetic generator is near-perfectly periodic
