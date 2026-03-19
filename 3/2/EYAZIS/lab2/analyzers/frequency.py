"""Frequency Analyzer - анализ частотности."""
from typing import Dict, List, Any
from collections import Counter


class FrequencyAnalyzer:
    """Анализатор частотности слов, лемм и грамматических категорий."""
    
    def __init__(self, corpus_manager):
        self.corpus = corpus_manager
    
    def get_word_form_frequency(self) -> Dict[str, int]:
        """Частотность словоформ."""
        words = self.corpus.db.get_all_words()
        return {w.word: w.frequency for w in words}
    
    def get_lemma_frequency(self) -> Dict[str, int]:
        """Частотность лемм."""
        words = self.corpus.db.get_all_words()
        lemma_freq = {}
        for w in words:
            lemma_freq[w.lemma] = lemma_freq.get(w.lemma, 0) + w.frequency
        return lemma_freq
    
    def get_pos_frequency(self) -> Dict[str, int]:
        """Частотность частей речи."""
        return self.corpus.db.get_pos_distribution()
    
    def get_top_words(self, n: int = 20) -> List[Dict[str, Any]]:
        """Топ-N слов по частоте."""
        words = self.corpus.db.get_all_words()
        top = sorted(words, key=lambda w: w.frequency, reverse=True)[:n]
        return [
            {
                "word": w.word,
                "lemma": w.lemma,
                "pos": w.pos,
                "frequency": w.frequency,
            }
            for w in top
        ]
    
    def get_top_lemmas(self, n: int = 20) -> List[Dict[str, Any]]:
        """Топ-N лемм по частоте."""
        lemma_freq = self.get_lemma_frequency()
        sorted_lemmas = sorted(lemma_freq.items(), key=lambda x: x[1], reverse=True)[:n]
        return [
            {"lemma": lemma, "frequency": freq}
            for lemma, freq in sorted_lemmas
        ]
    
    def get_frequency_by_pos(self) -> Dict[str, Dict[str, int]]:
        """Частотность слов по частям речи."""
        words = self.corpus.db.get_all_words()
        result = {}
        for w in words:
            pos = w.pos or "UNKNOWN"
            if pos not in result:
                result[pos] = {}
            result[pos][w.word] = w.frequency
        return result
    
    def analyze_text(self, text: str) -> Dict[str, Any]:
        """Анализ частотности текста (без сохранения в корпус)."""
        analysis = self.corpus.analyze_text(text)
        
        sorted_freq = sorted(
            analysis["word_frequency"].items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return {
            "total_words": analysis["total_words"],
            "unique_words": analysis["unique_words"],
            "word_frequency": dict(sorted_freq[:50]),
            "pos_distribution": analysis["pos_distribution"],
        }
