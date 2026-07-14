# Livestock Behavior TinyML

TinyML project for classifying cattle behavior from wearable IMU sensor data with Edge Impulse and an ESP32-S3 MVP.

## Overview

This repository contains labeled time-series CSV recordings for cattle behavior classification. The core target classes are:

- Grazing
- Walking
- Resting
- Miscellaneous behaviors

The data was collected from collar-mounted IMUs and includes BNO055 and MPU9250 sensor channels. The repository is structured so it can be used directly for Edge Impulse training, while also leaving room for a future dataset-preparation workflow that can merge public data and farm-collected data.

## Repository Layout

- `Grazing/`, `Walking/`, `Resting/`, `Miscellaneous behaviors/`: labeled source recordings
- `prepare_dataset.py`: merge and normalize the source recordings into a single training CSV
- `split_dataset.py`: create leakage-safe train/test CSVs at the recording level
- `verify_split.py`: confirm each behavior is close to an 80/20 split
- `data/`: optional drop-in location for an Excel source file or other raw inputs
- `output/`: generated CSVs and training exports
- `sample_data/`: small example output for reference
- `edge-impulse/`: Edge Impulse setup notes

## Current Stage Plan

Stage 1 is the ESP32-S3 MVP:

1. Collect and organize IMU data.
2. Prepare a clean labeled CSV for Edge Impulse.
3. Train and validate the first model.
4. Export the model to on-device inference firmware.

Stage 2 is a later low-power hardware upgrade using a custom PCB and different sensors for long-term deployment.

## Quick Start

1. Install Python 3.9 or newer.
2. Install dependencies with `pip install -r requirements.txt`.
3. Run `python prepare_dataset.py`.
4. Run `python split_dataset.py`.
5. Run `python verify_split.py`.
6. Upload the generated training and testing files from `output/` to Edge Impulse.

## Data Notes

The source recordings already contain raw time-series sensor channels. A typical file includes:

- `Time`
- BNO055 acceleration, angular rate, magnetometer, and quaternion channels
- MPU9250 acceleration, angular rate, and magnetometer channels

For behavior classification, accelerometer and gyroscope channels are the most useful features. Magnetometer and quaternion channels can be retained for experiments or removed if the model performs better without them.

## License

See the upstream project license and data-use constraints before redistributing the recordings.
