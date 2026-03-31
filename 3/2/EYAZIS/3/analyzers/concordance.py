"""Concordance Analyzer - анализ конкордансов."""
from typing import List, Dict, Any


class ConcordanceAnalyzer:
    """Анализатор конкордансов (контекстное использование слов)."""
    
    def __init__(self, corpus_manager):
        self.corpus = corpus_manager
    
    def get_concordance(
        self,
        lemma: str,
        window: int = 5,
    ) -> List[Dict[str, Any]]:
        """Получить конкордансы для слова."""
        return self.corpus.get_concordance(lemma, window)
    
    def get_kwic(
        self,
        lemma: str,
        window: int = 3,
    ) -> List[Dict[str, Any]]:
        """
        Keyword in Context (KWIC) - ключевое слово в контексте.
        """
        concordances = self.get_concordance(lemma, window)
        
        kwic_results = []
        for conc in concordances:
            context = conc["context"]
            words = context.split()
            
            keyword_pos = None
            for i, w in enumerate(words):
                if w.lower().strip(".,!?;:\"'()[]") == lemma.lower():
                    keyword_pos = i
                    break
            
            if keyword_pos is not None:
                left = " ".join(words[:keyword_pos])
                keyword = words[keyword_pos]
                right = " ".join(words[keyword_pos + 1:])
                
                kwic_results.append({
                    "left": left,
                    "keyword": keyword,
                    "right": right,
                    "text_id": conc["text_id"],
                    "text_title": conc["text_title"],
                })
        
        return kwic_results
    
    def get_collocations_in_context(
        self,
        lemma: str,
        window: int = 3,
    ) -> Dict[str, int]:
        """
        Получить слова, часто встречающиеся в контексте с данным словом.
        """
        concordances = self.get_concordance(lemma, window)
        collocates = {}
        
        for conc in concordances:
            words = conc["context"].lower().split()
            target_word = lemma.lower()
            
            for word in words:
                word_clean = word.strip(".,!?;:\"'()[]")
                if word_clean and word_clean != target_word:
                    collocates[word_clean] = collocates.get(word_clean, 0) + 1
        
        sorted_collocates = sorted(
            collocates.items(),
            key=lambda x: x[1],
            reverse=True
        )
        return dict(sorted_collocates[:20])
    
    def search_by_pos(self, pos: str) -> List[Dict[str, Any]]:
        """Поиск слов по части речи."""
        words = self.corpus.db.get_all_words()
        return [
            {
                "word": w.word,
                "lemma": w.lemma,
                "pos": w.pos,
                "frequency": w.frequency,
                "morph_tags": w.morph_tags,
            }
            for w in words
            if w.pos == pos
        ]
