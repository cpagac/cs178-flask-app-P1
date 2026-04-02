import pandas as pd
import glob

# Paths to the dataset files
files = sorted(glob.glob('/Users/colemanpagac/.cache/huggingface/hub/datasets--ahmadreza13--human-vs-Ai-generated-dataset/snapshots/93bd3cf72f6ad433207e683ffaba784f11cbfcf2/data/*.parquet'))

# Exact counts requested
target_counts = {
    'GPT4': 50,
    'claude': 50,
    'Claude3-Opus': 50,
    'gemini-1.5-pro': 50,
    'wikipedia': 200
}

all_data = []
for f in files:
    all_data.append(pd.read_parquet(f))

full_df = pd.concat(all_data)

final_samples = []
for model, count in target_counts.items():
    model_df = full_df[full_df['model'] == model]
    if len(model_df) >= count:
        final_samples.append(model_df.sample(count, random_state=42))
    else:
        print(f"Warning: only found {len(model_df)} for {model}")
        final_samples.append(model_df)

final_df = pd.concat(final_samples).sample(frac=1, random_state=42).reset_index(drop=True)

print("Final Counts:")
print(final_df['model'].value_counts())

final_df.to_csv('sampled_turing_data.csv', index=False)
print(f"\nSaved exactly {len(final_df)} rows to 'sampled_turing_data.csv'")
