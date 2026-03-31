"""Controller - контроллер для работы с корпусом."""
import logging
from typing import List, Dict, Any, Optional

from nltk import RegexpParser
from nltk.tree import Tree
import spacy
from spacy import displacy

from corpus import CorpusManager
from analyzers import FrequencyAnalyzer, ConcordanceAnalyzer

logger = logging.getLogger(__name__)


class CorpusController:
    CONSTITUENCY_GRAMMAR = r"""
        ADVP: {<ADV>+}
        ADJP: {<ADV>*<ADJ>+}
        NP: {<DET|NUM|ADJ>*<NOUN|PROPN>+}
            {<PRON>}
        PP: {<ADP><NP>}
        VP: {<AUX|VERB>+<PART>?<ADV>*<NP|PP|ADJP|ADVP>*}
        CLAUSE: {<NP><VP>}
    """
    """
    Контроллер корпусного менеджера.
    Обрабатывает запросы от представления и взаимодействует с моделью.
    """

    def __init__(self):
        self.corpus = CorpusManager()
        self.freq_analyzer = FrequencyAnalyzer(self.corpus)
        self.conc_analyzer = ConcordanceAnalyzer(self.corpus)
        self.nlp = None
        self.constituency_parser = RegexpParser(self.CONSTITUENCY_GRAMMAR)
        self._load_spacy_model()

    def _load_spacy_model(self):
        """Загрузка английской модели spaCy для синтаксического анализа."""
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            logger.error("English spaCy model 'en_core_web_sm' not found. Run: python -m spacy download en_core_web_sm")
            self.nlp = None

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

    def _build_constituency_tree(self, sent_doc) -> Dict[str, Any]:
        """Build a lightweight constituent tree from chunked POS tags."""
        tagged_tokens = []
        for token in sent_doc:
            if token.is_space:
                continue
            tagged_tokens.append((token.text, token.pos_ or "X"))

        if not tagged_tokens:
            return {"label": "S", "children": []}

        parsed_tree = self.constituency_parser.parse(tagged_tokens)
        if not isinstance(parsed_tree, Tree):
            parsed_tree = Tree("S", list(parsed_tree))

        return self._serialize_constituency_node(parsed_tree)

    def _serialize_constituency_node(self, node) -> Dict[str, Any]:
        """Convert an NLTK tree into JSON-friendly data for the frontend."""
        if isinstance(node, Tree):
            return {
                "label": node.label(),
                "children": [self._serialize_constituency_node(child) for child in node],
            }

        word, tag = node
        return {
            "label": tag,
            "text": word,
            "is_leaf": True,
        }

    def analyze_syntax(self, text: str) -> List[Dict[str, Any]]:
        """
        Синтаксический анализ текста с использованием spaCy.
        Возвращает список предложений с данными для визуализации дерева зависимостей.
        """
        if self.nlp is None:
            return []

        doc = self.nlp(text)
        sentences = []

        for sent in doc.sents:
            sent_doc = doc[sent.start:sent.end]
            constituency_tree = self._build_constituency_tree(sent_doc)
            
            # Визуализация дерева зависимостей через displacy
            dependency_html = displacy.render(
                sent_doc,
                style="dep",
                options={"compact": True, "bg": "#fff"},
                jupyter=False,
                page=False
            )
            
            # Данные токенов
            tokens_data = []
            for token in sent_doc:
                token_data = {
                    'text': token.text,
                    'lemma': token.lemma_,
                    'pos': token.pos_,
                    'tag': token.tag_,
                    'dep': token.dep_,
                    'head': token.head.text,
                    'head_idx': token.head.i - sent.start,
                }
                tokens_data.append(token_data)
            
            sentences.append({
                'text': sent.text,
                'tokens': tokens_data,
                'html': dependency_html,
                'dependency_html': dependency_html,
                'constituency_tree': constituency_tree,
            })
        
        return sentences

    def analyze_text_syntax(self, text: str) -> Dict[str, Any]:
        """
        Синтаксический анализ текста.
        Возвращает результаты анализа со всеми предложениями.
        """
        sentences = self.analyze_syntax(text)
        return {
            'sentences': sentences,
            'total_sentences': len(sentences)
        }
