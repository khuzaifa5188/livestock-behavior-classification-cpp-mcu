# Setup Guide

## Prerequisites

- Python 3.9 or newer
- `pip`
- Optional: VS Code

## Install Dependencies

```bash
pip install -r requirements.txt
```

## Prepare the Dataset

Run the script from the repository root:

```bash
python prepare_dataset.py
```

The script scans the labeled behavior folders, normalizes the column names, and writes a merged CSV to `output/livestock_behavior_dataset.csv`.

Then split it by recording so train and test data do not leak across the same source file:

```bash
python split_dataset.py
```

This writes `output/livestock_behavior_train.csv` and `output/livestock_behavior_test.csv`.

Verify the balance before uploading:

```bash
python verify_split.py
```

## Use With Edge Impulse

1. Create a new time-series project in Edge Impulse.
2. Upload `output/livestock_behavior_train.csv` as Training.
3. Upload `output/livestock_behavior_test.csv` as Testing.
4. Verify the label distribution with `python verify_split.py`.
5. Choose a window size that matches the behavior duration you want to classify.
6. Train and test the impulse.

## If You Later Add Excel Data

Place the Excel file in `data/` and adapt `prepare_dataset.py` to read it as an additional source. The current script is already organized to support that kind of extension.