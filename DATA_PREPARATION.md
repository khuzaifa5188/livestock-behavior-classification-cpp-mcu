# Data Preparation

## What the Dataset Contains

The repository already contains labeled raw recordings in class folders:

- `Grazing/`
- `Walking/`
- `Resting/`
- `Miscellaneous behaviors/`

Each CSV includes a `Time` column plus BNO055 and MPU9250 sensor readings.

## Columns to Keep

For the first Edge Impulse baseline, keep:

- `Time`
- `BNO055_AX`, `BNO055_AY`, `BNO055_AZ`
- `BNO055_GX`, `BNO055_GY`, `BNO055_GZ`
- `BNO055_MX`, `BNO055_MY`, `BNO055_MZ` if you want to test magnetometer features
- `MPU9250_AX`, `MPU9250_AY`, `MPU9250_AZ`
- `MPU9250_GX`, `MPU9250_GY`, `MPU9250_GZ`
- `MPU9250_MX`, `MPU9250_MY`, `MPU9250_MZ` if you want to compare sensor stacks
- `label`

The script keeps the full raw signal set by default and adds a normalized class label based on the folder name.

## Edge Impulse Recommendation

Start with the full raw signal set, then run a second experiment using only the accelerometer and gyroscope channels. For livestock behavior classification, those motion channels are usually the strongest features.

## Output

The merged file is written to:

```text
output/livestock_behavior_dataset.csv
```

That file is the basis for a leakage-safe split. Run `split_dataset.py` after merging to create:

- `output/livestock_behavior_train.csv`
- `output/livestock_behavior_test.csv`

Upload those two files separately into Edge Impulse.