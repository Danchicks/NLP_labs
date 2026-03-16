# Audit Summary: Lab 5 (Splits & Leakage)

**Що зроблено:**
* Реалізовано скрипт детермінованого розбиття даних (`src/split.py`) з використанням стратегії `GroupShuffleSplit` (seed=1).
* Сформовано Train (1599 записів), Val (201 запис) та Test (200 записів). Ідентифікатори збережено у `data/sample/splits_*_ids.txt`.
* Згенеровано `splits_manifest_lab5.json`.
* Проведено Sanity Checks і Leakage Checks у Colab ноутбуці.

**Ключові знахідки:**
* **Баланс класів:** Усі три класи (contradiction, neutral, entailment) займають приблизно по 31-37% у кожній з вибірок.
* **Розподіл довжин:** Стабільний. Середня довжина тексту у всіх вибірках становить 95-99 символів.
* **Витоки (Leakage):** Витоків не виявлено. Точних дублікатів — 0, near-duplicates — 0, перетину груп (Group Leakage) — 0.

