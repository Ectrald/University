"""Corpus Manager - управление корпусом текстов."""
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

from corpus.models import CorpusDB, TextDocument, CorpusWord
from processors.text_processor import TextProcessor

logger = logging.getLogger(__name__)


class CorpusManager:
    """
    Менеджер корпуса текстов.
    Обеспечивает базовую функциональность работы с корпусом:
    - добавление текстов
    - поиск
    - статистика
    - конкордансы
    """

    def __init__(self, db_path: str = "corpus.db"):
        self.db = CorpusDB(db_path)
        self.processor = TextProcessor()

    def add_text(
        self,
        title: str,
        content: str,
        source_file: Optional[str] = None,
        domain: str = "Animals",
        author: Optional[str] = None,
        genre: Optional[str] = None,
        date_created: Optional[str] = None,
    ) -> TextDocument:
        """Добавляет текст в корпус с морфологической разметкой."""
        logger.debug("Adding text to corpus: %s", title)

        doc = self.db.add_text_document(
            title=title,
            content=content,
            source_file=source_file,
            domain=domain,
            author=author,
            genre=genre,
            date_created=date_created,
        )

        words_data = self.processor.process_text(content)

        for word_info in words_data:
            word = self.db.add_word(
                word=word_info["word"],
                lemma=word_info["lemma"],
                pos=word_info["pos"],
                morph_tags=str(word_info.get("morph", {})),
            )
            self.db.link_word_to_text(doc.id, word.id)

        logger.info("Text added: %s, %d words processed", title, len(words_data))
        return doc

    def add_text_from_file(
        self,
        file_path: str,
        title: Optional[str] = None,
        domain: str = "Animals",
        author: Optional[str] = None,
        genre: Optional[str] = None,
        date_created: Optional[str] = None,
    ) -> TextDocument:
        """Добавляет текст из файла в корпус."""
        from readers.reader_factory import ReaderFactory

        path = Path(file_path)
        reader = ReaderFactory.create_reader(path)
        content = reader.read()

        doc_title = title if title else path.stem
        return self.add_text(
            title=doc_title,
            content=content,
            source_file=str(path),
            domain=domain,
            author=author,
            genre=genre,
            date_created=date_created,
        )
    
    def search(self, query: str) -> List[CorpusWord]:
        """Поиск слов по лемме или словоформе."""
        logger.debug("Searching for: %s", query)
        return self.db.search_words(query)
    
    def get_word_info(self, lemma: str) -> List[CorpusWord]:
        """Получить информацию о слове (все формы)."""
        return self.db.get_word_by_lemma(lemma)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Получить общую статистику корпуса."""
        freq_stats = self.db.get_frequency_stats()
        pos_dist = self.db.get_pos_distribution()
        
        return {
            "total_words": freq_stats["total_words"],
            "unique_words": freq_stats["unique_words"],
            "total_texts": freq_stats["total_texts"],
            "pos_distribution": pos_dist,
        }
    
    def get_concordance(self, lemma: str, window: int = 5) -> List[Dict[str, Any]]:
        """Получить конкордансы для слова."""
        logger.debug("Getting concordance for: %s", lemma)
        return self.db.get_concordance(lemma, window)
    
    def get_all_texts(self) -> List[TextDocument]:
        """Получить все тексты корпуса."""
        return self.db.get_all_texts()
    
    def get_text_by_id(self, text_id: int) -> Optional[TextDocument]:
        """Получить текст по ID."""
        session = self.db.get_session()
        try:
            return session.query(TextDocument).filter_by(id=text_id).first()
        finally:
            session.close()
    
    def delete_text(self, text_id: int) -> bool:
        """Удалить текст из корпуса."""
        logger.debug("Deleting text: %d", text_id)
        return self.db.delete_text(text_id)
    
    def update_text(
        self,
        text_id: int,
        title: Optional[str] = None,
        content: Optional[str] = None,
        domain: Optional[str] = None,
        author: Optional[str] = None,
        genre: Optional[str] = None,
        date_created: Optional[str] = None,
    ) -> Optional[TextDocument]:
        """Обновить текст или его метаданные."""
        old_doc = self.get_text_by_id(text_id)
        if not old_doc:
            return None
            
        if content is not None and content != old_doc.content:
            # Если изменился сам текст, пересоздаем его для обновления разметки
            self.delete_text(text_id)
            return self.add_text(
                title=title if title is not None else old_doc.title,
                content=content,
                source_file=old_doc.source_file,
                domain=domain if domain is not None else old_doc.domain,
                author=author if author is not None else old_doc.author,
                genre=genre if genre is not None else old_doc.genre,
                date_created=date_created if date_created is not None else old_doc.date_created,
            )
        else:
            return self.db.update_text_document(
                text_id, title=title, content=content, domain=domain,
                author=author, genre=genre, date_created=date_created
            )
    
    def clear_corpus(self) -> tuple:
        """Очистить весь корпус."""
        logger.warning("Clearing corpus")
        return self.db.clear_corpus()
    
    def get_texts_by_domain(self, domain: str) -> List[TextDocument]:
        """Получить тексты по домену."""
        return self.db.get_texts_by_domain(domain)
    
    def analyze_text(self, text: str) -> Dict[str, Any]:
        """Анализ текста без сохранения в корпус."""
        word_freq = self.processor.get_word_frequency(text)
        pos_dist = self.processor.get_pos_distribution(text)
        words_detailed = self.processor.extract_words_detailed(text)
        
        return {
            "word_frequency": word_freq,
            "pos_distribution": pos_dist,
            "total_words": len(words_detailed),
            "unique_words": len(word_freq),
            "words_detailed": words_detailed,
        }
