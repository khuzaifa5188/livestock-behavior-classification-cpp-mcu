"""Verify that the train/test split is balanced per behavior.

This checks both label counts and per-label train/test ratios. It is intended
for the recording-level split produced by split_dataset.py.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parent
TRAIN_FILE = ROOT / "output" / "livestock_behavior_train.csv"
TEST_FILE = ROOT / "output" / "livestock_behavior_test.csv"
TOLERANCE = 5.0


def print_distribution(name: str, frame: pd.DataFrame) -> pd.Series:
    counts = frame["label"].value_counts().sort_index()
    total = len(frame)

    print("=" * 60)
    print(name)
    print("=" * 60)
    for label, count in counts.items():
        percentage = (count / total * 100) if total else 0
        print(f"  {label:20} {count:6} samples ({percentage:5.1f}%)")
    print(f"  {'TOTAL':20} {total:6} samples\n")
    return counts


def main() -> None:
    if not TRAIN_FILE.exists():
        raise FileNotFoundError(f"Missing file: {TRAIN_FILE}")
    if not TEST_FILE.exists():
        raise FileNotFoundError(f"Missing file: {TEST_FILE}")

    train_df = pd.read_csv(TRAIN_FILE)
    test_df = pd.read_csv(TEST_FILE)

    train_counts = print_distribution("TRAINING SET DISTRIBUTION", train_df)
    test_counts = print_distribution("TESTING SET DISTRIBUTION", test_df)

    all_labels = sorted(set(train_counts.index) | set(test_counts.index))

    print("=" * 60)
    print("SPLIT RATIO PER BEHAVIOR")
    print("=" * 60)

    balanced = True
    for label in all_labels:
        train_count = int(train_counts.get(label, 0))
        test_count = int(test_counts.get(label, 0))
        total_count = train_count + test_count
        train_ratio = (train_count / total_count * 100) if total_count else 0
        test_ratio = (test_count / total_count * 100) if total_count else 0

        print(f"  {label:20}")
        print(f"    Train: {train_count:6} ({train_ratio:5.1f}%)")
        print(f"    Test:  {test_count:6} ({test_ratio:5.1f}%)")

        if not (80.0 - TOLERANCE <= train_ratio <= 80.0 + TOLERANCE):
            balanced = False

    print("\n" + "=" * 60)
    print("BALANCE CHECK")
    print("=" * 60)

    if balanced:
        print("  OK All behaviors are within the 80/20 tolerance window.")
    else:
        print("  ERROR One or more behaviors drifted outside the tolerance window.")
        print("  Adjust the split or review the recording counts per label.")


if __name__ == "__main__":
    main()