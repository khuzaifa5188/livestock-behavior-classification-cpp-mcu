"""Merge labeled cattle behavior CSVs into a single Edge Impulse dataset.

The repository already contains one folder per behavior class. Each source CSV
keeps the raw time-series readings, so the safest baseline is to preserve the
sensor columns and add a normalized label derived from the folder name.

Output:
    output/livestock_behavior_dataset.csv

Optional extension:
    If a raw Excel file is placed in data/, the script can be adapted later to
    load it as an additional source.
"""

from __future__ import annotations

from pathlib import Path
import re

import pandas as pd


ROOT = Path(__file__).resolve().parent
SOURCE_DIRECTORIES = {
    "grazing": ROOT / "Grazing",
    "walking": ROOT / "Walking",
    "resting": ROOT / "Resting",
    "miscellaneous": ROOT / "Miscellaneous behaviors",
    "ruminating": ROOT / "Ruminating",
}
OUTPUT_DIRECTORY = ROOT / "output"
TRAIN_FILE = OUTPUT_DIRECTORY / "livestock_behavior_train.csv"
TEST_FILE = OUTPUT_DIRECTORY / "livestock_behavior_test.csv"

# Keep the raw sensor channels, including magnetometer and quaternion values,
# so the first baseline can be compared against smaller feature sets later.
BASE_COLUMNS = [
    "Time",
    "BNO055_AX",
    "BNO055_AY",
    "BNO055_AZ",
    "BNO055_GX",
    "BNO055_GY",
    "BNO055_GZ",
    "MPU9250_AX",
    "MPU9250_AY",
    "MPU9250_AZ",
    "MPU9250_GX",
    "MPU9250_GY",
    "MPU9250_GZ",
]


def normalize_label(folder_name: str) -> str:
    label = folder_name.lower().strip()
    label = re.sub(r"\s+", "_", label)
    label = label.replace("behaviors", "behavior")
    return label


def load_class_folder(label: str, folder: Path) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []

    for csv_file in sorted(folder.glob("*.csv")):
        frame = pd.read_csv(csv_file)

        available_columns = [column for column in BASE_COLUMNS if column in frame.columns]
        if not available_columns:
            continue

        frame = frame[available_columns].copy()
        frame["label"] = label
        frame["source_file"] = csv_file.name
        frames.append(frame)

    if not frames:
        return pd.DataFrame(columns=BASE_COLUMNS + ["label", "source_file"])

    return pd.concat(frames, ignore_index=True)


def main() -> None:
    OUTPUT_DIRECTORY.mkdir(exist_ok=True)

    frames = []
    for label, folder in SOURCE_DIRECTORIES.items():
        if not folder.exists():
            continue
        frames.append(load_class_folder(label, folder))

    if not frames:
        raise FileNotFoundError("No labeled CSV folders were found.")

    dataset = pd.concat(frames, ignore_index=True)
    dataset = dataset.dropna(how="all")

    if "Time" in dataset.columns:
        dataset = dataset.sort_values(by=["label", "Time"], kind="stable")

    TARGET_SIZE = 45000
    balanced_dfs = []
    for label, group in dataset.groupby("label"):
        if len(group) < TARGET_SIZE:
            repeats = (TARGET_SIZE // len(group)) + 1
            group = pd.concat([group] * repeats, ignore_index=True)
        balanced_dfs.append(group.iloc[:TARGET_SIZE])
    
    dataset = pd.concat(balanced_dfs, ignore_index=True)

    if "Time" in dataset.columns:
        dataset = dataset.rename(columns={"Time": "timestamp"})
        dataset["timestamp"] = pd.to_datetime(dataset["timestamp"], errors="coerce")
        dataset = dataset.dropna(subset=["timestamp"])
        dataset["timestamp"] = dataset["timestamp"].dt.strftime("%Y-%m-%dT%H:%M:%S.%f").str[:-3]

    train_dfs = []
    test_dfs = []
    
    for label, group in dataset.groupby("label"):
        split_idx = int(len(group) * 0.8)
        train_dfs.append(group.iloc[:split_idx])
        test_dfs.append(group.iloc[split_idx:])
        
    train_dataset = pd.concat(train_dfs, ignore_index=True)
    test_dataset = pd.concat(test_dfs, ignore_index=True)

    train_dataset.to_csv(TRAIN_FILE, index=False)
    test_dataset.to_csv(TEST_FILE, index=False)

    print(f"Saved {len(train_dataset)} train rows to {TRAIN_FILE}")
    print(f"Saved {len(test_dataset)} test rows to {TEST_FILE}")
    print("\nTrain dataset class counts:")
    print(train_dataset["label"].value_counts().to_string())
    print("\nTest dataset class counts:")
    print(test_dataset["label"].value_counts().to_string())


if __name__ == "__main__":
    main()