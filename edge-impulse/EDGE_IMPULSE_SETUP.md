# Edge Impulse Setup

## Project Type

Create a time-series classification project.

## Recommended Labels

- `grazing`
- `walking`
- `resting`
- `miscellaneous`

## Suggested Workflow

1. Upload `output/livestock_behavior_dataset.csv`.
2. Confirm the labels imported correctly.
3. Split the dataset by recording, not by individual rows, if possible.
4. Use a time window that matches the behavior rhythm.
5. Train a baseline classifier.
6. Inspect confusion between grazing and resting first, then grazing and walking.

## Feature Experiment

Run one baseline with all channels, then compare it with an accelerometer-plus-gyroscope-only version. If magnetometer and quaternion channels do not help, remove them for a smaller on-device model.

## ESP32-S3 Deployment

After training, export an Arduino or ESP-IDF-compatible library and integrate the inference code into the ESP32-S3 firmware.