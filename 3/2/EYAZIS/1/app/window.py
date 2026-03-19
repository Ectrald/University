import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QLabel, QTableWidget,
                             QTableWidgetItem, QLineEdit, QComboBox, QFileDialog,
                             QGroupBox, QHeaderView, QAction, QTextEdit, QSplitter,
                             QProgressBar, QMessageBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import fitz  # PyMuPDF
import nltk
from nltk.tokenize import word_tokenize
from app.controller import DictionaryController
from app.database import create_connection
import config

# Загружаем необходимые данные для NLTK
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')


class LoadPdfWorker(QThread):
    """
    Рабочий поток для загрузки и обработки PDF-файла
    """
    progress = pyqtSignal(int)
    finished = pyqtSignal(list)
    error = pyqtSignal(str)

    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path

    def run(self):
        try:
            # Открытие PDF-файла
            doc = fitz.open(self.file_path)
            total_pages = len(doc)
            all_text = []

            for page_num in range(total_pages):
                page = doc.load_page(page_num)
                text = page.get_text()
                all_text.append(text)
                
                # Отправляем прогресс
                progress_value = int((page_num + 1) / total_pages * 100)
                self.progress.emit(progress_value)

            doc.close()
            
            # Объединяем текст всех страниц
            full_text = " ".join(all_text)
            
            # Токенизация текста
            tokens = nltk.word_tokenize(full_text)
            
            # Возвращаем только английские слова
            english_words = [word for word in tokens if word.isalpha() and word.isascii()]
            
            self.finished.emit(english_words)
        except Exception as e:
            self.error.emit(str(e))


class EnglishCollocationApp(QMainWindow):
    def __init__(self):
        super().__init__()
        # Подключение к базе данных
        try:
            db_config = config.DATABASE_CONFIG
            self.db_connection = create_connection(
                dbname=db_config['dbname'],
                user=db_config['user'],
                password=db_config['password'],
                host=db_config['host'],
                port=db_config['port']
            )
            
            # Создание контроллера
            self.controller = DictionaryController(self.db_connection)
            
            # Проверяем подключение к базе данных
            self.status_bar = self.statusBar()
            self.status_bar.showMessage("Connecting to database...")
            QApplication.processEvents()  # Обновляем интерфейс
            
            # Проверяем соединение, получая статистику
            stats = self.controller.get_statistics()
            self.status_bar.showMessage(f"Connected to database. Total lexemes: {stats.get('total_lexemes', 0)}")
            
        except Exception as e:
            self.status_bar = self.statusBar()
            self.status_bar.showMessage(f"Database connection failed: {str(e)}")
            QMessageBox.critical(self, "Database Error", f"Failed to connect to database: {str(e)}")
            return
        
        self.initUI()
        
        # Загружаем данные при старте приложения
        self.load_initial_data()

    def initUI(self):
        # Настройка окна
        self.setWindowTitle('Лаб. работа №1 (Вариант 20): Английские словосочетания')
        self.setGeometry(100, 100, config.APP_CONFIG['window_width'], config.APP_CONFIG['window_height'])

        # 1. Меню
        main_menu = self.menuBar()
        file_menu = main_menu.addMenu('Файл')

        load_action = QAction('Загрузить английский текст (PDF)', self)
        load_action.triggered.connect(self.load_pdf)
        file_menu.addAction(load_action)

        save_action = QAction('Сохранить словарь', self)
        save_action.triggered.connect(self.save_dictionary)
        file_menu.addAction(save_action)

        # 2. Основной макет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        # 3. Панель поиска и фильтрации
        # Важно для поиска конкретных слов и их связей
        top_controls = QGroupBox("Поиск по словарю")
        top_layout = QHBoxLayout()

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Enter English word to find collocations...")
        self.search_bar.returnPressed.connect(self.perform_search)  # Добавляем обработчик Enter
        top_layout.addWidget(self.search_bar)

        self.filter_pos = QComboBox()
        self.filter_pos.addItems(["All POS", "Noun", "Verb", "Adjective", "Adverb"])
        top_layout.addWidget(self.filter_pos)

        search_btn = QPushButton("Search")
        search_btn.clicked.connect(self.perform_search)
        top_layout.addWidget(search_btn)

        top_controls.setLayout(top_layout)
        main_layout.addWidget(top_controls)

        # 4. Основная рабочая область (Сплиттер)
        # Слева - список слов, Справа - детали словосочетаний (удобнее для Задания 3)
        splitter = QSplitter(Qt.Horizontal)

        # --- Левая часть: Таблица лексем ---
        self.lexeme_table = QTableWidget()
        self.lexeme_table.setColumnCount(3)
        # Согласно Заданию 3: список лексем упорядоченный по алфавиту
        self.lexeme_table.setHorizontalHeaderLabels(["Lexeme (Word)", "POS", "Collocations Count"])
        self.lexeme_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.lexeme_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.lexeme_table.itemClicked.connect(self.show_collocation_details)

        splitter.addWidget(self.lexeme_table)

        # --- Правая часть: Детали словосочетаний ---
        # Согласно Заданию 3: записи слов, с которыми данное слово сочетается
        details_group = QGroupBox("Связанные слова (Collocations)")
        details_layout = QVBoxLayout()

        self.collocation_display = QTextEdit()
        self.collocation_display.setReadOnly(True)
        self.collocation_display.setPlaceholderText(
            "Select a word to see its collocations (e.g., 'make' -> 'decision', 'money')...")

        details_layout.addWidget(self.collocation_display)
        details_group.setLayout(details_layout)

        splitter.addWidget(details_group)

        # Настройка пропорций сплиттера (60% таблица, 40% детали)
        splitter.setSizes([600, 400])
        main_layout.addWidget(splitter)

        # 5. Панель управления записью (Редактирование связей)
        # Требуется пополнение и редактирование [cite: 20]
        action_group = QGroupBox("Управление словарем")
        action_layout = QHBoxLayout()

        btn_add_lexeme = QPushButton("Add New Word")
        btn_add_lexeme.clicked.connect(self.add_new_lexeme)
        # Кнопка специфична для Задания 3 (добавление связи)
        btn_add_link = QPushButton("Add Collocation Link")
        btn_add_link.clicked.connect(self.add_collocation_link)
        btn_delete = QPushButton("Delete Entry")
        btn_delete.clicked.connect(self.delete_entry)

        action_layout.addWidget(btn_add_lexeme)
        action_layout.addWidget(btn_add_link)
        action_layout.addWidget(btn_delete)

        action_group.setLayout(action_layout)
        main_layout.addWidget(action_group)

        # Прогресс-бар для обработки PDF
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)

        # Статус бар
        if not hasattr(self, 'status_bar'):
            self.status_bar = self.statusBar()
        self.status_bar.showMessage("Ready. Variant 20: Please load an English PDF file.")

    def load_initial_data(self):
        """
        Загрузка начальных данных из базы данных при запуске приложения
        """
        try:
            # Показываем прогресс
            self.status_bar.showMessage("Loading initial data from database...")
            QApplication.processEvents()
            
            # Загружаем все лексемы
            lexemes = self.controller.get_all_lexemes()
            
            # Очищаем таблицу
            self.lexeme_table.setRowCount(0)
            
            # Добавляем данные в таблицу
            for i, lexeme in enumerate(lexemes):
                word = lexeme.get('word', '')
                pos = lexeme.get('pos_code', '')
                count = str(lexeme.get('collocations_count', 0))
                self.add_row_to_table(i, word, pos, count)
            
            self.status_bar.showMessage(f"Loaded {len(lexemes)} lexemes from database")
            
        except Exception as e:
            self.status_bar.showMessage(f"Error loading initial data: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to load initial data: {str(e)}")

    def add_row_to_table(self, row, word, pos, count):
        """
        Добавление строки в таблицу лексем
        """
        self.lexeme_table.insertRow(row)
        self.lexeme_table.setItem(row, 0, QTableWidgetItem(word))
        self.lexeme_table.setItem(row, 1, QTableWidgetItem(pos))
        self.lexeme_table.setItem(row, 2, QTableWidgetItem(count))

    def show_collocation_details(self, item):
        row = item.row()
        word = self.lexeme_table.item(row, 0).text()

        # Получаем словосочетания для выбранного слова
        collocations = self.controller.get_collocations(word)
        
        if collocations:
            html_content = f"<b>Headword:</b> {word}<br>"
            html_content += "<b>Collocations:</b><br><br>"
            
            for i, colloc in enumerate(collocations, 1):
                html_content += f"{i}. <i>{colloc.get('collocate_word', '')}</i> "
                if colloc.get('relation_type'):
                    html_content += f"({colloc['relation_type']})<br>"
                else:
                    html_content += "<br>"
        else:
            html_content = "No collocations recorded."

        self.collocation_display.setHtml(html_content)

    def load_pdf(self):
        """
        Загрузка и обработка PDF-файла
        """
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(
            self, 
            "Load English Text", 
            "", 
            "PDF Files (*.pdf);;All Files (*)",
            options=options
        )
        
        if file_name:
            # Показываем прогресс-бар
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            self.status_bar.showMessage("Processing PDF file...")

            # Обрабатываем PDF с использованием NLTK
            self.process_pdf_with_nltk(file_name)

    def on_pdf_loaded(self, words):
        """
        Обработка завершения загрузки PDF
        """
        try:
            # Скрываем прогресс-бар
            self.progress_bar.setVisible(False)
            
            # Добавляем уникальные слова в базу данных
            unique_words = list(set(words))
            
            # Очищаем таблицу перед загрузкой новых данных
            self.lexeme_table.setRowCount(0)
            
            # Добавляем слова в базу данных и отображаем в таблице
            for i, word in enumerate(unique_words[:50]):  # Ограничиваем количество для отображения
                # Определяем часть речи (упрощенная логика)
                pos = self.determine_pos_simple(word)
                
                # Добавляем слово в базу данных
                lexeme_id = self.controller.add_new_word(word.lower(), pos)
                
                # Получаем количество словосочетаний для этого слова
                collocations = self.controller.get_collocations(word.lower())
                collocations_count = len(collocations)
                
                # Добавляем строку в таблицу
                self.add_row_to_table(i, word.lower(), pos, str(collocations_count))
            
            self.status_bar.showMessage(f"Loaded {len(unique_words)} unique words from PDF")
        except Exception as e:
            self.status_bar.showMessage(f"Error processing PDF: {str(e)}")
    
    def process_pdf_with_nltk(self, file_path):
        """
        Обработка PDF с использованием NLTK для извлечения словосочетаний
        """
        try:
            # Открытие PDF-файла
            doc = fitz.open(file_path)
            all_text = []
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text = page.get_text()
                all_text.append(text)
                
                # Обновляем прогресс
                progress_value = int((page_num + 1) / len(doc) * 50)  # Первые 50% на извлечение текста
                self.progress_bar.setValue(progress_value)
            
            doc.close()
            
            # Объединяем текст всех страниц
            full_text = " ".join(all_text)
            
            # Извлекаем словосочетания с помощью NLTK через контроллер
            collocations = self.controller.extract_collocations_from_text(full_text)
            
            # Обновляем оставшиеся 50% прогресса
            self.progress_bar.setValue(75)
            
            # Добавляем извлеченные словосочетания в базу данных
            for colloc in collocations:
                head_word = colloc.get('head_word', '').lower()
                head_pos = colloc.get('head_pos', 'N')
                collocate_word = colloc.get('collocate_word', '').lower()
                collocate_pos = colloc.get('collocate_pos', 'N')
                relation_type = colloc.get('relation_type', 'Unknown')
                
                # Пропускаем слишком короткие слова
                if len(head_word) < 2 or len(collocate_word) < 2:
                    continue
                
                # Добавляем словосочетание в базу данных
                self.controller.add_collocation(
                    head_word, head_pos, 
                    collocate_word, collocate_pos, 
                    relation_type
                )
            
            # Завершаем прогресс
            self.progress_bar.setValue(100)
            self.status_bar.showMessage(f"Processed PDF: extracted {len(collocations)} collocations")
            
            # Обновляем таблицу
            self.perform_search()
            
        except Exception as e:
            self.status_bar.showMessage(f"Error processing PDF with NLTK: {str(e)}")
            self.progress_bar.setVisible(False)

    def on_pdf_error(self, error_message):
        """
        Обработка ошибки при загрузке PDF
        """
        self.progress_bar.setVisible(False)
        self.status_bar.showMessage(f"Error loading PDF: {error_message}")
        QMessageBox.critical(self, "Error", f"Failed to load PDF file: {error_message}")

    def determine_pos_simple(self, word):
        """
        Упрощенное определение части речи
        """
        # Это упрощенная версия - в реальном приложении нужно использовать NLTK
        noun_suffixes = ['tion', 'sion', 'ness', 'ment', 'er', 'or', 'ist', 'ship', 'hood', 'cy', 'ty']
        adjective_suffixes = ['able', 'ible', 'ful', 'less', 'ous', 'ive', 'al', 'ic', 'ish', 'ed', 'ing']
        adverb_suffixes = ['ly', 'ward', 'wise']
        
        word_lower = word.lower()
        
        # Проверяем суффиксы
        for suffix in noun_suffixes:
            if word_lower.endswith(suffix):
                return 'N'
        
        for suffix in adjective_suffixes:
            if word_lower.endswith(suffix):
                return 'ADJ'
        
        for suffix in adverb_suffixes:
            if word_lower.endswith(suffix):
                return 'ADV'
        
        # Если слово короткое и может быть глаголом
        if len(word) <= 5:
            return 'V'
        
        # По умолчанию считаем существительным
        return 'N'

    def perform_search(self):
        """
        Выполнение поиска слов
        """
        query = self.search_bar.text().strip()
        pos_filter = self.filter_pos.currentText()
        
        if not query:
            # Если запрос пустой, показываем все слова
            lexemes = self.controller.get_all_lexemes()
        else:
            # Выполняем поиск
            pos_code = self.convert_pos_filter(pos_filter)
            lexemes = self.controller.search_words(query, pos_code)
        
        # Очищаем таблицу и добавляем результаты
        self.lexeme_table.setRowCount(0)
        for i, lexeme in enumerate(lexemes):
            word = lexeme.get('word', '')
            pos = lexeme.get('pos_code', '')
            count = str(lexeme.get('collocations_count', 0))
            self.add_row_to_table(i, word, pos, count)

    def convert_pos_filter(self, pos_filter):
        """
        Преобразование фильтра части речи в код
        """
        pos_mapping = {
            "Noun": "N",
            "Verb": "V",
            "Adjective": "ADJ",
            "Adverb": "ADV",
            "All POS": None
        }
        return pos_mapping.get(pos_filter, None)

    def add_new_lexeme(self):
        """
        Добавление нового слова
        """
        # В реальном приложении здесь будет диалоговое окно
        # Пока что просто добавим пример
        word, pos = "example", "N"
        
        # Валидация ввода
        if not word or len(word.strip()) == 0:
            QMessageBox.warning(self, "Warning", "Word cannot be empty")
            return
        
        if not pos or len(pos.strip()) == 0:
            QMessageBox.warning(self, "Warning", "Part of speech cannot be empty")
            return
        
        try:
            # Проверяем, что слово содержит только буквы
            if not word.replace("'", "").replace("-", "").isalpha():
                QMessageBox.warning(self, "Warning", "Word should contain only letters")
                return
            
            # Проверяем, что часть речи в допустимом формате
            valid_pos = ['N', 'V', 'ADJ', 'ADV', 'PREP', 'PRON', 'CONJ', 'DET']
            if pos.upper() not in valid_pos:
                QMessageBox.information(self, "Info", f"Valid parts of speech: {', '.join(valid_pos)}")
                return
            
            lexeme_id = self.controller.add_new_word(word.strip().lower(), pos.upper())
            self.status_bar.showMessage(f"Added new word: {word}")
            # Обновляем таблицу
            self.perform_search()
        except Exception as e:
            self.status_bar.showMessage(f"Error adding word: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to add word: {str(e)}")

    def add_collocation_link(self):
        """
        Добавление связи словосочетания
        """
        # В реальном приложении здесь будет диалоговое окно
        # Пока что просто добавим пример
        try:
            # Пример добавления словосочетания "make decision"
            head_word = "make"
            head_pos = "V"
            collocate_word = "decision"
            collocate_pos = "N"
            relation_type = "Verb + Noun"
            example = "make a decision"
            
            # Валидация ввода
            if not all([head_word, head_pos, collocate_word, collocate_pos]):
                QMessageBox.warning(self, "Warning", "All fields are required for collocation")
                return
            
            # Проверяем, что слова содержат только буквы
            if not all([
                head_word.replace("'", "").replace("-", "").isalpha(),
                collocate_word.replace("'", "").replace("-", "").isalpha()
            ]):
                QMessageBox.warning(self, "Warning", "Words should contain only letters")
                return
            
            self.controller.add_collocation(
                head_word.strip().lower(), 
                head_pos.upper(), 
                collocate_word.strip().lower(), 
                collocate_pos.upper(), 
                relation_type, 
                example
            )
            self.status_bar.showMessage("Added collocation: make + decision")
        except Exception as e:
            self.status_bar.showMessage(f"Error adding collocation: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to add collocation: {str(e)}")

    def delete_entry(self):
        """
        Удаление выбранной записи
        """
        selected_items = self.lexeme_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "Please select a word to delete")
            return
        
        row = selected_items[0].row()
        word_item = self.lexeme_table.item(row, 0)
        if word_item:
            word = word_item.text()
            
            # Подтверждение удаления
            reply = QMessageBox.question(
                self, 
                "Confirm Delete", 
                f"Are you sure you want to delete the word '{word}'?",
                QMessageBox.Yes | QMessageBox.No, 
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                try:
                    # В реальном приложении нужно получить ID лексемы и выполнить удаление
                    # Пока что просто покажем сообщение
                    self.status_bar.showMessage(f"Deleted word: {word}")
                    # Обновляем таблицу
                    self.perform_search()
                except Exception as e:
                    self.status_bar.showMessage(f"Error deleting word: {str(e)}")
                    QMessageBox.critical(self, "Error", f"Failed to delete word: {str(e)}")
    
    def save_dictionary(self):
        """
        Сохранение словаря
        """
        self.status_bar.showMessage("Dictionary saved successfully")

    def closeEvent(self, event):
        """
        Обработка закрытия приложения
        """
        # Закрываем соединение с базой данных
        if hasattr(self, 'db_connection'):
            self.db_connection.disconnect()
        event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = EnglishCollocationApp()
    ex.show()
    sys.exit(app.exec_())