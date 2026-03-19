"""
Скрипт для инициализации базы данных с тестовыми данными
для приложения "Английские словосочетания"
"""

import psycopg2
from psycopg2 import sql
import config

def initialize_database():
    """
    Создает структуру базы данных и добавляет тестовые данные
    """
    # Подключение к PostgreSQL (без указания имени базы данных)
    conn = psycopg2.connect(
        host=config.DATABASE_CONFIG['host'],
        port=config.DATABASE_CONFIG['port'],
        user=config.DATABASE_CONFIG['user'],
        password=config.DATABASE_CONFIG['password']
    )
    
    conn.autocommit = True
    cursor = conn.cursor()
    
    # Создание базы данных, если она не существует
    try:
        cursor.execute(sql.SQL("CREATE DATABASE {}").format(
            sql.Identifier(config.DATABASE_CONFIG['dbname'])
        ))
        print(f"База данных {config.DATABASE_CONFIG['dbname']} создана")
    except psycopg2.errors.DuplicateDatabase:
        print(f"База данных {config.DATABASE_CONFIG['dbname']} уже существует")
    
    cursor.close()
    conn.close()
    
    # Подключение к созданной базе данных
    conn = psycopg2.connect(**config.DATABASE_CONFIG)
    cursor = conn.cursor()
    
    # Создание таблиц и функций (из файла database.sql)
    schema_sql = """
    -- 1. Справочник частей речи (для нормализации)
    CREATE TABLE IF NOT EXISTS parts_of_speech (
        id SERIAL PRIMARY KEY,
        code VARCHAR(10) UNIQUE NOT NULL, -- Например: N, V, ADJ
        description VARCHAR(50) -- Например: Noun, Verb
    );

    -- Заполним базовыми английскими частями речи
    INSERT INTO parts_of_speech (code, description) VALUES
    ('N', 'Noun'),
    ('V', 'Verb'),
    ('ADJ', 'Adjective'),
    ('ADV', 'Adverb'),
    ('PREP', 'Preposition')
    ON CONFLICT (code) DO NOTHING;

    -- 2. Таблица лексем (Словарь)
    -- Согласно заданию: список слов, упорядоченный по алфавиту [cite: 39]
    CREATE TABLE IF NOT EXISTS lexemes (
        id SERIAL PRIMARY KEY,
        word VARCHAR(100) NOT NULL, -- Сама лексема
        pos_id INT REFERENCES parts_of_speech(id), -- Ссылка на часть речи
        frequency INT DEFAULT 0, -- Общая частота встречаемости (для задания 1 и статистики)
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

        -- Уникальность пары "слово + часть речи" (чтобы различать 'mail' как сущ. и глагол)
        CONSTRAINT unique_lexeme UNIQUE (word, pos_id)
    );

    -- 3. Таблица документов (Источники)
    -- Для хранения информации о PDF файлах
    CREATE TABLE IF NOT EXISTS documents (
        id SERIAL PRIMARY KEY,
        filename VARCHAR(255) NOT NULL,
        upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        content_hash VARCHAR(64) -- Для предотвращения повторной загрузки одного и того же файла
    );

    -- 4. Таблица словосочетаний (Связи)
    -- Самая важная часть для Задания 3: "записи... с которыми данное слово может сочетаться"
    CREATE TABLE IF NOT EXISTS collocations (
        id SERIAL PRIMARY KEY,
        head_lexeme_id INT REFERENCES lexemes(id) ON DELETE CASCADE, -- Главное слово (напр. decision)
        collocate_lexeme_id INT REFERENCES lexemes(id) ON DELETE CASCADE, -- Зависимое слово (напр. make)

        -- Тип связи (например, 'Verb + Noun' или 'Adj + Noun')
        relation_type VARCHAR(50),

        -- Пример использования (контекст)
        example_context TEXT,

        -- Частота совместной встречаемости
        co_occurrence_count INT DEFAULT 1,

        -- Ограничение: такая связь должна быть уникальной
        CONSTRAINT unique_collocation UNIQUE (head_lexeme_id, collocate_lexeme_id, relation_type)
    );

    -- Индексы для ускорения поиска (важно для "поиска по заданному условию" [cite: 20])
    CREATE INDEX IF NOT EXISTS idx_lexeme_word ON lexemes(word);
    CREATE INDEX IF NOT EXISTS idx_collocation_head ON collocations(head_lexeme_id);
    CREATE INDEX IF NOT EXISTS idx_collocation_collocate ON collocations(collocate_lexeme_id);

    -- ============================================
    -- SQL ФУНКЦИИ ДЛЯ РАБОТЫ СО СЛОВОСОЧЕТАНИЯМИ
    -- ============================================

    -- Функция 1: Получить все лексемы, упорядоченные по алфавиту
    -- Согласно Заданию 3: "список слов, упорядоченный по алфавиту"
    CREATE OR REPLACE FUNCTION get_lexemes_alphabetically(
        pos_filter VARCHAR DEFAULT NULL
    )
    RETURNS TABLE (
        id INT,
        word VARCHAR,
        pos_code VARCHAR,
        pos_description VARCHAR,
        frequency INT,
        collocations_count BIGINT
    ) AS $$
    BEGIN
        RETURN QUERY
        SELECT
            l.id,
            l.word,
            p.code AS pos_code,
            p.description AS pos_description,
            l.frequency,
            COUNT(DISTINCT c.id) AS collocations_count
        FROM lexemes l
        LEFT JOIN parts_of_speech p ON l.pos_id = p.id
        LEFT JOIN collocations c ON (c.head_lexeme_id = l.id OR c.collocate_lexeme_id = l.id)
        WHERE (pos_filter IS NULL OR p.code = pos_filter)
        GROUP BY l.id, l.word, p.code, p.description, l.frequency
        ORDER BY l.word ASC;
    END;
    $$ LANGUAGE plpgsql;

    -- Функция 2: Получить словосочетания для заданного слова
    -- Согласно Заданию 3: "слова, с которыми данное слово может сочетаться"
    CREATE OR REPLACE FUNCTION get_collocations_for_word(
        word_text VARCHAR,
        pos_code VARCHAR DEFAULT NULL
    )
    RETURNS TABLE (
        collocation_id INT,
        head_word VARCHAR,
        head_pos VARCHAR,
        collocate_word VARCHAR,
        collocate_pos VARCHAR,
        relation_type VARCHAR,
        example_context TEXT,
        co_occurrence_count INT
    ) AS $$
    BEGIN
        RETURN QUERY
        SELECT
            c.id AS collocation_id,
            h.word AS head_word,
            hp.code AS head_pos,
            col.word AS collocate_word,
            cp.code AS collocate_pos,
            c.relation_type,
            c.example_context,
            c.co_occurrence_count
        FROM lexemes h
        JOIN parts_of_speech hp ON h.pos_id = hp.id
        JOIN collocations c ON c.head_lexeme_id = h.id
        JOIN lexemes col ON c.collocate_lexeme_id = col.id
        JOIN parts_of_speech cp ON col.pos_id = cp.id
        WHERE h.word = word_text
            AND (pos_code IS NULL OR hp.code = pos_code)

        UNION ALL

        SELECT
            c.id AS collocation_id,
            col.word AS head_word,
            cp.code AS head_pos,
            h.word AS collocate_word,
            hp.code AS collocate_pos,
            c.relation_type,
            c.example_context,
            c.co_occurrence_count
        FROM lexemes h
        JOIN parts_of_speech hp ON h.pos_id = hp.id
        JOIN collocations c ON c.collocate_lexeme_id = h.id
        JOIN lexemes col ON c.head_lexeme_id = col.id
        JOIN parts_of_speech cp ON col.pos_id = cp.id
        WHERE h.word = word_text
            AND (pos_code IS NULL OR hp.code = pos_code)
        ORDER BY co_occurrence_count DESC, relation_type;
    END;
    $$ LANGUAGE plpgsql;

    -- Функция 3: Добавить или обновить лексему
    CREATE OR REPLACE FUNCTION add_or_update_lexeme(
        word_text VARCHAR,
        pos_code VARCHAR,
        increment_frequency BOOLEAN DEFAULT FALSE
    )
    RETURNS INT AS $$
    DECLARE
        lexeme_id INT;
        pos_id_val INT;
    BEGIN
        -- Получить ID части речи
        SELECT id INTO pos_id_val FROM parts_of_speech WHERE code = pos_code;

        IF pos_id_val IS NULL THEN
            RAISE EXCEPTION 'Part of speech with code % not found', pos_code;
        END IF;

        -- Попытаться найти существующую лексему
        SELECT id INTO lexeme_id
        FROM lexemes
        WHERE word = word_text AND pos_id = pos_id_val;

        -- Если не найдена, создать новую
        IF lexeme_id IS NULL THEN
            INSERT INTO lexemes (word, pos_id, frequency)
            VALUES (word_text, pos_id_val, 1)
            RETURNING id INTO lexeme_id;
        ELSE
            -- Обновить частоту, если требуется
            IF increment_frequency THEN
                UPDATE lexemes
                SET frequency = frequency + 1
                WHERE id = lexeme_id;
            END IF;
        END IF;

        RETURN lexeme_id;
    END;
    $$ LANGUAGE plpgsql;

    -- Функция 4: Добавить словосочетание
    -- Согласно Заданию 3: добавление связей между словами
    CREATE OR REPLACE FUNCTION add_collocation(
        head_word VARCHAR,
        head_pos VARCHAR,
        collocate_word VARCHAR,
        collocate_pos VARCHAR,
        relation_type_val VARCHAR DEFAULT NULL,
        example_context_val TEXT DEFAULT NULL
    )
    RETURNS INT AS $$
    DECLARE
        head_id INT;
        collocate_id INT;
        collocation_id INT;
        relation_type_default VARCHAR;
    BEGIN
        -- Получить или создать лексемы
        SELECT add_or_update_lexeme(head_word, head_pos, FALSE) INTO head_id;
        SELECT add_or_update_lexeme(collocate_word, collocate_pos, FALSE) INTO collocate_id;

        -- Определить тип связи по умолчанию, если не указан
        IF relation_type_val IS NULL THEN
            SELECT CONCAT(cp1.description, ' + ', cp2.description) INTO relation_type_default
            FROM parts_of_speech cp1, parts_of_speech cp2
            WHERE cp1.code = head_pos AND cp2.code = collocate_pos;
            relation_type_val := relation_type_default;
        END IF;

        -- Попытаться найти существующее словосочетание
        SELECT id INTO collocation_id
        FROM collocations
        WHERE head_lexeme_id = head_id
            AND collocate_lexeme_id = collocate_id
            AND relation_type = relation_type_val;

        -- Если не найдено, создать новое
        IF collocation_id IS NULL THEN
            INSERT INTO collocations (
                head_lexeme_id,
                collocate_lexeme_id,
                relation_type,
                example_context,
                co_occurrence_count
            )
            VALUES (
                head_id,
                collocate_id,
                relation_type_val,
                example_context_val,
                1
            )
            RETURNING id INTO collocation_id;
        ELSE
            -- Увеличить счетчик совместной встречаемости
            UPDATE collocations
            SET co_occurrence_count = co_occurrence_count + 1,
                example_context = COALESCE(example_context_val, example_context)
            WHERE id = collocation_id;
        END IF;

        RETURN collocation_id;
    END;
    $$ LANGUAGE plpgsql;

    -- Функция 5: Поиск лексем по шаблону
    CREATE OR REPLACE FUNCTION search_lexemes(
        search_pattern VARCHAR,
        pos_filter VARCHAR DEFAULT NULL,
        limit_count INT DEFAULT 100
    )
    RETURNS TABLE (
        id INT,
        word VARCHAR,
        pos_code VARCHAR,
        pos_description VARCHAR,
        frequency INT,
        collocations_count BIGINT
    ) AS $$
    BEGIN
        RETURN QUERY
        SELECT
            l.id,
            l.word,
            p.code AS pos_code,
            p.description AS pos_description,
            l.frequency,
            COUNT(DISTINCT c.id) AS collocations_count
        FROM lexemes l
        LEFT JOIN parts_of_speech p ON l.pos_id = p.id
        LEFT JOIN collocations c ON (c.head_lexeme_id = l.id OR c.collocate_lexeme_id = l.id)
        WHERE l.word ILIKE '%' || search_pattern || '%'
            AND (pos_filter IS NULL OR p.code = pos_filter)
        GROUP BY l.id, l.word, p.code, p.description, l.frequency
        ORDER BY l.frequency DESC, l.word ASC
        LIMIT limit_count;
    END;
    $$ LANGUAGE plpgsql;

    -- Функция 6: Извлечение типовых словосочетаний из текста
    -- Согласно Заданию 3: "автоматизированное извлечение из исходных текстов типовых словосочетаний"
    -- Примечание: это базовая версия, полная обработка требует морфологического анализа
    CREATE OR REPLACE FUNCTION extract_collocations_from_text(
        text_content TEXT,
        document_id INT DEFAULT NULL
    )
    RETURNS TABLE (
        head_word VARCHAR,
        collocate_word VARCHAR,
        relation_type VARCHAR,
        occurrences INT
    ) AS $$
    DECLARE
        word_pair RECORD;
        head_word_text VARCHAR;
        collocate_word_text VARCHAR;
    BEGIN
        -- Это упрощенная версия. В реальности нужен морфологический анализ
        -- для определения частей речи и правильного извлечения словосочетаний.
        -- Здесь показана структура функции.

        -- Пример: извлечение биграмм (соседних слов)
        -- В реальной реализации здесь должен быть вызов внешней библиотеки
        -- для обработки естественного языка (например, через Python)

        -- Возвращаем пустой результат, так как полная реализация требует
        -- интеграции с библиотеками NLP
        RETURN;
    END;
    $$ LANGUAGE plpgsql;

    -- Функция 7: Синтез словосочетания
    -- Согласно Заданию 3: "средства синтеза словосочетаний"
    CREATE OR REPLACE FUNCTION synthesize_phrase(
        head_word VARCHAR,
        head_pos VARCHAR,
        target_relation_type VARCHAR DEFAULT NULL
    )
    RETURNS TABLE (
        suggested_collocate VARCHAR,
        collocate_pos VARCHAR,
        relation_type VARCHAR,
        example_context TEXT,
        confidence_score NUMERIC
    ) AS $$
    BEGIN
        RETURN QUERY
        SELECT
            col.word AS suggested_collocate,
            cp.code AS collocate_pos,
            c.relation_type,
            c.example_context,
            -- Оценка уверенности на основе частоты встречаемости
            CASE
                WHEN c.co_occurrence_count > 10 THEN 0.9
                WHEN c.co_occurrence_count > 5 THEN 0.7
                WHEN c.co_occurrence_count > 2 THEN 0.5
                ELSE 0.3
            END AS confidence_score
        FROM lexemes h
        JOIN parts_of_speech hp ON h.pos_id = hp.id
        JOIN collocations c ON c.head_lexeme_id = h.id
        JOIN lexemes col ON c.collocate_lexeme_id = col.id
        JOIN parts_of_speech cp ON col.pos_id = cp.id
        WHERE h.word = head_word
            AND hp.code = head_pos
            AND (target_relation_type IS NULL OR c.relation_type = target_relation_type)
        ORDER BY c.co_occurrence_count DESC, confidence_score DESC
        LIMIT 10;
    END;
    $$ LANGUAGE plpgsql;

    -- Функция 8: Получить статистику по словарю
    CREATE OR REPLACE FUNCTION get_dictionary_stats()
    RETURNS TABLE (
        total_lexemes BIGINT,
        total_collocations BIGINT,
        lexemes_with_collocations BIGINT,
        most_frequent_word VARCHAR,
        most_common_collocation TEXT
    ) AS $$
    BEGIN
        RETURN QUERY
        SELECT
            (SELECT COUNT(*) FROM lexemes) AS total_lexemes,
            (SELECT COUNT(*) FROM collocations) AS total_collocations,
            (SELECT COUNT(DISTINCT head_lexeme_id) + COUNT(DISTINCT collocate_lexeme_id)
             FROM collocations) AS lexemes_with_collocations,
            (SELECT word FROM lexemes ORDER BY frequency DESC LIMIT 1) AS most_frequent_word,
            (SELECT CONCAT(h.word, ' + ', col.word, ' (', c.relation_type, ')')
             FROM collocations c
             JOIN lexemes h ON c.head_lexeme_id = h.id
             JOIN lexemes col ON c.collocate_lexeme_id = col.id
             ORDER BY c.co_occurrence_count DESC
             LIMIT 1) AS most_common_collocation;
    END;
    $$ LANGUAGE plpgsql;
    """
    
    try:
        cursor.execute(schema_sql)
        print("Структура базы данных создана")
        
        # Добавление тестовых данных
        test_data_sql = """
        -- Добавление тестовых лексем
        INSERT INTO lexemes (word, pos_id, frequency) VALUES 
        ('make', (SELECT id FROM parts_of_speech WHERE code='V'), 5),
        ('decision', (SELECT id FROM parts_of_speech WHERE code='N'), 3),
        ('money', (SELECT id FROM parts_of_speech WHERE code='N'), 4),
        ('mistake', (SELECT id FROM parts_of_speech WHERE code='N'), 2),
        ('friends', (SELECT id FROM parts_of_speech WHERE code='N'), 1)
        ON CONFLICT (word, pos_id) DO NOTHING;
        
        -- Добавление тестовых словосочетаний
        INSERT INTO collocations (head_lexeme_id, collocate_lexeme_id, relation_type, example_context, co_occurrence_count) VALUES
        (
            (SELECT id FROM lexemes WHERE word='make' AND pos_id=(SELECT id FROM parts_of_speech WHERE code='V')),
            (SELECT id FROM lexemes WHERE word='decision' AND pos_id=(SELECT id FROM parts_of_speech WHERE code='N')),
            'Verb + Noun',
            'make a decision',
            3
        ),
        (
            (SELECT id FROM lexemes WHERE word='make' AND pos_id=(SELECT id FROM parts_of_speech WHERE code='V')),
            (SELECT id FROM lexemes WHERE word='money' AND pos_id=(SELECT id FROM parts_of_speech WHERE code='N')),
            'Verb + Noun',
            'make money',
            2
        ),
        (
            (SELECT id FROM lexemes WHERE word='make' AND pos_id=(SELECT id FROM parts_of_speech WHERE code='V')),
            (SELECT id FROM lexemes WHERE word='mistake' AND pos_id=(SELECT id FROM parts_of_speech WHERE code='N')),
            'Verb + Noun',
            'make a mistake',
            4
        ),
        (
            (SELECT id FROM lexemes WHERE word='make' AND pos_id=(SELECT id FROM parts_of_speech WHERE code='V')),
            (SELECT id FROM lexemes WHERE word='friends' AND pos_id=(SELECT id FROM parts_of_speech WHERE code='N')),
            'Verb + Noun',
            'make friends',
            1
        )
        ON CONFLICT (head_lexeme_id, collocate_lexeme_id, relation_type) DO NOTHING;
        """
        
        cursor.execute(test_data_sql)
        print("Тестовые данные добавлены")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("База данных успешно инициализирована!")
        print("Теперь вы можете запустить приложение с помощью команды: python main.py")
        
    except Exception as e:
        print(f"Ошибка при инициализации базы данных: {e}")
        conn.rollback()
        cursor.close()
        conn.close()

if __name__ == "__main__":
    initialize_database()