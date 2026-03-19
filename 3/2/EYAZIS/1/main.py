"""
Главный модуль приложения "Английские словосочетания"
Лабораторная работа №1, Вариант 20
"""

import sys
from PyQt5.QtWidgets import QApplication, QMessageBox
from app.window import EnglishCollocationApp
from app.controller import DictionaryController


def main():
    """
    Точка входа в приложение
    """
    # Создание Qt-приложения
    app = QApplication(sys.argv)

    try:
        # Создание главного окна
        window = EnglishCollocationApp()
        
        # Проверяем, было ли успешно создано окно (проверяем подключение к БД)
        if hasattr(window, 'db_connection'):
            window.show()
        else:
            # Если подключение к БД не удалось, показываем сообщение и завершаем
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setWindowTitle("Database Connection Error")
            msg.setText("Could not connect to the database. Application will exit.")
            msg.exec_()
            sys.exit(1)

        # Запуск цикла обработки событий
        sys.exit(app.exec_())
    except Exception as e:
        # Обработка любых других ошибок при запуске
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle("Application Error")
        msg.setText(f"An error occurred while starting the application: {str(e)}")
        msg.exec_()
        sys.exit(1)


if __name__ == '__main__':
    main()
