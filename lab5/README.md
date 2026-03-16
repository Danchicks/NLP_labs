## Lab 5: Data Splitting & Leakage Checks
У цій лабораторній роботі було виконано детерміноване розбиття очищених даних на Train/Val/Test та проведено аудит Data Leakage.

**Ключові деталі:**
* **Стратегія:** `GroupShuffleSplit` (щоб уникнути потрапляння однакових `premise` у різні вибірки).
* **Спліт:** 80% Train, 10% Val, 10% Test (Seed: 1).
* **Перевірки:** Нульові показники точних дублікатів, near-duplicates та group leakage між Train та Test.