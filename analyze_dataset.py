import pandas as pd
import glob

files = sorted(glob.glob('/Users/colemanpagac/.cache/huggingface/hub/datasets--ahmadreza13--human-vs-Ai-generated-dataset/snapshots/93bd3cf72f6ad433207e683ffaba784f11cbfcf2/data/*.parquet'))
all_models = set()
total_rows = 0

for f in files:
    df = pd.read_parquet(f)
    total_rows += len(df)
    all_models.update(df['model'].unique().tolist())
    print(f"File: {f.split('/')[-1]}")
    print(f"  Rows: {len(df)}")
    print(f"  Generated (1=AI, 0=Human): {df['generated'].value_counts().to_dict()}")
    print(f"  Models present: {df['model'].unique().tolist()}")

print("\n--- Summary ---")
print(f"Total Rows: {total_rows}")
print(f"All Unique Models: {sorted(list(all_models))}")
