"""Controller - контроллер для работы с корпусом."""
import logging
from typing import List, Dict, Any, Optional

from corpus import CorpusManager
from analyzers import FrequencyAnalyzer, ConcordanceAnalyzer

logger = logging.getLogger(__name__)


class CorpusController:
    """
    Контроллер корпусного менеджера.
    Обрабатывает запросы от представления и взаимодействует с моделью.
    """

    def __init__(self):
        self.corpus = CorpusManager()
        self.freq_analyzer = FrequencyAnalyzer(self.corpus)
        self.conc_analyzer = ConcordanceAnalyzer(self.corpus)

    def add_text(
        self,
        title: str,
        content: str,
        domain: str = "Animals",
        author: Optional[str] = None,
        genre: Optional[str] = None,
        date_created: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Добавить текст в корпус."""
        try:
            doc = self.corpus.add_text(
                title=title,
                content=content,
                domain=domain,
                author=author,
                genre=genre,
                date_created=date_created,
            )
            return {"success": True, "message": f"Text '{title}' added", "doc_id": doc.id}
        except Exception as e:
            logger.exception("Error adding text")
            return {"success": False, "message": str(e)}

    def add_text_from_file(
        self,
        file_path: str,
        title: Optional[str] = None,
        domain: str = "Animals",
        author: Optional[str] = None,
        genre: Optional[str] = None,
        date_created: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Добавить текст из файла."""
        try:
            doc = self.corpus.add_text_from_file(
                file_path=file_path,
                title=title,
                domain=domain,
                author=author,
                genre=genre,
                date_created=date_created,
            )
            return {"success": True, "message": f"File added: {doc.title}", "doc_id": doc.id}
        except Exception as e:
            logger.exception("Error adding file")
            return {"success": False, "message": str(e)}

    def get_all_texts(self) -> List[Dict[str, Any]]:
        """Получить все тексты корпуса."""
        texts = self.corpus.get_all_texts()
        return [
            {
                "id": t.id,
                "title": t.title,
                "domain": t.domain,
                "author": t.author or "",
                "genre": t.genre or "",
                "date_created": t.date_created or "",
                "word_count": t.word_count,
                "created_at": t.created_at.strftime("%Y-%m-%d %H:%M") if t.created_at else "",
            }
            for t in texts
        ]
    
    def delete_text(self, text_id: int) -> Dict[str, Any]:
        """Удалить текст."""
        try:
            success = self.corpus.delete_text(text_id)
            if success:
                return {"success": True, "message": "Text deleted"}
            return {"success": False, "message": "Text not found"}
        except Exception as e:
            logger.exception("Error deleting text")
            return {"success": False, "message": str(e)}

    def update_text(
        self,
        text_id: int,
        title: Optional[str] = None,
        content: Optional[str] = None,
        domain: Optional[str] = None,
        author: Optional[str] = None,
        genre: Optional[str] = None,
        date_created: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Обновить текст."""
        try:
            doc = self.corpus.update_text(
                text_id, title=title, content=content, domain=domain,
                author=author, genre=genre, date_created=date_created
            )
            if doc:
                return {"success": True, "message": "Text updated", "doc_id": doc.id}
            return {"success": False, "message": "Text not found"}
        except Exception as e:
            logger.exception("Error updating text")
            return {"success": False, "message": str(e)}
    
    def search_words(self, query: str) -> List[Dict[str, Any]]:
        """Поиск слов."""
        words = self.corpus.search(query)
        return [
            {
                "id": w.id,
                "word": w.word,
                "lemma": w.lemma,
                "pos": w.pos,
                "frequency": w.frequency,
                "morph_tags": w.morph_tags,
            }
            for w in words
        ]
    
    def get_word_info(self, lemma: str) -> List[Dict[str, Any]]:
        """Получить информацию о слове."""
        words = self.corpus.get_word_info(lemma)
        return [
            {
                "word": w.word,
                "lemma": w.lemma,
                "pos": w.pos,
                "frequency": w.frequency,
                "morph_tags": w.morph_tags,
            }
            for w in words
        ]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Получить статистику корпуса."""
        return self.corpus.get_statistics()
    
    def get_frequency_data(self, top_n: int = 20) -> Dict[str, Any]:
        """Получить частотные данные."""
        return {
            "top_words": self.freq_analyzer.get_top_words(top_n),
            "top_lemmas": self.freq_analyzer.get_top_lemmas(top_n),
            "pos_frequency": self.freq_analyzer.get_pos_frequency(),
        }
    
    def get_concordance(self, lemma: str, window: int = 5) -> List[Dict[str, Any]]:
        """Получить конкордансы."""
        return self.conc_analyzer.get_concordance(lemma, window)
    
    def get_kwic(self, lemma: str, window: int = 3) -> List[Dict[str, Any]]:
        """Получить KWIC данные."""
        return self.conc_analyzer.get_kwic(lemma, window)
    
    def get_collocates(self, lemma: str, window: int = 3) -> Dict[str, int]:
        """Получить коллокаты (слова в контексте)."""
        return self.conc_analyzer.get_collocations_in_context(lemma, window)
    
    def analyze_text(self, text: str) -> Dict[str, Any]:
        """Анализ текста без сохранения."""
        return self.corpus.analyze_text(text)
    
    def clear_corpus(self) -> Dict[str, Any]:
        """Очистить корпус."""
        try:
            counts = self.corpus.clear_corpus()
            return {"success": True, "message": f"Cleared: {counts[0]} texts, {counts[1]} words"}
        except Exception as e:
            logger.exception("Error clearing corpus")
            return {"success": False, "message": str(e)}
    
    def analyze_word(self, word: str) -> Dict[str, Any]:
        """Анализ отдельного слова (лемматизация, морфология)."""
        from processors.text_processor import TextProcessor
        
        processor = TextProcessor()
        return processor.get_morph_info(word)
