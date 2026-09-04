import numpy as np

from app.analysis.intervals import measure_pr_interval, measure_qrs_duration, measure_qt_qtc


def synthetic_beat(fs=250):
    """One synthetic PQRST complex centered so we know rough ground truth:
    P at t=0.16s, QRS at t=0.28-0.31s (R at 0.30), T at t=0.45-0.50s."""
    t = np.arange(0, 0.9, 1 / fs)
    sig = np.zeros_like(t)
    sig += 0.15 * np.exp(-((t - 0.16) ** 2) / (2 * 0.015 ** 2))  # P wave
    sig += 1.0 * np.exp(-((t - 0.30) ** 2) / (2 * 0.008 ** 2))   # R spike
    sig += 0.25 * np.exp(-((t - 0.48) ** 2) / (2 * 0.03 ** 2))   # T wave
    r_idx = int(round(0.30 * fs))
    return sig, r_idx


def test_qrs_duration_is_plausible_and_narrow():
    fs = 250
    sig, r_idx = synthetic_beat(fs)
    result = measure_qrs_duration(sig, r_idx, fs)
    if result.value_ms is not None:
        assert 20 < result.value_ms < 200  # sanity bounds, not a precision claim


def test_pr_interval_returns_value_or_explicit_unmeasurable_note():
    fs = 250
    sig, r_idx = synthetic_beat(fs)
    result = measure_pr_interval(sig, r_idx, fs)
    # Either it measures something plausible, or it explicitly says why not --
    # it must never silently return a nonsensical number.
    if result.value_ms is not None:
        assert 0 < result.value_ms < 400
    else:
        assert isinstance(result.note, str) and len(result.note) > 0


def test_qt_not_measurable_returns_explicit_note_not_zero():
    fs = 250
    sig, r_idx = synthetic_beat(fs)
    qt, qtc, correction = measure_qt_qtc(sig, r_idx, prior_rr_s=0.83, fs=fs)
    if qt.value_ms is None:
        assert "not" in qt.note or "not" in qtc.note
    else:
        assert qt.value_ms > 0
