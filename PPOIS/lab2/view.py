import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

class View:
    def __init__(self, root, controller):
        self.root = root
        self.controller = controller
        self.style = ttk.Style('flatly')
        self.view_mode = 'table'  # table или tree

        # Меню
        self.menubar = tk.Menu(self.root)
        self.root.config(menu=self.menubar)

        file_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="Сохранить в XML", command=self.controller.save_to_xml)
        file_menu.add_command(label="Загрузить из XML", command=self.controller.load_from_xml)
        file_menu.add_command(label="Дополнить из XML", command=self.controller.add_from_xml)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.root.quit)

        edit_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Правка", menu=edit_menu)
        edit_menu.add_command(label="Добавить запись", command=self.controller.open_add_dialog)
        edit_menu.add_command(label="Поиск", command=self.controller.open_search_dialog)
        edit_menu.add_command(label="Удалить", command=self.controller.open_delete_dialog)

        view_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Вид", menu=view_menu)
        view_menu.add_command(label="Таблица", command=lambda: self.controller.switch_view('table'))
        view_menu.add_command(label="Дерево", command=lambda: self.controller.switch_view('tree'))

        # Панель инструментов
        self.toolbar = ttk.Frame(self.root)
        self.toolbar.pack(fill='x', pady=5)

        ttk.Button(self.toolbar, text="Сохранить", bootstyle=PRIMARY, command=self.controller.save_to_xml).pack(
            side='left', padx=2)
        ttk.Button(self.toolbar, text="Загрузить", bootstyle=PRIMARY, command=self.controller.load_from_xml).pack(
            side='left', padx=2)
        ttk.Button(self.toolbar, text="Дополнить", bootstyle=PRIMARY, command=self.controller.add_from_xml).pack(
            side='left', padx=2)
        ttk.Button(self.toolbar, text="Добавить", bootstyle=SUCCESS, command=self.controller.open_add_dialog).pack(
            side='left', padx=2)
        ttk.Button(self.toolbar, text="Поиск", bootstyle=INFO, command=self.controller.open_search_dialog).pack(
            side='left', padx=2)
        ttk.Button(self.toolbar, text="Удалить", bootstyle=DANGER, command=self.controller.open_delete_dialog).pack(
            side='left', padx=2)

        # Главный контейнер
        self.main_frame = ttk.Frame(self.root, padding=10)
        self.main_frame.pack(fill='both', expand=True)

        # Treeview (таблица или дерево)
        self.tree = ttk.Treeview(self.main_frame, show='headings', selectmode='browse')
        self.tree.pack(side='left', fill='both', expand=True)
        self.update_columns()

        # Прокрутка
        scrollbar = ttk.Scrollbar(self.main_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')

        # Панель навигации
        self.nav_frame = ttk.Frame(self.main_frame)
        self.nav_frame.pack(fill='x', pady=10)

        self.first_btn = ttk.Button(self.nav_frame, text='« Первая', bootstyle=INFO, command=self.controller.first_page)
        self.first_btn.pack(side='left', padx=2)
        self.prev_btn = ttk.Button(self.nav_frame, text='← Назад', bootstyle=INFO, command=self.controller.prev_page)
        self.prev_btn.pack(side='left', padx=2)
        self.page_label = ttk.Label(self.nav_frame, text='Страница 1 из 1')
        self.page_label.pack(side='left', padx=5)
        self.next_btn = ttk.Button(self.nav_frame, text='Вперёд →', bootstyle=INFO, command=self.controller.next_page)
        self.next_btn.pack(side='left', padx=2)
        self.last_btn = ttk.Button(self.nav_frame, text='Последняя »', bootstyle=INFO, command=self.controller.last_page)
        self.last_btn.pack(side='left', padx=2)

        self.per_page_var = tk.StringVar(value='10')
        ttk.Label(self.nav_frame, text='Записей на странице:').pack(side='left', padx=5)
        ttk.Entry(self.nav_frame, textvariable=self.per_page_var, width=5).pack(side='left')
        ttk.Button(self.nav_frame, text='Применить', bootstyle=SECONDARY, command=self.controller.update_per_page).pack(side='left', padx=2)

        self.total_label = ttk.Label(self.nav_frame, text='Всего записей: 0')
        self.total_label.pack(side='right', padx=5)

        # Статусная строка
        self.status_var = tk.StringVar(value="Готово")
        self.status_label = ttk.Label(self.main_frame, textvariable=self.status_var, bootstyle=INFO)
        self.status_label.pack(fill='x', pady=(10, 0))

        self.root.bind("<Configure>", self.on_resize)

    def update_columns(self):
        self.tree['columns'] = (
            'rowid', 'surname', 'name', 'patronymic', 'account_number',
            'registration_address', 'mobile_phone', 'landline_phone'
        ) if self.view_mode == 'table' else ()
        if self.view_mode == 'table':
            columns = [
                ('rowid', 'ID', 50),
                ('surname', 'Фамилия', 120),
                ('name', 'Имя', 100),
                ('patronymic', 'Отчество', 120),
                ('account_number', 'Номер счёта', 120),
                ('registration_address', 'Адрес', 200),
                ('mobile_phone', 'Мобильный', 120),
                ('landline_phone', 'Городской', 120)
            ]
            for col_id, col_text, width in columns:
                self.tree.heading(col_id, text=col_text)
                self.tree.column(col_id, width=width, minwidth=width, anchor='w', stretch=True)
            self.tree.tag_configure('oddrow', background='#f8f9fa')
            self.tree.tag_configure('evenrow', background='#e9ecef')
            self.tree['show'] = 'headings'
        else:
            self.tree['show'] = 'tree'

    def update_data(self, data, current_page, total_pages, total_items):
        for row in self.tree.get_children():
            self.tree.delete(row)

        if self.view_mode == 'table':
            for i, item in enumerate(data):
                tag = 'evenrow' if i % 2 == 0 else 'oddrow'
                values = tuple('' if x is None else x for x in item)
                self.tree.insert('', tk.END, values=values, tags=(tag,))
        else:
            for item in data:
                root = self.tree.insert('', tk.END, text=f"Запись {item[0]}")
                fields = ['ID', 'Фамилия', 'Имя', 'Отчество', 'Номер счёта', 'Адрес', 'Мобильный', 'Городской']
                for i, value in enumerate(item):
                    self.tree.insert(root, tk.END, text=f"{fields[i]}: {value if value else ''}")

        self.page_label.config(text=f'Страница {current_page}/{total_pages}')
        self.total_label.config(text=f'Всего записей: {total_items}')
        self.update_status(f"Загружено {len(data)} записей")

    def on_resize(self, event):
        if self.view_mode == 'table':
            total_width = self.tree.winfo_width()
            if total_width > 0:
                for col_id, _, base_width in [
                    ('rowid', 'ID', 50),
                    ('surname', 'Фамилия', 120),
                    ('name', 'Имя', 100),
                    ('patronymic', 'Отчество', 120),
                    ('account_number', 'Номер счёта', 120),
                    ('registration_address', 'Адрес', 200),
                    ('mobile_phone', 'Мобильный', 120),
                    ('landline_phone', 'Городской', 120)
                ]:
                    self.tree.column(col_id, width=max(base_width, int(base_width * total_width / 950)))

    def update_status(self, message):
        self.status_var.set(message)
        self.root.after(5000, lambda: self.status_var.set("Готово"))

    def get_selected_item(self):
        selected = self.tree.selection()
        if selected and self.view_mode == 'table':
            return self.tree.item(selected[0])['values']
        return None

    def open_record_dialog(self, title, default_values=None):
        dialog = ttk.Toplevel(self.root)
        dialog.title(title)
        dialog.geometry("400x400")
        dialog.transient(self.root)
        dialog.grab_set()

        fields = [
            ('Фамилия', 'surname', True),
            ('Имя', 'name', True),
            ('Отчество', 'patronymic', True),
            ('Номер счёта', 'account_number', False),
            ('Адрес', 'registration_address', True),
            ('Мобильный телефон', 'mobile_phone', False),
            ('Городской телефон', 'landline_phone', False)
        ]

        entries = {}
        for i, (label, key, required) in enumerate(fields):
            ttk.Label(dialog, text=label).grid(row=i, column=0, padx=5, pady=5, sticky='w')
            entry = ttk.Entry(dialog)
            entry.grid(row=i, column=1, padx=5, pady=5, sticky='ew')
            if default_values and len(default_values) > i + 1:
                value = default_values[i + 1]
                entry.insert(0, value if value is not None else '')
            entries[key] = (entry, required)

        def submit():
            data = {}
            for key, (entry, required) in entries.items():
                value = entry.get().strip()
                if required and not value:
                    messagebox.showerror("Ошибка", f"Поле {key.replace('_', ' ').title()} обязательно")
                    return
                data[key] = value if value else None
            self.controller.save_record(data, dialog)

        ttk.Button(dialog, text="Сохранить", bootstyle=PRIMARY, command=submit).grid(row=len(fields), column=0, columnspan=2, pady=10)
        dialog.columnconfigure(1, weight=1)

    def open_search_dialog(self):
        dialog = ttk.Toplevel(self.root)
        dialog.title("Поиск записей")
        dialog.geometry("500x500")
        dialog.transient(self.root)
        dialog.grab_set()

        fields = [
            ('Фамилия', 'surname'),
            ('Имя', 'name'),
            ('Отчество', 'patronymic'),
            ('Номер счёта', 'account_number'),
            ('Адрес', 'registration_address'),
            ('Мобильный телефон', 'mobile_phone'),
            ('Городской телефон', 'landline_phone'),
            ('Цифры в номере', 'number_contains')
        ]

        entries = {}
        for i, (label, key) in enumerate(fields):
            ttk.Label(dialog, text=label).grid(row=i, column=0, padx=5, pady=5, sticky='w')
            entry = ttk.Entry(dialog)
            entry.grid(row=i, column=1, padx=5, pady=5, sticky='ew')
            entries[key] = entry

        result_frame = ttk.Frame(dialog)
        result_frame.grid(row=len(fields), column=0, columnspan=2, pady=10, sticky='nsew')
        result_tree = ttk.Treeview(result_frame, columns=(
            'rowid', 'surname', 'name', 'patronymic', 'account_number',
            'registration_address', 'mobile_phone', 'landline_phone'
        ), show='headings')
        columns = [
            ('rowid', 'ID', 50),
            ('surname', 'Фамилия', 100),
            ('name', 'Имя', 80),
            ('patronymic', 'Отчество', 100),
            ('account_number', 'Номер счёта', 100),
            ('registration_address', 'Адрес', 150),
            ('mobile_phone', 'Мобильный', 100),
            ('landline_phone', 'Городской', 100)
        ]
        for col_id, col_text, width in columns:
            result_tree.heading(col_id, text=col_text)
            result_tree.column(col_id, width=width, anchor='w')
        result_tree.pack(fill='both', expand=True)

        def search():
            for row in result_tree.get_children():
                result_tree.delete(row)
            data = {}
            for key, entry in entries.items():
                value = entry.get().strip()
                if value:
                    data[key] = value
            results = self.controller.search_records(data)
            for item in results:
                result_tree.insert('', tk.END, values=tuple('' if x is None else x for x in item))

        ttk.Button(dialog, text="Найти", bootstyle=PRIMARY, command=search).grid(row=len(fields) + 1, column=0, columnspan=2, pady=10)
        dialog.columnconfigure(1, weight=1)
        dialog.rowconfigure(len(fields), weight=1)

    def open_delete_dialog(self):
        dialog = ttk.Toplevel(self.root)
        dialog.title("Удаление записей")
        dialog.geometry("400x400")
        dialog.transient(self.root)
        dialog.grab_set()

        fields = [
            ('Фамилия', 'surname'),
            ('Имя', 'name'),
            ('Отчество', 'patronymic'),
            ('Номер счёта', 'account_number'),
            ('Адрес', 'registration_address'),
            ('Мобильный телефон', 'mobile_phone'),
            ('Городской телефон', 'landline_phone'),
            ('Цифры в номере', 'number_contains')
        ]

        entries = {}
        for i, (label, key) in enumerate(fields):
            ttk.Label(dialog, text=label).grid(row=i, column=0, padx=5, pady=5, sticky='w')
            entry = ttk.Entry(dialog)
            entry.grid(row=i, column=1, padx=5, pady=5, sticky='ew')
            entries[key] = entry

        def delete():
            data = {}
            for key, entry in entries.items():
                value = entry.get().strip()
                if value:
                    data[key] = value
            count = self.controller.delete_records(data)
            messagebox.showinfo("Результат", f"Удалено записей: {count}")
            dialog.destroy()

        ttk.Button(dialog, text="Удалить", bootstyle=DANGER, command=delete).grid(row=len(fields), column=0, columnspan=2, pady=10)
        dialog.columnconfigure(1, weight=1)