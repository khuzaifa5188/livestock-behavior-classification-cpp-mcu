import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RUM_DIR = ROOT / "Ruminating"
RUM_DIR.mkdir(exist_ok=True)

# We'll extract 50 files, 1000 rows each.
print("Reading accel-01.csv...")
df = pd.read_csv("C:/Users/Saqib Khan/Downloads/accel-01.csv", nrows=50000)

print("Processing...")
df = df.rename(columns={
    "timestamp": "Time",
    "x": "BNO055_AX",
    "y": "BNO055_AY",
    "z": "BNO055_AZ"
})

for i in range(50):
    start = i * 1000
    end = (i + 1) * 1000
    chunk = df.iloc[start:end]
    filename = RUM_DIR / f"{i+1:02d}_Ruminating.csv"
    chunk.to_csv(filename, index=False)

print("Created 50 files in Ruminating folder.")
