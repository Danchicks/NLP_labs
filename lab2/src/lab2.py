import os
import re
import json
import unicodedata
import pandas as pd


def clean_text(text: str) -> str:
    if not isinstance(text, str): return ""
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'\s+([.,!?])', r'\1', text) 
    text = re.sub(r'^"+|"+$', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def normalize_text(text: str) -> str:
    if not text: return ""
    text = re.sub(r"[ʼ’‘`´]", "'", text)
    text = re.sub(r"[–—−]", "-", text)
    text = re.sub(r"[«»“”]", '"', text)
    return unicodedata.normalize('NFC', text)

def capitalize_text(text: str) -> str:
    if not text: return ""
    return re.sub(
        r'(^|[.!?]\s+)([а-яіїєґa-z])', 
        lambda m: m.group(1) + m.group(2).upper(), 
        text
    )

def mask_pii(text: str) -> str:
    if not text: return ""
    text = re.sub(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', '<EMAIL>', text)
    text = re.sub(r'https?://\S+|www\.\S+', '<URL>', text)
    text = re.sub(r'(\+?38)?\s?\(?0\d{2}\)?[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}', '<PHONE>', text)
    return text

def sentence_split(text: str) -> list[str]:
    if not text: return []
    protected_abbrs = [r'\bм\.', r'\bвул\.', r'\bр\.', r'\bт\.д\.', r'\bт\.п\.', r'\bгрн\.']
    
    for abbr in protected_abbrs:
        text = re.sub(abbr, lambda m: m.group(0).replace('.', '<DOT>'), text)
    text = re.sub(r'(\d)\.(\d)', r'\1<DOT>\2', text)
    
    sentences = re.split(r'(?<=[.!?])\s+(?=[А-ЯІЇЄҐA-Z])', text)
    return [s.replace('<DOT>', '.') for s in sentences]

def preprocess(text: str) -> dict:
    clean = capitalize_text(mask_pii(normalize_text(clean_text(text))))
    sentences = sentence_split(clean)
    return {"clean": clean, "sentences": sentences}


def setup_edge_cases(input_csv: str, output_jsonl: str):
    df = pd.read_csv(input_csv)
    edge_cases = []
    seen_texts = set()

    rules = [
        (r'\s+[.,!?]', "Видалити відірвану пунктуацію (пробіл перед знаком)"),
        (r'^".*"$', "Видалити зовнішні подвійні лапки"),
        (r'[«»“”]', "Звести типографські лапки до стандартних ASCII"),
        (r'\d+\.\d+', "Не розбивати речення на десятковому дробі"),
        (r'\b(м\.|вул\.|р\.|грн\.|ім\.)', "Не розбивати речення на абревіатурах"),
        (r'\s+[-–—−]\s+', "Нормалізувати тире між словами"),
        (r'\w+[-–—−]\w+', "Нормалізувати дефіси всередині слів"),
        (r'\b\d+\b', "Коректний sentence split (не розривати на цифрах)"),
        (r'(^|[.!?]\s+)[а-яіїєґa-z]', "Капіталізувати першу літеру речення")
    ]

    MAX_PER_RULE = 5
    rule_counts = {expected: 0 for _, expected in rules}

    texts = pd.concat([df['premise_clean'], df['hypothesis_clean']]).dropna().astype(str).tolist()

    case_id = 1
    for text in texts:
        if len(edge_cases) >= 20: 
            break 
        if text in seen_texts:
            continue

        for pattern, expected in rules:
            if rule_counts[expected] >= MAX_PER_RULE:
                continue 
            
            if re.search(pattern, text):
                edge_cases.append({
                    "id": f"real_edge_{case_id:02d}",
                    "raw_text": text,
                    "expected_behavior": expected
                })
                seen_texts.add(text)
                rule_counts[expected] += 1
                case_id += 1
                break 

    os.makedirs(os.path.dirname(output_jsonl), exist_ok=True)
    with open(output_jsonl, 'w', encoding='utf-8') as f:
        for case in edge_cases:
            f.write(json.dumps(case, ensure_ascii=False) + '\n')



def print_pipeline_stats(df):
    cols = ['premise_clean', 'hypothesis_clean']
    total_stats = {
        'Відірвана пунктуація (пробіли перед крапками/комами)': 0,
        'Зайві зовнішні лапки (CSV артефакти)': 0,
        'Нетипові апострофи (ʼ’‘`´)': 0,
        'Типографські тире (–—−)': 0,
        'Множинні пробіли': 0,
        'Речення з малої літери (буде капіталізовано)': 0
    }
    
    for col in cols:
        total_stats['Відірвана пунктуація (пробіли перед крапками/комами)'] += df[col].str.contains(r'\s+[.,!?]', regex=True, na=False).sum()
        total_stats['Зайві зовнішні лапки (CSV артефакти)'] += df[col].str.contains(r'^"+|"+$', regex=True, na=False).sum()
        total_stats['Нетипові апострофи (ʼ’‘`´)'] += df[col].str.contains(r"[ʼ’‘`´]", regex=True, na=False).sum()
        total_stats['Типографські тире (–—−)'] += df[col].str.contains(r"[–—−]", regex=True, na=False).sum()
        total_stats['Множинні пробіли'] += df[col].str.contains(r'\s{2,}', regex=True, na=False).sum()
        total_stats['Речення з малої літери (буде капіталізовано)'] += df[col].str.contains(r'(^|[.!?]\s+)[а-яіїєґa-z]', regex=True, na=False).sum()

    print("\nСтатистика")
    for k, v in total_stats.items():
        print(f"  - {k}: {v} шт.")
    print("-" * 50)

def run_regression_tests():
    print("\n[Regression test]")
    sample = "чоловік готується кидати палку за свою собаку ." 
    step1 = preprocess(sample)['clean']
    step2 = preprocess(step1)['clean']
    assert step1 == "Чоловік готується кидати палку за свою собаку.", "Помилка капіталізації або пунктуації!"
    assert step1 == step2, "Fail: Idempotence"
    print("Success: Idempotence & Capitalization tests passed")

def main():
    RAW_DATA_PATH = '/Users/danylo/Desktop/coursework/lab2/data/processed.csv' 
    PROCESSED_DATA_PATH = '/Users/danylo/Desktop/coursework/lab2/data/processed_v2.csv'
    EDGE_CASES_PATH = '/Users/danylo/Desktop/coursework/lab2/tests/edge_cases.jsonl'   
     
    setup_edge_cases(RAW_DATA_PATH, EDGE_CASES_PATH)
    run_regression_tests()
    
    print("\n[Data processing]")
    try:
        df = pd.read_csv(RAW_DATA_PATH)
        print(f"Завантажено рядків: {len(df)}")
    except FileNotFoundError:
        print(f"Файл {RAW_DATA_PATH} не знайдено")
        return

    print_pipeline_stats(df)

    df['premise_dict'] = df['premise_clean'].apply(lambda x: preprocess(str(x)))
    df['hypothesis_dict'] = df['hypothesis_clean'].apply(lambda x: preprocess(str(x)))
    df['premise_v2'] = df['premise_dict'].apply(lambda x: x['clean'])
    df['hypothesis_v2'] = df['hypothesis_dict'].apply(lambda x: x['clean'])
    df['premise_sentences'] = df['premise_dict'].apply(lambda x: x['sentences'])
    df['hypothesis_sentences'] = df['hypothesis_dict'].apply(lambda x: x['sentences'])

    empty_premises = df[df['premise_v2'] == ''].shape[0]
    print(f"\nЗнайдено {empty_premises} порожніх premise.")

    empty_hypothesis = df[df['hypothesis_v2'] == ''].shape[0]
    print(f"\nЗнайдено {empty_hypothesis} порожніх hypothesis.")
    
    duplicates_before = df.duplicated(subset=['premise_clean', 'hypothesis_clean']).sum()
    duplicates_after = df.duplicated(subset=['premise_v2', 'hypothesis_v2']).sum()
    print(f"Дублікати ДО: {duplicates_before}")
    print(f"Дублікати ПІСЛЯ нормалізації: {duplicates_after}")

    print("\n[5 Прикладів До/Після ")
    
    mask_quotes = df['premise_clean'].str.contains(r'^"+|"+$', regex=True, na=False) | \
                  df['hypothesis_clean'].str.contains(r'^"+|"+$', regex=True, na=False)
    df_quotes = df[mask_quotes].head(2)
    
    mask_others = ((df['premise_clean'] != df['premise_v2']) | \
                   (df['hypothesis_clean'] != df['hypothesis_v2'])) & ~mask_quotes
    df_others = df[mask_others].head(4)
    
    demo_df = pd.concat([df_quotes, df_others]).head(5)
    if demo_df.empty: demo_df = df.head(5)
    
    for _, row in demo_df.iterrows():
        if re.search(r'^"+|"+$', str(row['premise_clean'])) or (row['premise_clean'] != row['premise_v2']):
            print(f"RAW:   {row['premise_clean']}")
            print(f"CLEAN: {row['premise_v2']}")
        elif row['hypothesis_clean'] != row['hypothesis_v2']:
            print(f"RAW:   {row['hypothesis_clean']}")
            print(f"CLEAN: {row['hypothesis_v2']}")
        print("-" * 50)

    os.makedirs(os.path.dirname(PROCESSED_DATA_PATH), exist_ok=True)
    output_cols = ['premise_v2', 'hypothesis_v2', 'premise_sentences', 'hypothesis_sentences', 'labels', 'label_name']
    df[output_cols].to_csv(PROCESSED_DATA_PATH, index=False)
    print(f"\nДані збережено у {PROCESSED_DATA_PATH}")

if __name__ == "__main__":
    main()