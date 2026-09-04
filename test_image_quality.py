import cv2
import numpy as np

from app.preprocessing.image_quality import assess_quality


def make_clear_grid_image(w=800, h=600):
    img = np.full((h, w, 3), 255, dtype=np.uint8)
    for x in range(0, w, 10):
        cv2.line(img, (x, 0), (x, h), (200, 200, 255), 1)
    for y in range(0, h, 10):
        cv2.line(img, (0, y), (w, y), (200, 200, 255), 1)
    # fake trace
    for x in range(w - 1):
        y1 = int(h / 2 + 50 * np.sin(x / 20))
        y2 = int(h / 2 + 50 * np.sin((x + 1) / 20))
        cv2.line(img, (x, y1), (x + 1, y2), (0, 0, 0), 2)
    return img


def make_blank_image(w=800, h=600):
    return np.full((h, w, 3), 250, dtype=np.uint8)


def make_tiny_image():
    return np.full((50, 80, 3), 200, dtype=np.uint8)


def test_clear_image_scores_reasonably_high():
    img = make_clear_grid_image()
    result = assess_quality(img)
    assert result.score >= 40
    assert result.state in ("green", "yellow")


def test_blank_image_flagged_low_quality():
    img = make_blank_image()
    result = assess_quality(img)
    assert result.state in ("yellow", "red")
    assert len(result.reasons) > 0


def test_tiny_image_penalized_for_resolution():
    img = make_tiny_image()
    result = assess_quality(img)
    assert any("resolution" in r for r in result.reasons)
