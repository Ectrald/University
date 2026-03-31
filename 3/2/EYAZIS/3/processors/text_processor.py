"""Модуль для обработки текста и морфологического анализа (расширенный)."""
import spacy
from typing import List, Tuple, Dict, Any, Optional
from collections import Counter

try:
    nlp = spacy.load("en_core_web_sm")
except (OSError, IOError):
    nlp = None


class TextProcessor:
    """Класс для обработки текста и морфологического анализа."""
    
    def __init__(self, language: str = 'en'):
        self.language = language
        self.nlp = nlp
        if not self.nlp:
            raise RuntimeError("spaCy model not loaded")
    
    def process_text(self, text: str) -> List[Dict[str, Any]]:
        """
        Полный морфологический анализ текста.
        Возвращает список слов с морфологическими характеристиками.
        """
        doc = self.nlp(text)
        results = []
        
        for token in doc:
            if token.is_punct or token.is_space:
                continue
            
            morph_info = {
                "word": token.text,
                "lemma": token.lemma_.lower(),
                "pos": token.pos_,
                "tag": token.tag_,
                "dep": token.dep_,
                "is_stop": token.is_stop,
            }
            
            if token.morph:
                morph_dict = token.morph.to_dict()
                morph_info["morph"] = morph_dict
            
            results.append(morph_info)
        
        return results
    
    def extract_words(self, text: str) -> List[Tuple[str, str]]:
        """Извлекает слова (лемма, POS)."""
        doc = self.nlp(text)
        words = []
        for token in doc:
            if not token.is_stop and not token.is_punct and not token.is_space:
                lemma = token.lemma_.lower()
                pos = token.pos_
                words.append((lemma, pos))
        return words
    
    def extract_words_detailed(self, text: str) -> List[Dict[str, Any]]:
        """Извлекает слова с детальной морфологической информацией."""
        return self.process_text(text)
        
    def extract_collocations(self, text: str) -> List[Tuple[str, int]]:
        """Извлекает словосочетания."""
        doc = self.nlp(text)
        phrases = []

        target_deps = {"amod", "compound", "dobj", "nsubj", "advmod", "acomp", "prep", "prt"}

        for token in doc:
            if token.is_punct or token.is_space:
                continue

            for child in token.children:
                if child.dep_ not in target_deps:
                    continue

                if child.dep_ not in ['prep', 'prt'] and (child.is_stop or child.is_punct):
                    continue

                w1, w2 = sorted([token, child], key=lambda t: t.i)
                phrase = f"{w1.lemma_.lower()} {w2.lemma_.lower()}"
                phrases.append(phrase)

        counts = Counter(phrases)
        return [(phrase, count) for phrase, count in counts.items()]
    
    def get_sentences(self, text: str) -> List[str]:
        """Разбивает текст на предложения."""
        doc = self.nlp(text)
        return [sent.text.strip() for sent in doc.sents]
    
    def get_word_frequency(self, text: str) -> Dict[str, int]:
        """Возвращает частоту слов в тексте."""
        doc = self.nlp(text)
        words = []
        for token in doc:
            if not token.is_punct and not token.is_space:
                words.append(token.lemma_.lower())
        return dict(Counter(words))
    
    def get_pos_distribution(self, text: str) -> Dict[str, int]:
        """Возвращает распределение частей речи."""
        doc = self.nlp(text)
        pos_list = []
        for token in doc:
            if not token.is_punct and not token.is_space:
                pos_list.append(token.pos_)
        return dict(Counter(pos_list))
    
    def lemmatize(self, word: str) -> str:
        """Лемматизирует одно слово."""
        doc = self.nlp(word)
        if doc:
            return doc[0].lemma_.lower()
        return word.lower()
    
    def get_morph_info(self, word: str) -> Dict[str, Any]:
        """Получить морфологическую информацию о слове."""
        doc = self.nlp(word)
        if not doc:
            return {}
        
        token = doc[0]
        return {
            "word": token.text,
            "lemma": token.lemma_.lower(),
            "pos": token.pos_,
            "tag": token.tag_,
            "morph": token.morph.to_dict() if token.morph else {},
        }
