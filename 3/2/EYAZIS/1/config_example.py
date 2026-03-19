"""
Пример файла конфигурации для подключения к базе данных
Скопируйте этот файл в config.py и укажите свои параметры подключения
"""

# Параметры подключения к PostgreSQL
DATABASE_CONFIG = {
    'dbname': 'english_dictionary',  # Имя базы данных
    'user': 'postgres',              # Имя пользователя
    'password': 'your_password',     # Пароль
    'host': 'localhost',             # Хост
    'port': 5432                     # Порт
}
