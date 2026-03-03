import stanza
import pandas as pd

class TextLinguist:
    def __init__(self):
        stanza.download('uk', processors='tokenize,pos,lemma')
        self.nlp = stanza.Pipeline(lang='uk', processors='tokenize,pos,lemma', use_gpu=False)

    def extract_features(self, text: str) -> dict:
        if not isinstance(text, str) or not text.strip():
            return {"lemma_text": "", "pos_seq": ""}
        
        doc = self.nlp(text)
        lemmas = []
        pos_tags = []
        
        for sentence in doc.sentences:
            for word in sentence.words:
                lemmas.append(word.lemma if word.lemma else word.text)
                pos_tags.append(word.upos if word.upos else "X")
                
        return {
            "lemma_text": " ".join(lemmas),
            "pos_seq": " ".join(pos_tags)
        }

if __name__ == "__main__":
    linguist = TextLinguist()
    sample = "Чоловік готується кидати палку за свою собаку."
    res = linguist.extract_features(sample)
    print(f"RAW: {sample}")
    print(f"LEMMA: {res['lemma_text']}")
    print(f"POS: {res['pos_seq']}")