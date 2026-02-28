#!/usr/bin/env python3
"""
Wargame Counter Extractor — geometry only, no colour changes.
Finds counters in a scan, straightens, crops, and resizes to 180×180.

Usage:
    python extract_counters.py counters.png
    python extract_counters.py counters.png --output ./my_counters
    python extract_counters.py counters.png --size 256 --debug
"""

import cv2
import numpy as np
import os
import sys
import argparse
from pathlib import Path


# ── Tunables ──────────────────────────────────────────────────────────────────
MIN_COUNTER_PX   = 80      # minimum side length in pixels to count as a counter
MAX_ASPECT_SKEW  = 0.30    # counters must be within 30% of square
MAX_ROTATION_DEG = 15      # clamp Hough rotation correction to ±15 degrees
OUTPUT_SIZE      = 180     # output square size in pixels
# ──────────────────────────────────────────────────────────────────────────────


def order_points(pts: np.ndarray) -> np.ndarray:
    """Order 4 points as: top-left, top-right, bottom-right, bottom-left."""
    rect = np.zeros((4, 2), dtype=np.float32)
    s    = pts.sum(axis=1)
    diff = np.diff(pts, axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
    return rect


def four_point_warp(image: np.ndarray, pts: np.ndarray, size: int) -> np.ndarray:
    """Perspective-warp the quadrilateral defined by pts to a square."""
    src = order_points(pts)
    dst = np.array([[0, 0], [size-1, 0], [size-1, size-1], [0, size-1]],
                   dtype=np.float32)
    M = cv2.getPerspectiveTransform(src, dst)
    return cv2.warpPerspective(image, M, (size, size),
                               flags=cv2.INTER_LANCZOS4,
                               borderMode=cv2.BORDER_REPLICATE)


def correct_rotation(image: np.ndarray) -> np.ndarray:
    """
    Fine-tune any remaining rotation using Hough line detection.
    Pure geometric operation — pixels are never recoloured.
    """
    gray  = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)
    lines = cv2.HoughLines(edges, 1, np.pi / 180, threshold=60)
    if lines is None:
        return image

    angles = []
    for line in lines:
        rho, theta = line[0]
        angle = np.degrees(theta) - 90
        if abs(angle) < MAX_ROTATION_DEG:
            angles.append(angle)

    if not angles:
        return image

    angle = float(np.median(angles))
    if abs(angle) < 0.5:
        return image

    h, w = image.shape[:2]
    M = cv2.getRotationMatrix2D((w / 2, h / 2), angle, 1.0)
    return cv2.warpAffine(image, M, (w, h),
                          flags=cv2.INTER_LANCZOS4,
                          borderMode=cv2.BORDER_REPLICATE)


def find_counters(image: np.ndarray, debug: bool = False):
    """
    Locate all counters using shadow-robust binarisation (detection only —
    the original image pixels are never touched here).
    Returns list of rotated rects sorted top-left to bottom-right.
    """
    gray    = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Adaptive threshold handles uneven lighting / shadows
    binary = cv2.adaptiveThreshold(blurred, 255,
                                   cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY_INV,
                                   blockSize=51, C=8)

    # Otsu on illumination-normalised image catches what adaptive misses
    bg_blur   = cv2.GaussianBlur(gray, (101, 101), 0)
    corrected = cv2.divide(gray, bg_blur, scale=255)
    _, otsu   = cv2.threshold(corrected, 0, 255,
                              cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    combined = cv2.bitwise_or(binary, otsu)

    k      = cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7))
    closed = cv2.morphologyEx(combined, cv2.MORPH_CLOSE, k, iterations=3)
    opened = cv2.morphologyEx(closed,   cv2.MORPH_OPEN,  k, iterations=2)

    if debug:
        cv2.imwrite("debug_mask.png", opened)
        print("  Saved debug_mask.png")

    contours, _ = cv2.findContours(opened, cv2.RETR_EXTERNAL,
                                   cv2.CHAIN_APPROX_SIMPLE)

    img_area = image.shape[0] * image.shape[1]
    results  = []

    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < MIN_COUNTER_PX ** 2:
            continue
        if area > img_area * 0.8:
            continue

        rect = cv2.minAreaRect(cnt)
        (cx, cy), (w, h), angle = rect
        if w < h:
            w, h = h, w

        if h < MIN_COUNTER_PX:
            continue
        if (w / max(h, 1)) > 1 + MAX_ASPECT_SKEW:
            continue

        results.append(rect)

    results.sort(key=lambda r: (int(r[0][1] / 150), r[0][0]))
    return results


def extract_counter(image: np.ndarray, rect, padding_frac: float = 0.02,
                    size: int = OUTPUT_SIZE) -> np.ndarray:
    """
    Extract one counter via perspective warp + fine rotation correction.
    Absolutely no colour or brightness changes.
    """
    (cx, cy), (w, h), angle = rect
    if w < h:
        w, h = h, w

    side = min(w, h) * (1.0 - padding_frac)
    box  = cv2.boxPoints(((cx, cy), (side, side), angle)).astype(np.float32)

    warped = four_point_warp(image, box, size)
    warped = correct_rotation(warped)
    return warped


def main():
    parser = argparse.ArgumentParser(
        description="Extract wargame counters: straighten, crop, resize only. No colour changes.")
    parser.add_argument("input",  help="Input scan (e.g. counters.png)")
    parser.add_argument("--output", default=None,
                        help="Output directory (default: input filename without extension)")
    parser.add_argument("--size", type=int, default=OUTPUT_SIZE,
                        help=f"Output square size in px (default: {OUTPUT_SIZE})")
    parser.add_argument("--padding", type=float, default=0.02,
                        help="Inset fraction to avoid clipping neighbours (default: 0.02)")
    parser.add_argument("--debug", action="store_true",
                        help="Save debug_mask.png and debug_detections.png")
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"ERROR: '{args.input}' not found.")
        sys.exit(1)

    image = cv2.imread(args.input)
    if image is None:
        print(f"ERROR: could not load '{args.input}'.")
        sys.exit(1)

    print(f"Loaded '{args.input}': {image.shape[1]}x{image.shape[0]} px")
    print("Detecting counters...")

    rects = find_counters(image, debug=args.debug)
    print(f"  Found {len(rects)} counter(s).")

    if not rects:
        print("No counters found. Try --debug to inspect the detection mask.")
        sys.exit(1)

    if args.debug:
        dbg = image.copy()
        for rect in rects:
            box = np.intp(cv2.boxPoints(rect))
            cv2.drawContours(dbg, [box], 0, (0, 255, 0), 3)
        cv2.imwrite("debug_detections.png", dbg)
        print("  Saved debug_detections.png")

    out_dir = Path(args.output) if args.output else Path(Path(args.input).stem)
    out_dir.mkdir(parents=True, exist_ok=True)

    for i, rect in enumerate(rects, start=1):
        counter = extract_counter(image, rect,
                                  padding_frac=args.padding,
                                  size=args.size)
        out_path = out_dir / f"{i:02d}.png"
        cv2.imwrite(str(out_path), counter)
        print(f"  Saved {out_path}")

    print(f"\nDone. {len(rects)} counters -> {out_dir}/")


if __name__ == "__main__":
    main()
