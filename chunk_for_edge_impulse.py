import pandas as pd
import numpy as np
from pathlib import Path
import os

ROOT = Path(__file__).resolve().parent
TRAIN_FILE = ROOT / "output" / "livestock_behavior_train.csv"
TEST_FILE = ROOT / "output" / "livestock_behavior_test.csv"
OUT_DIR = ROOT / "output" / "edge_impulse_upload"

def chunk_and_save(df, label, num_chunks, split_name):
    if "timestamp" in df.columns:
        df = df.sort_values("timestamp")
    
    chunks = np.array_split(df, num_chunks)
    for i, chunk in enumerate(chunks):
        file_name = f"{label}.{split_name}.{i+1:02d}.csv"
        file_path = OUT_DIR / file_name
        
        # Replace the absolute timestamp with relative milliseconds (0, 100, 200...)
        # to guarantee a perfect 10Hz frequency for Edge Impulse.
        if "timestamp" in chunk.columns:
            chunk = chunk.copy()
            chunk["timestamp"] = np.arange(len(chunk)) * 100
        
        # Drop the 'label' column to make it a pure time-series for Edge Impulse 
        if "label" in chunk.columns:
            chunk = chunk.drop(columns=["label"])
            
        chunk.to_csv(file_path, index=False)
        print(f"Saved {file_name} with {len(chunk)} rows")

def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    
    print("Loading datasets...")
    train_df = pd.read_csv(TRAIN_FILE)
    test_df = pd.read_csv(TEST_FILE)
    
    labels = train_df['label'].unique()
    
    for label in labels:
        print(f"\nProcessing label: {label}")
        
        # Train chunks (16)
        train_sub = train_df[train_df['label'] == label]
        chunk_and_save(train_sub, label, 16, "train")
        
        # Test chunks (4)
        test_sub = test_df[test_df['label'] == label]
        chunk_and_save(test_sub, label, 4, "test")
        
    print(f"\nAll files saved successfully to: {OUT_DIR}")

if __name__ == "__main__":
    main()
