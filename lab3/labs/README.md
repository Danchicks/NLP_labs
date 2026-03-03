# Lab 3: Lemma/POS Baseline (UA)

**1. Напрям:** А (Класифікація текстів / NLI)
**2. Інструмент для Lemma/POS:** Stanza (українська модель: `tokenize, pos, lemma`)
**3. Бейзлайни:**
   - **Baseline 1:** TF-IDF + Logistic Regression на звичайному очищеному тексті (`processed_v2`).
   - **Baseline 2:** TF-IDF + Logistic Regression на текстах-лемах (`text_lemma`).
   - **Baseline 3:** TF-IDF + Logistic Regression виключно на POS-тегах (`text_pos`).

**4. Основні цифри (до/після):**
   - Baseline 1 (RAW): Accuracy = **0.4225**, Macro-F1 = **0.4225**
   - Baseline 2 (LEMMA): Accuracy = **0.3450**, Macro-F1 = **0.3447**
   - Baseline 3 (POS tags): Accuracy = **0.3375**, Macro-F1 = **0.3354**

**5. Висновок:**
Використання лематизації та POS-тегів як основних ознак для моделі TF-IDF у задачі NLI **недоцільне**. Леми руйнують тонкий контекст, а чисті POS-теги втрачають семантику слів (модель починає просто вгадувати з імовірністю 33%).
**Рішення:** Залишаємо оригінальний очищений текст (`processed_v2`) як найкращий вхідний формат для нашого бейзлайну (дає найкращий скор — 42.25%).