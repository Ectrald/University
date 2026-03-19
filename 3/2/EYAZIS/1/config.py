"""
Файл конфигурации для подключения к базе данных
"""

import os
from dotenv import load_dotenv

# Загрузка переменных окружения из .env файла (если существует)
load_dotenv()

# Параметры подключения к PostgreSQL
DATABASE_CONFIG = {
    'dbname': os.getenv('DB_NAME', 'english_dictionary'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', '1423'),
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', '5432'))
}

# Параметры приложения
APP_CONFIG = {
    'window_width': 1000,
    'window_height': 700,
    'default_pos_filter': 'All POS',
    'max_search_results': 100,
    'default_relation_type': 'Verb + Noun'
}