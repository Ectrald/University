import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

class View:
    def __init__(self, root, controller):
        self.root = root
        self.controller = controller
        self.style = ttk.Style('flatly')
        self.view_mode = 'table'

        self._create_menu()
        self._create_toolbar()
        self._create_main_content()
        self._create_status_bar()

    def _create_menu(self):
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

    def _create_toolbar(self):
        self.toolbar = ttk.Frame(self.root)
        self.toolbar.pack(fill='x', pady=5)

        buttons = [
            ("Сохранить", PRIMARY, self.controller.save_to_xml),
            ("Загрузить", PRIMARY, self.controller.load_from_xml),
            ("Дополнить", PRIMARY, self.controller.add_from_xml),
            ("Добавить", SUCCESS, self.controller.open_add_dialog),
            ("Поиск", INFO, self.controller.open_search_dialog),
            ("Удалить", DANGER, self.controller.open_delete_dialog)
        ]

        for text, style, command in buttons:
            ttk.Button(self.toolbar, text=text, bootstyle=style, command=command).pack(side='left', padx=2)

    def _create_main_content(self):
        self.main_frame = ttk.Frame(self.root, padding=10)
        self.main_frame.pack(fill='both', expand=True)

        self.tree = ttk.Treeview(self.main_frame, show='headings', selectmode='browse')
        self.tree.pack(side='left', fill='both', expand=True)
        self.update_columns()

        scrollbar = ttk.Scrollbar(self.main_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')

        self._create_pagination_controls()

    def _create_pagination_controls(self):
        self.nav_frame = ttk.Frame(self.main_frame)
        self.nav_frame.pack(fill='x', pady=10)

        buttons = [
            ('« Первая', self.controller.first_page),
            ('← Назад', self.controller.prev_page),
            ('Вперёд →', self.controller.next_page),
            ('Последняя »', self.controller.last_page)
        ]

        self.first_btn = ttk.Button(self.nav_frame, text=buttons[0][0], bootstyle=INFO, command=buttons[0][1])
        self.first_btn.pack(side='left', padx=2)
        self.prev_btn = ttk.Button(self.nav_frame, text=buttons[1][0], bootstyle=INFO, command=buttons[1][1])
        self.prev_btn.pack(side='left', padx=2)

        self.page_label = ttk.Label(self.nav_frame, text='Страница 1 из 1')
        self.page_label.pack(side='left', padx=5)

        self.next_btn = ttk.Button(self.nav_frame, text=buttons[2][0], bootstyle=INFO, command=buttons[2][1])
        self.next_btn.pack(side='left', padx=2)
        self.last_btn = ttk.Button(self.nav_frame, text=buttons[3][0], bootstyle=INFO, command=buttons[3][1])
        self.last_btn.pack(side='left', padx=2)

        self.pagination_controls_frame = ttk.Frame(self.main_frame)
        self.pagination_controls_frame.pack(fill='x', pady=(0, 10))

        self.per_page_var = tk.StringVar(value='10')
        ttk.Label(self.pagination_controls_frame, text='Записей на странице:').pack(side='left', padx=5)
        ttk.Entry(self.pagination_controls_frame, textvariable=self.per_page_var, width=5).pack(side='left')
        ttk.Button(self.pagination_controls_frame, text='Применить', bootstyle=SECONDARY,
                   command=self.controller.update_per_page).pack(side='left', padx=2)

        self.total_label = ttk.Label(self.pagination_controls_frame, text='Всего записей: 0')
        self.total_label.pack(side='right', padx=5)

    def _create_status_bar(self):
        self.status_var = tk.StringVar(value="Готово")
        self.status_label = ttk.Label(self.main_frame, textvariable=self.status_var, bootstyle=INFO)
        self.status_label.pack(fill='x', pady=(10, 0))
        self.root.bind("<Configure>", self.on_resize)

    def update_columns(self):
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
        total_width = sum(col[2] for col in columns)  # 950

        if self.view_mode == 'table':
            self.tree['columns'] = tuple(col[0] for col in columns)
            for col_id, col_text, width in columns:
                self.tree.heading(col_id, text=col_text)
                self.tree.column(col_id, width=width, minwidth=width, anchor='w', stretch=True)
            self.tree.tag_configure('oddrow', background='#f8f9fa')
            self.tree.tag_configure('evenrow', background='#e9ecef')
            self.tree['show'] = 'headings'
        else:
            self.tree['columns'] = ()
            self.tree['show'] = 'tree'
            self.tree.column('#0', width=total_width, minwidth=total_width, stretch=False)

    def update_data(self, data, current_page, total_pages, total_items):
        self.tree.delete(*self.tree.get_children())

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
        total_width = self.tree.winfo_width()
        if total_width > 0:
            base_widths = [
                ('rowid', 50), ('surname', 120), ('name', 100),
                ('patronymic', 120), ('account_number', 120),
                ('registration_address', 200), ('mobile_phone', 120),
                ('landline_phone', 120)
            ]
            total_base_width = sum(width for _, width in base_widths)
            if self.view_mode == 'table':
                for col_id, base_width in base_widths:
                    self.tree.column(col_id, width=max(base_width, int(base_width * total_width / total_base_width)))
            else:
                scaled_width = max(total_base_width, int(total_base_width * total_width / total_base_width))
                self.tree.column('#0', width=scaled_width, minwidth=total_base_width, stretch=False)

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
            ('Номер счёта', 'account_number', True),
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

        ttk.Button(dialog, text="Сохранить", bootstyle=PRIMARY, command=submit).grid(
            row=len(fields), column=0, columnspan=2, pady=10)
        dialog.columnconfigure(1, weight=1)

    def open_search_dialog(self):
        dialog = ttk.Toplevel(self.root)
        dialog.title("Поиск записей")
        dialog.geometry("800x650")
        dialog.transient(self.root)
        dialog.grab_set()

        main_frame = ttk.Frame(dialog, padding=10)
        main_frame.pack(fill='both', expand=True)

        search_frame = ttk.Frame(main_frame)
        search_frame.pack(fill='x', pady=5)

        fields = [
            ('Фамилия', 'surname'), ('Имя', 'name'), ('Отчество', 'patronymic'),
            ('Номер счёта', 'account_number'), ('Адрес', 'registration_address'),
            ('Мобильный телефон', 'mobile_phone'), ('Городской телефон', 'landline_phone'),
            ('Цифры в номере', 'number_contains')
        ]

        self.search_entries = {}
        for i, (label, key) in enumerate(fields):
            ttk.Label(search_frame, text=label).grid(row=i, column=0, padx=5, pady=2, sticky='w')
            entry = ttk.Entry(search_frame)
            entry.grid(row=i, column=1, padx=5, pady=2, sticky='ew')
            self.search_entries[key] = entry

        ttk.Button(search_frame, text="Найти", bootstyle=PRIMARY,
                   command=self._perform_search).grid(row=len(fields), column=0, columnspan=2, pady=10)

        result_frame = ttk.Frame(main_frame)
        result_frame.pack(fill='both', expand=True, pady=5)

        self.result_tree = ttk.Treeview(result_frame, columns=(
            'rowid', 'surname', 'name', 'patronymic', 'account_number',
            'registration_address', 'mobile_phone', 'landline_phone'
        ), show='headings')

        columns = [
            ('rowid', 'ID', 50), ('surname', 'Фамилия', 100), ('name', 'Имя', 80),
            ('patronymic', 'Отчество', 100), ('account_number', 'Номер счёта', 100),
            ('registration_address', 'Адрес', 150), ('mobile_phone', 'Мобильный', 100),
            ('landline_phone', 'Городской', 100)
        ]

        for col_id, col_text, width in columns:
            self.result_tree.heading(col_id, text=col_text)
            self.result_tree.column(col_id, width=width, anchor='w')

        self.result_tree.pack(side='left', fill='both', expand=True)

        scrollbar = ttk.Scrollbar(result_frame, orient='vertical', command=self.result_tree.yview)
        self.result_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')

        pagination_frame = ttk.Frame(main_frame)
        pagination_frame.pack(fill='x', pady=5)

        ttk.Button(pagination_frame, text='« Первая', bootstyle=INFO,
                   command=lambda: self._go_to_search_page(1)).pack(side='left', padx=2)
        ttk.Button(pagination_frame, text='← Назад', bootstyle=INFO,
                   command=lambda: self._go_to_search_page(max(1, self.controller.search_current_page - 1))).pack(side='left', padx=2)
        self.search_page_label = ttk.Label(pagination_frame, text='Страница 1 из 1')
        self.search_page_label.pack(side='left', padx=5)
        ttk.Button(pagination_frame, text='Вперёд →', bootstyle=INFO,
                   command=lambda: self._go_to_search_page(self.controller.search_current_page + 1)).pack(side='left', padx=2)
        ttk.Button(pagination_frame, text='Последняя »', bootstyle=INFO,
                   command=lambda: self._go_to_search_page(self.controller.get_search_total_pages())).pack(side='left', padx=2)

        per_page_frame = ttk.Frame(main_frame)
        per_page_frame.pack(fill='x', pady=5)

        self.search_per_page_var = tk.StringVar(value='10')
        ttk.Label(per_page_frame, text='Записей на странице:').pack(side='left', padx=5)
        ttk.Entry(per_page_frame, textvariable=self.search_per_page_var, width=5).pack(side='left')
        ttk.Button(per_page_frame, text='Применить', bootstyle=SECONDARY,
                   command=self._update_search_per_page).pack(side='left', padx=5)
        self.search_total_label = ttk.Label(per_page_frame, text='Всего записей: 0')
        self.search_total_label.pack(side='right', padx=5)

    def _perform_search(self):
        search_params = {key: entry.get().strip() for key, entry in self.search_entries.items() if entry.get().strip()}
        self.controller.search_records(search_params)
        self._update_search_results()

    def _update_search_results(self):
        try:
            page_data = self.controller.get_search_page_data()
            total_pages = self.controller.get_search_total_pages()
            total_items = self.controller.search_total_items

            self.result_tree.delete(*self.result_tree.get_children())
            for item in page_data:
                self.result_tree.insert('', 'end', values=tuple('' if x is None else x for x in item))

            self.search_page_label.config(text=f'Страница {self.controller.search_current_page}/{total_pages}')
            self.search_total_label.config(text=f'Всего записей: {total_items}')
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось обновить результаты: {str(e)}")

    def _go_to_search_page(self, page_num):
        self.controller.set_search_page(page_num)
        self._update_search_results()

    def _update_search_per_page(self):
        try:
            new_per_page = int(self.search_per_page_var.get())
            if new_per_page <= 0:
                raise ValueError
            self.controller.set_search_per_page(new_per_page)
            self._update_search_results()
        except ValueError:
            messagebox.showerror("Ошибка", "Введите положительное число")
            self.search_per_page_var.set(str(self.controller.search_per_page))

    def open_delete_dialog(self):
        dialog = ttk.Toplevel(self.root)
        dialog.title("Удаление записей")
        dialog.geometry("400x400")
        dialog.transient(self.root)
        dialog.grab_set()

        fields = [
            ('Фамилия', 'surname'), ('Имя', 'name'), ('Отчество', 'patronymic'),
            ('Номер счёта', 'account_number'), ('Адрес', 'registration_address'),
            ('Мобильный телефон', 'mobile_phone'), ('Городской телефон', 'landline_phone'),
            ('Цифры в номере', 'number_contains')
        ]

        entries = {}
        for i, (label, key) in enumerate(fields):
            ttk.Label(dialog, text=label).grid(row=i, column=0, padx=5, pady=5, sticky='w')
            entry = ttk.Entry(dialog)
            entry.grid(row=i, column=1, padx=5, pady=5, sticky='ew')
            entries[key] = entry

        def delete():
            data = {key: entry.get().strip() for key, entry in entries.items() if entry.get().strip()}
            count = self.controller.delete_records(data)
            messagebox.showinfo("Результат", f"Удалено записей: {count}")
            dialog.destroy()

        ttk.Button(dialog, text="Удалить", bootstyle=DANGER, command=delete).grid(
            row=len(fields), column=0, columnspan=2, pady=10)
        dialog.columnconfigure(1, weight=1)