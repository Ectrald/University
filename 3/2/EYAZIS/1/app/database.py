"""
Модуль интеграции с PostgreSQL через psycopg2
Для работы со словарем английских словосочетаний (Задание 3)
"""

import psycopg2
from psycopg2.extras import RealDictCursor, execute_values
from psycopg2 import sql
from typing import List, Dict, Optional, Tuple
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DictionaryDB:
    """
    Класс для работы с базой данных словаря словосочетаний
    """
    
    def __init__(self, dbname: str, user: str, password: str, 
                 host: str = 'localhost', port: int = 5432):
        """
        Инициализация подключения к базе данных
        
        Args:
            dbname: Имя базы данных
            user: Имя пользователя
            password: Пароль
            host: Хост (по умолчанию localhost)
            port: Порт (по умолчанию 5432)
        """
        self.connection_params = {
            'dbname': dbname,
            'user': user,
            'password': password,
            'host': host,
            'port': port
        }
        self.conn = None
        self.connect()
    
    def connect(self):
        """Установить соединение с базой данных"""
        try:
            self.conn = psycopg2.connect(**self.connection_params)
            self.conn.autocommit = False
            logger.info("Successfully connected to database")
        except psycopg2.Error as e:
            logger.error(f"Error connecting to database: {e}")
            raise
    
    def disconnect(self):
        """Закрыть соединение с базой данных"""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")
    
    def __enter__(self):
        """Контекстный менеджер: вход"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Контекстный менеджер: выход"""
        self.disconnect()
        if exc_type:
            self.rollback()
        return False
    
    def commit(self):
        """Подтвердить транзакцию"""
        if self.conn:
            self.conn.commit()
    
    def rollback(self):
        """Откатить транзакцию"""
        if self.conn:
            self.conn.rollback()
    
    # ============================================
    # МЕТОДЫ ДЛЯ РАБОТЫ С ЛЕКСЕМАМИ
    # ============================================
    
    def get_lexemes_alphabetically(self, pos_filter: Optional[str] = None) -> List[Dict]:
        """
        Получить все лексемы, упорядоченные по алфавиту
        
        Args:
            pos_filter: Фильтр по части речи (код, например 'N', 'V')
        
        Returns:
            Список словарей с информацией о лексемах
        """
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.callproc('get_lexemes_alphabetically', [pos_filter])
                results = cur.fetchall()
                return [dict(row) for row in results]
        except psycopg2.Error as e:
            logger.error(f"Error getting lexemes: {e}")
            self.rollback()
            raise
    
    def search_lexemes(self, search_pattern: str, pos_filter: Optional[str] = None, 
                      limit: int = 100) -> List[Dict]:
        """
        Поиск лексем по шаблону
        
        Args:
            search_pattern: Паттерн для поиска (поддерживает частичное совпадение)
            pos_filter: Фильтр по части речи
            limit: Максимальное количество результатов
        
        Returns:
            Список найденных лексем
        """
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.callproc('search_lexemes', [search_pattern, pos_filter, limit])
                results = cur.fetchall()
                return [dict(row) for row in results]
        except psycopg2.Error as e:
            logger.error(f"Error searching lexemes: {e}")
            self.rollback()
            raise
    
    def add_or_update_lexeme(self, word: str, pos_code: str, 
                            increment_frequency: bool = False) -> int:
        """
        Добавить или обновить лексему
        
        Args:
            word: Слово
            pos_code: Код части речи ('N', 'V', 'ADJ', etc.)
            increment_frequency: Увеличить частоту встречаемости
        
        Returns:
            ID лексемы
        """
        try:
            with self.conn.cursor() as cur:
                cur.callproc('add_or_update_lexeme', 
                           [word, pos_code, increment_frequency])
                lexeme_id = cur.fetchone()[0]
                self.commit()
                logger.info(f"Added/updated lexeme: {word} ({pos_code}), ID: {lexeme_id}")
                return lexeme_id
        except psycopg2.Error as e:
            logger.error(f"Error adding lexeme: {e}")
            self.rollback()
            raise
    
    # ============================================
    # МЕТОДЫ ДЛЯ РАБОТЫ СО СЛОВОСОЧЕТАНИЯМИ
    # ============================================
    
    def get_collocations_for_word(self, word: str, 
                                  pos_code: Optional[str] = None) -> List[Dict]:
        """
        Получить словосочетания для заданного слова
        Согласно Заданию 3: "слова, с которыми данное слово может сочетаться"
        
        Args:
            word: Слово для поиска
            pos_code: Код части речи (если слово может быть разных частей речи)
        
        Returns:
            Список словосочетаний
        """
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.callproc('get_collocations_for_word', [word, pos_code])
                results = cur.fetchall()
                return [dict(row) for row in results]
        except psycopg2.Error as e:
            logger.error(f"Error getting collocations: {e}")
            self.rollback()
            raise
    
    def add_collocation(self, head_word: str, head_pos: str,
                       collocate_word: str, collocate_pos: str,
                       relation_type: Optional[str] = None,
                       example_context: Optional[str] = None) -> int:
        """
        Добавить словосочетание
        
        Args:
            head_word: Главное слово
            head_pos: Часть речи главного слова
            collocate_word: Зависимое слово
            collocate_pos: Часть речи зависимого слова
            relation_type: Тип связи (например, 'Verb + Noun')
            example_context: Пример использования
        
        Returns:
            ID словосочетания
        """
        try:
            with self.conn.cursor() as cur:
                cur.callproc('add_collocation', 
                           [head_word, head_pos, collocate_word, 
                            collocate_pos, relation_type, example_context])
                collocation_id = cur.fetchone()[0]
                self.commit()
                logger.info(f"Added collocation: {head_word} + {collocate_word}, ID: {collocation_id}")
                return collocation_id
        except psycopg2.Error as e:
            logger.error(f"Error adding collocation: {e}")
            self.rollback()
            raise
    
    def synthesize_phrase(self, head_word: str, head_pos: str,
                         target_relation_type: Optional[str] = None) -> List[Dict]:
        """
        Синтез словосочетания
        Согласно Заданию 3: "средства синтеза словосочетаний"
        
        Args:
            head_word: Главное слово
            head_pos: Часть речи главного слова
            target_relation_type: Желаемый тип связи (опционально)
        
        Returns:
            Список предложенных словосочетаний с оценкой уверенности
        """
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.callproc('synthesize_phrase', 
                           [head_word, head_pos, target_relation_type])
                results = cur.fetchall()
                return [dict(row) for row in results]
        except psycopg2.Error as e:
            logger.error(f"Error synthesizing phrase: {e}")
            self.rollback()
            raise
    
    def extract_collocations_from_text(self, text_content: str, 
                                       document_id: Optional[int] = None) -> List[Dict]:
        """
        Извлечение типовых словосочетаний из текста
        Согласно Заданию 3: "автоматизированное извлечение из исходных текстов"
        
        Примечание: Базовая версия. Полная реализация требует интеграции с NLP библиотеками.
        
        Args:
            text_content: Текст для обработки
            document_id: ID документа (опционально)
        
        Returns:
            Список извлеченных словосочетаний
        """
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.callproc('extract_collocations_from_text', 
                           [text_content, document_id])
                results = cur.fetchall()
                return [dict(row) for row in results]
        except psycopg2.Error as e:
            logger.error(f"Error extracting collocations: {e}")
            self.rollback()
            raise
    
    # ============================================
    # ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ
    # ============================================
    
    def get_dictionary_stats(self) -> Dict:
        """
        Получить статистику по словарю
        
        Returns:
            Словарь со статистикой
        """
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.callproc('get_dictionary_stats')
                result = cur.fetchone()
                return dict(result) if result else {}
        except psycopg2.Error as e:
            logger.error(f"Error getting stats: {e}")
            self.rollback()
            raise
    
    def get_parts_of_speech(self) -> List[Dict]:
        """
        Получить список всех частей речи
        
        Returns:
            Список частей речи
        """
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT id, code, description FROM parts_of_speech ORDER BY code")
                results = cur.fetchall()
                return [dict(row) for row in results]
        except psycopg2.Error as e:
            logger.error(f"Error getting parts of speech: {e}")
            self.rollback()
            raise
    
    def delete_lexeme(self, lexeme_id: int) -> bool:
        """
        Удалить лексему (и все связанные словосочетания через CASCADE)
        
        Args:
            lexeme_id: ID лексемы
        
        Returns:
            True если успешно удалено
        """
        try:
            with self.conn.cursor() as cur:
                cur.execute("DELETE FROM lexemes WHERE id = %s", (lexeme_id,))
                deleted = cur.rowcount > 0
                self.commit()
                logger.info(f"Deleted lexeme with ID: {lexeme_id}")
                return deleted
        except psycopg2.Error as e:
            logger.error(f"Error deleting lexeme: {e}")
            self.rollback()
            raise
    
    def delete_collocation(self, collocation_id: int) -> bool:
        """
        Удалить словосочетание
        
        Args:
            collocation_id: ID словосочетания
        
        Returns:
            True если успешно удалено
        """
        try:
            with self.conn.cursor() as cur:
                cur.execute("DELETE FROM collocations WHERE id = %s", (collocation_id,))
                deleted = cur.rowcount > 0
                self.commit()
                logger.info(f"Deleted collocation with ID: {collocation_id}")
                return deleted
        except psycopg2.Error as e:
            logger.error(f"Error deleting collocation: {e}")
            self.rollback()
            raise
    
    def batch_add_collocations(self, collocations: List[Tuple]) -> int:
        """
        Пакетное добавление словосочетаний
        
        Args:
            collocations: Список кортежей (head_word, head_pos, collocate_word, 
                         collocate_pos, relation_type, example_context)
        
        Returns:
            Количество добавленных словосочетаний
        """
        count = 0
        try:
            for colloc in collocations:
                self.add_collocation(*colloc)
                count += 1
            return count
        except psycopg2.Error as e:
            logger.error(f"Error in batch add: {e}")
            self.rollback()
            raise


# ============================================
# ФУНКЦИЯ ДЛЯ СОЗДАНИЯ ПОДКЛЮЧЕНИЯ
# ============================================

def create_connection(dbname: str, user: str, password: str, 
                     host: str = 'localhost', port: int = 5432) -> DictionaryDB:
    """
    Создать и вернуть объект подключения к базе данных
    
    Args:
        dbname: Имя базы данных
        user: Имя пользователя
        password: Пароль
        host: Хост
        port: Порт
    
    Returns:
        Объект DictionaryDB
    """
    return DictionaryDB(dbname, user, password, host, port)


# ============================================
# ПРИМЕР ИСПОЛЬЗОВАНИЯ
# ============================================

if __name__ == '__main__':
    # Пример использования
    try:
        # Создать подключение
        db = create_connection(
            dbname='english_dictionary',
            user='postgres',
            password='your_password',
            host='localhost',
            port=5432
        )
        
        # Получить все лексемы по алфавиту
        lexemes = db.get_lexemes_alphabetically()
        print(f"Total lexemes: {len(lexemes)}")
        
        # Добавить новую лексему
        lexeme_id = db.add_or_update_lexeme('decision', 'N')
        print(f"Added lexeme with ID: {lexeme_id}")
        
        # Добавить словосочетание
        colloc_id = db.add_collocation(
            head_word='make',
            head_pos='V',
            collocate_word='decision',
            collocate_pos='N',
            relation_type='Verb + Noun',
            example_context='make a decision'
        )
        print(f"Added collocation with ID: {colloc_id}")
        
        # Получить словосочетания для слова
        collocations = db.get_collocations_for_word('decision')
        print(f"Collocations for 'decision': {len(collocations)}")
        for colloc in collocations:
            print(f"  - {colloc['head_word']} + {colloc['collocate_word']}")
        
        # Синтез словосочетания
        suggestions = db.synthesize_phrase('decision', 'N')
        print(f"Suggestions for 'decision': {len(suggestions)}")
        
        # Статистика
        stats = db.get_dictionary_stats()
        print(f"Dictionary stats: {stats}")
        
        # Закрыть подключение
        db.disconnect()
        
    except Exception as e:
        logger.error(f"Error in example: {e}")
