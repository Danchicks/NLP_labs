import pandas as pd
import numpy as np
import json
import os
from sklearn.model_selection import GroupShuffleSplit
from datetime import datetime

def make_splits(df, strategy="group_split", seed=1):

    if 'id' not in df.columns:
        df['id'] = [f"nli_{i}" for i in range(len(df))]
        
    gss = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=seed)
    train_idx, temp_idx = next(gss.split(df, groups=df['premise_v2']))
    
    train_df = df.iloc[train_idx]
    temp_df = df.iloc[temp_idx].reset_index(drop=True)
    
    gss_val_test = GroupShuffleSplit(n_splits=1, test_size=0.5, random_state=seed)
    val_idx, test_idx = next(gss_val_test.split(temp_df, groups=temp_df['premise_v2']))
    
    val_df = temp_df.iloc[val_idx]
    test_df = temp_df.iloc[test_idx]
    
    return {
        "train": train_df,
        "val": val_df,
        "test": test_df
    }

def save_splits(splits_dict, out_dir, manifest_path, seed, strategy):
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(os.path.dirname(manifest_path), exist_ok=True)
    
    sizes = {}
    for split_name, df_split in splits_dict.items():
        file_path = os.path.join(out_dir, f"splits_{split_name}_ids.txt")
        with open(file_path, "w", encoding="utf-8") as f:
            for item in df_split['id'].tolist():
                f.write(f"{item}\n")
        sizes[split_name] = len(df_split)
        
    manifest = {
        "seed": seed,
        "strategy": strategy,
        "group_column": "premise_v2",
        "split_ratios_target": {"train": 0.8, "val": 0.1, "test": 0.1},
        "sizes_actual": sizes,
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=4, ensure_ascii=False)
    print(f"Спліти збережено. {manifest_path}")

if __name__ == "__main__":
    DATA_PATH = "/Users/danylo/Desktop/coursework/lab5/data/processed_v2.csv" 
    OUTPUT_DIR = "/Users/danylo/Desktop/coursework/lab5/data/sample"
    MANIFEST_PATH = "/Users/danylo/Desktop/coursework/lab5/docs/splits_manifest_lab5.json"
    
    df = pd.read_csv(DATA_PATH)
    
    splits = make_splits(df, strategy="group_split", seed=1)
    save_splits(splits, OUTPUT_DIR, MANIFEST_PATH, seed=1, strategy="GroupShuffleSplit")