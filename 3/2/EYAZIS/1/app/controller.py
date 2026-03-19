"""
Контроллер для управления данными между интерфейсом и базой данных
Реализует бизнес-логику приложения "Английские словосочетания"
"""

import nltk
from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag
from app.database import DictionaryDB, create_connection


class DictionaryController:
    """
    Контроллер для управления операциями со словарём
    Связывает UI (window.py) с БД (database.py)
    """

    def __init__(self, db_connection: DictionaryDB):
        """
        Инициализация контроллера

        Args:
            db_connection: Объект подключения к базе данных
        """
        self.db = db_connection
        
        # Загружаем необходимые данные для NLTK
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')
        
        try:
            nltk.data.find('taggers/averaged_perceptron_tagger')
        except LookupError:
            nltk.download('averaged_perceptron_tagger')

    def get_all_lexemes(self, pos_filter: str = None):
        """
        Получить все лексемы с сортировкой по алфавиту

        Args:
            pos_filter: Фильтр по части речи (опционально)

        Returns:
            Список лексем
        """
        return self.db.get_lexemes_alphabetically(pos_filter)

    def search_words(self, query: str, pos_filter: str = None):
        """
        Поиск слов по шаблону

        Args:
            query: Поисковый запрос
            pos_filter: Фильтр по части речи

        Returns:
            Список найденных слов
        """
        return self.db.search_lexemes(query, pos_filter)

    def get_collocations(self, word: str, pos_code: str = None):
        """
        Получить словосочетания для заданного слова

        Args:
            word: Слово для поиска
            pos_code: Часть речи (опционально)

        Returns:
            Список словосочетаний
        """
        return self.db.get_collocations_for_word(word, pos_code)

    def add_new_word(self, word: str, pos_code: str):
        """
        Добавить новое слово в словарь

        Args:
            word: Слово
            pos_code: Код части речи

        Returns:
            ID добавленной лексемы
        """
        return self.db.add_or_update_lexeme(word, pos_code)

    def add_collocation(self, head_word: str, head_pos: str,
                       collocate_word: str, collocate_pos: str,
                       relation_type: str = None, example: str = None):
        """
        Добавить связь между словами

        Args:
            head_word: Главное слово
            head_pos: Часть речи главного слова
            collocate_word: Зависимое слово
            collocate_pos: Часть речи зависимого слова
            relation_type: Тип связи
            example: Пример использования

        Returns:
            ID добавленного словосочетания
        """
        return self.db.add_collocation(
            head_word, head_pos, collocate_word,
            collocate_pos, relation_type, example
        )

    def delete_word(self, word_id: int):
        """
        Удалить слово из словаря

        Args:
            word_id: ID слова

        Returns:
            True при успешном удалении
        """
        return self.db.delete_lexeme(word_id)

    def get_statistics(self):
        """
        Получить статистику по словарю

        Returns:
            Словарь со статистикой
        """
        return self.db.get_dictionary_stats()

    def synthesize_collocations(self, word: str, pos: str, relation_type: str = None):
        """
        Синтезировать возможные словосочетания

        Args:
            word: Слово
            pos: Часть речи
            relation_type: Желаемый тип связи

        Returns:
            Список предложенных словосочетаний
        """
        return self.db.synthesize_phrase(word, pos, relation_type)
    
    def extract_collocations_from_text(self, text: str, document_id: int = None):
        """
        Извлечение словосочетаний из текста с использованием NLTK
        
        Args:
            text: Текст для анализа
            document_id: ID документа (опционально)
            
        Returns:
            Список извлеченных словосочетаний
        """
        # Используем существующую функцию из базы данных
        return self.db.extract_collocations_from_text(text, document_id)
    
    def _is_valid_collocation(self, pos1: str, pos2: str) -> bool:
        """
        Проверяет, является ли комбинация частей речи потенциальным словосочетанием
        
        Args:
            pos1: Часть речи первого слова
            pos2: Часть речи второго слова
            
        Returns:
            True если это потенциальное словосочетание
        """
        # Основные шаблоны словосочетаний
        valid_patterns = [
            ('JJ', 'NN'),   # прилагательное + существительное
            ('JJ', 'NNS'),  # прилагательное + существительное (мн.ч.)
            ('VB', 'NN'),   # глагол + существительное
            ('VB', 'NNS'),  # глагол + существительное (мн.ч.)
            ('VBD', 'NN'),  # глагол (прошедш.вр.) + существительное
            ('VBD', 'NNS'), # глагол (прошедш.вр.) + существительное (мн.ч.)
            ('VBG', 'NN'),  # герундий + существительное
            ('VBG', 'NNS'), # герундий + существительное (мн.ч.)
            ('VBN', 'NN'),  # причастие прошедш.вр. + существительное
            ('VBN', 'NNS'), # причастие прошедш.вр. + существительное (мн.ч.)
            ('NN', 'VBG'),  # существительное + герундий
            ('NNS', 'VBG'), # существительное (мн.ч.) + герундий
        ]
        
        return (pos1, pos2) in valid_patterns
