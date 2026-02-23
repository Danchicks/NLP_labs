import pandas as pd
import re
from datasets import load_dataset
import matplotlib.pyplot as plt

ds = load_dataset("ukr-detect/ukr-nli-dataset-translated-stanford", split="train")

df = ds.to_pandas()

df_subset = df.sample(n=2000).reset_index(drop=True)

df_subset.to_csv('/Users/danylo/Desktop/coursework/lab1/data/raw.csv', index=False)
print(f"Raw data saved. Shape: {df_subset.shape}")

print(df_subset.head(10))

print(f"Всього рядків: {len(df_subset)}")

label_map = {0: 'entailment', 1: 'neutral', 2: 'contradiction'}
df_subset['label_name'] = df_subset['labels'].map(label_map)

# Розподіл класів
print("\nРозподіл класів:")
print(df_subset['label_name'].value_counts())
df_subset['label_name'].value_counts().plot(kind='bar', title='Class Distribution')
plt.show()

df_subset['total_length'] = df_subset['premise'].astype(str).str.len() + df_subset['hypothesis'].astype(str).str.len()
print("\nСтатистика довжини (символи):")
print(df_subset['total_length'].describe())


def clean_text(text):
    if not isinstance(text, str):
        return ""
    
    text = re.sub(r"[’‘`]", "'", text)
    
    text = re.sub(r"\s+", " ", text).strip()
    
    text = re.sub(r"http\S+|www\.\S+", "<URL>", text)
    
    text = re.sub(r"\S+@\S+\.\S+", "<EMAIL>", text)

    text = re.sub(r"\+?\d[\d -]{8,}\d", "<PHONE>", text)
    
    return text


df_subset['premise_clean'] = df_subset['premise'].apply(clean_text)
df_subset['hypothesis_clean'] = df_subset['hypothesis'].apply(clean_text)


duplicates = df_subset.duplicated(subset=['premise_clean', 'hypothesis_clean']).sum()
print(f"\Повний дублікати: {duplicates} ({duplicates/len(df_subset)*100:.2f}%)")

short_texts = df_subset[
    (df_subset['premise_clean'].str.split().str.len() + 
     df_subset['hypothesis_clean'].str.split().str.len()) < 4
]
print(f"<4 слів ): {len(short_texts)}")

empty_rows = df_subset[(df_subset['premise_clean'] == "") | (df_subset['hypothesis_clean'] == "")]
print(f"Порожні рядки: {len(empty_rows)}")

df_processed = df_subset.drop_duplicates(subset=['premise_clean', 'hypothesis_clean'])
df_processed = df_processed[
    (df_processed['premise_clean'].str.len() > 0) & 
    (df_processed['hypothesis_clean'].str.len() > 0)
]

final_cols = ['premise_clean', 'hypothesis_clean', 'labels', 'label_name']
df_processed[final_cols].to_csv('/Users/danylo/Desktop/coursework/lab1/data/processed.csv', index=False)
print(f"\nЗбероеження. Рядки: {len(df_processed)}")

pd.DataFrame(list(label_map.items()), columns=['id', 'name']).to_csv('/Users/danylo/Desktop/coursework/lab1/data/labels.csv', index=False)