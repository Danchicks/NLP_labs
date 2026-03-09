import re
import os

NUMBER_WORDS = {
    "один": 1, "одна": 1, "одне": 1, "одні": 1,
    "два": 2, "дві": 2, "двоє": 2,
    "три": 3, "троє": 3,
    "чотири": 4, "четверо": 4,
    "п'ять": 5, "п'ятеро": 5,
    "шість": 6, "сім": 7, "вісім": 8, "дев'ять": 9, "десять": 10,
    "кілька": "кілька", "багато": "багато"
}

def load_dictionary(filepath):
    if not os.path.exists(filepath):
        print(f"❌ ПОМИЛКА: Файл словника не знайдено -> {filepath}") # <--- ДОДАЙ ЦЕ
        return []
    with open(filepath, 'r', encoding='utf-8') as f:
        return [line.strip().lower() for line in f if line.strip()]

LOCATIONS = load_dictionary('/Users/danylo/Desktop/coursework/lab4/resources/locations_ua.txt')
COLORS = load_dictionary('/Users/danylo/Desktop/coursework/lab4/resources/colors_ua.txt')

def extract_quantities(text: str) -> list:
    results = []
    
    for match in re.finditer(r'\b\d+\b', text):
        results.append({
            "field_type": "QUANTITY",
            "value": int(match.group()),
            "start_char": match.start(),
            "end_char": match.end(),
            "method": "regex_digits"
        })
        
    word_pattern = r'\b(?:' + '|'.join(NUMBER_WORDS.keys()) + r')\b'
    for match in re.finditer(word_pattern, text.lower()):
        raw_val = match.group()
        results.append({
            "field_type": "QUANTITY",
            "value": NUMBER_WORDS.get(raw_val, raw_val),
            "start_char": match.start(),
            "end_char": match.end(),
            "method": "dict_number_words"
        })
        
    return results

def extract_locations(text: str) -> list:
    results = []
    if not LOCATIONS:
        return results
        
    loc_roots = '|'.join(LOCATIONS)
   
    pattern = r'(?i)\b(в|у|на|біля|по)\s+((?:' + loc_roots + r')[а-яіїєґ]*)\b'
    
    for match in re.finditer(pattern, text):
        results.append({
            "field_type": "LOCATION",
            "value": match.group(2).lower(),
            "start_char": match.start(2),   
            "end_char": match.end(2),
            "method": "regex_prep_dict"
        })
        
    return results

# стара версія 
# def extract_colors(text: str) -> list:
#     results = []
#     if not COLORS:
#         return results
        
#     color_roots = '|'.join(COLORS)
#     pattern = r'(?i)\b((?:' + color_roots + r')[а-яіїєґ]*)\b'
    
#     for match in re.finditer(pattern, text):
#         results.append({
#             "field_type": "COLOR",
#             "value": match.group(1).lower(),
#             "start_char": match.start(),
#             "end_char": match.end(),
#             "method": "dict_colors"
#         })
        
#     return results

# оновлена версія

def extract_colors(text: str) -> list:
    results = []
    if not COLORS:
        return results
        
    color_roots = '|'.join(COLORS)
    pattern = r'(?i)\b((?:' + color_roots + r')[а-яіїєґ]*)\b'
    
    exceptions = {'біля', 'більш', 'більше', 'білок', 'білка', 'синяк'}
    
    for match in re.finditer(pattern, text):
        found_word = match.group(1).lower()
        
        if found_word in exceptions:
            continue
            
        results.append({
            "field_type": "COLOR",
            "value": found_word,
            "start_char": match.start(),
            "end_char": match.end(),
            "method": "dict_colors"
        })
        
    return results

def extract_all(text: str) -> list:
    if not isinstance(text, str):
        return []
    
    all_entities = []
    all_entities.extend(extract_quantities(text))
    all_entities.extend(extract_locations(text))
    all_entities.extend(extract_colors(text))
    
    return sorted(all_entities, key=lambda x: x['start_char'])

if __name__ == "__main__":
    sample = "Дві дівчини у червоних сукнях сидять на траві біля будівлі 5."
    print(f"Приклад: {sample}\n")
    entities = extract_all(sample)
    for ent in entities:
        print(f"[{ent['field_type']}] Значення: '{ent['value']}' | Позиція: {ent['start_char']}-{ent['end_char']} | Метод: {ent['method']}")