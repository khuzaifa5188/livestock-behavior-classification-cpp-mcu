"""Split the merged cattle behavior dataset into train and test sets.

The split is performed at the recording level, separately within each behavior
class, so adjacent IMU samples from the same original CSV stay together and the
label balance stays close to 80/20 for each behavior.

Output:
    output/livestock_behavior_train.csv
    output/livestock_behavior_test.csv
"""

from __future__ import annotations

from pathlib import Path
from collections import defaultdict
import random

import pandas as pd


ROOT = Path(__file__).resolve().parent
INPUT_FILE = ROOT / "output" / "livestock_behavior_dataset.csv"
OUTPUT_DIRECTORY = ROOT / "output"
TRAIN_FILE = OUTPUT_DIRECTORY / "livestock_behavior_train.csv"
TEST_FILE = OUTPUT_DIRECTORY / "livestock_behavior_test.csv"
TEST_RATIO = 0.2
RANDOM_SEED = 42
SEARCH_TRIALS = 400


def choose_split_groups(dataset: pd.DataFrame) -> tuple[set[str], set[str]]:
    if "source_file" not in dataset.columns:
        raise ValueError(
            "The merged dataset must include a source_file column. Run prepare_dataset.py first."
        )

    groups_by_label: dict[str, dict[str, int]] = defaultdict(dict)
    for source_file, label, row_count in (
        dataset.groupby(["source_file", "label"]).size().reset_index(name="row_count").itertuples(index=False)
    ):
        groups_by_label[str(label)][str(source_file)] = int(row_count)

    rng = random.Random(RANDOM_SEED)
    train_groups: set[str] = set()
    test_groups: set[str] = set()

    for label, file_row_counts in groups_by_label.items():
        if len(file_row_counts) <= 1:
            train_groups.update(file_row_counts.keys())
            continue

        files = list(file_row_counts.items())
        total_rows = sum(row_count for _, row_count in files)
        target_test_rows = total_rows * TEST_RATIO
        best_test_selection: set[str] | None = None
        best_score: tuple[float, float, int] | None = None

        for trial in range(SEARCH_TRIALS):
            ordered_files = files[:]
            rng.shuffle(ordered_files)
            test_selection: set[str] = set()
            test_rows = 0

            for file_name, row_count in ordered_files:
                current_distance = abs(test_rows - target_test_rows)
                new_distance = abs((test_rows + row_count) - target_test_rows)

                if not test_selection:
                    if len(ordered_files) > 1:
                        test_selection.add(file_name)
                        test_rows += row_count
                    continue

                if len(test_selection) >= len(ordered_files) - 1:
                    continue

                if new_distance < current_distance:
                    test_selection.add(file_name)
                    test_rows += row_count

            if not test_selection:
                smallest_file = min(files, key=lambda item: item[1])[0]
                test_selection = {smallest_file}
                test_rows = file_row_counts[smallest_file]

            if len(test_selection) == len(files):
                largest_file = max(files, key=lambda item: item[1])[0]
                test_selection.discard(largest_file)
                test_rows -= file_row_counts[largest_file]

            train_selection = set(file_row_counts) - test_selection
            if not train_selection:
                continue

            train_rows = total_rows - test_rows
            score = (
                abs(test_rows - target_test_rows),
                abs(train_rows - total_rows * (1 - TEST_RATIO)),
                len(test_selection),
            )

            if best_score is None or score < best_score:
                best_score = score
                best_test_selection = set(test_selection)

        if best_test_selection is None:
            all_files = sorted(file_row_counts)
            split_index = max(1, min(len(all_files) - 1, round(len(all_files) * TEST_RATIO)))
            best_test_selection = set(all_files[:split_index])

        best_train_selection = set(file_row_counts) - best_test_selection
        train_groups.update(best_train_selection)
        test_groups.update(best_test_selection)

    return train_groups, test_groups


def main() -> None:
    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Missing {INPUT_FILE}. Run prepare_dataset.py before splitting the dataset."
        )

    dataset = pd.read_csv(INPUT_FILE)
    train_groups, test_groups = choose_split_groups(dataset)

    train_df = dataset[dataset["source_file"].isin(train_groups)].copy()
    test_df = dataset[dataset["source_file"].isin(test_groups)].copy()

    train_df = train_df.drop(columns=["source_file"])
    test_df = test_df.drop(columns=["source_file"])

    if "Time" in train_df.columns:
        train_df = train_df.rename(columns={"Time": "timestamp"})
    if "Time" in test_df.columns:
        test_df = test_df.rename(columns={"Time": "timestamp"})

    if "timestamp" in train_df.columns:
        train_df["timestamp"] = pd.to_datetime(train_df["timestamp"], errors="coerce")
        train_df = train_df.dropna(subset=["timestamp"])
        train_df["timestamp"] = train_df["timestamp"].dt.strftime("%Y-%m-%dT%H:%M:%S.%f").str[:-3]

    if "timestamp" in test_df.columns:
        test_df["timestamp"] = pd.to_datetime(test_df["timestamp"], errors="coerce")
        test_df = test_df.dropna(subset=["timestamp"])
        test_df["timestamp"] = test_df["timestamp"].dt.strftime("%Y-%m-%dT%H:%M:%S.%f").str[:-3]

    OUTPUT_DIRECTORY.mkdir(exist_ok=True)
    train_df.to_csv(TRAIN_FILE, index=False)
    test_df.to_csv(TEST_FILE, index=False)

    print(f"Training rows: {len(train_df)} -> {TRAIN_FILE}")
    print(f"Testing rows: {len(test_df)} -> {TEST_FILE}")
    print("Training labels:\n" + train_df["label"].value_counts().to_string())
    print("Testing labels:\n" + test_df["label"].value_counts().to_string())


if __name__ == "__main__":
    main()