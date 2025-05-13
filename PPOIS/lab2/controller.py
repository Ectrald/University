from model import Model
from view import View
from tkinter import messagebox, filedialog
import re

class Controller:
    def __init__(self, root):
        self.model = Model()
        self.view = View(root, self)
        self.current_page = 1
        self.per_page = 10
        self.view_mode = 'table'

        #self.model.add_test_data()
        self.load_data()

    def load_data(self):
        data = self.model.get_items(self.current_page, self.per_page)
        total_pages = self.model.get_total_pages(self.per_page)
        total_items = self.model.get_total_items()
        self.view.update_data(data, self.current_page, total_pages, total_items)

    def first_page(self):
        self.current_page = 1
        self.load_data()

    def last_page(self):
        total_pages = self.model.get_total_pages(self.per_page)
        self.current_page = total_pages
        self.load_data()

    def next_page(self):
        total_pages = self.model.get_total_pages(self.per_page)
        if self.current_page < total_pages:
            self.current_page += 1
            self.load_data()

    def prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.load_data()

    def update_per_page(self):
        try:
            per_page = int(self.view.per_page_var.get())
            if per_page <= 0:
                raise ValueError
            self.per_page = per_page
            self.current_page = 1
            self.load_data()
        except ValueError:
            messagebox.showerror("Ошибка", "Введите положительное число записей на странице")
            self.view.per_page_var.set(str(self.per_page))

    def switch_view(self, mode):
        self.view_mode = mode
        self.view.view_mode = mode
        self.view.update_columns()
        self.load_data()

    def save_to_xml(self):
        filename = filedialog.asksaveasfilename(defaultextension=".xml", filetypes=[("XML files", "*.xml")])
        if filename:
            try:
                self.model.save_to_xml(filename)
                self.view.update_status("Данные успешно сохранены в XML")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить файл: {str(e)}")

    def load_from_xml(self):
        filename = filedialog.askopenfilename(filetypes=[("XML files", "*.xml")])
        if filename:
            try:
                self.model.load_from_xml(filename)
                self.current_page = 1
                self.load_data()
                self.view.update_status("Данные успешно загружены из XML")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить файл: {str(e)}")

    def add_from_xml(self):
        filename = filedialog.askopenfilename(filetypes=[("XML files", "*.xml")])
        if filename:
            try:
                self.model.add_from_xml(filename)
                self.current_page = 1
                self.load_data()
                self.view.update_status("Данные успешно загружены из XML")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить файл: {str(e)}")

    def open_add_dialog(self):
        self.view.open_record_dialog("Добавить запись")

    def open_search_dialog(self):
        self.view.open_search_dialog()

    def open_delete_dialog(self):
        self.view.open_delete_dialog()

    def save_record(self, data, dialog):
        try:
            for phone in [data['mobile_phone'], data['landline_phone']]:
                if phone and not re.match(r'^\+?\d{10,12}$', phone):
                    messagebox.showerror("Ошибка", "Неверный формат номера телефона")
                    return
            if data['account_number'] and not data['account_number'].isdigit():
                messagebox.showerror("Ошибка", "Номер счёта должен быть числом")
                return
            if not data['mobile_phone'] and not data['landline_phone']:
                messagebox.showerror("Ошибка", "Укажите хотя бы один номер телефона")
                return

            self.model.add_data(
                surname=data['surname'],
                name=data['name'],
                patronymic=data['patronymic'],
                account_number=int(data['account_number']) if data['account_number'] else None,
                registration_address=data['registration_address'],
                mobile_phone=data['mobile_phone'],
                landline_phone=data['landline_phone']
            )
            self.load_data()
            self.view.update_status("Запись успешно сохранена")
            dialog.destroy()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить запись: {str(e)}")

    def search_records(self, data):
        search_params = {}
        if data.get('surname'):
            search_params['surname'] = data['surname']
        if data.get('name'):
            search_params['name'] = data['name']
        if data.get('patronymic'):
            search_params['patronymic'] = data['patronymic']
        if data.get('account_number'):
            try:
                search_params['account_number'] = int(data['account_number'])
            except ValueError:
                messagebox.showerror("Ошибка", "Номер счёта должен быть числом")
                return []
        if data.get('registration_address'):
            search_params['registration_address'] = data['registration_address']
        if data.get('mobile_phone'):
            search_params['mobile_phone'] = data['mobile_phone']
        if data.get('landline_phone'):
            search_params['landline_phone'] = data['landline_phone']
        if data.get('number_contains'):
            search_params['number_contains'] = data['number_contains']

        return self.model.search_data(**search_params)

    def delete_records(self, data):
        delete_params = {}
        if data.get('surname'):
            delete_params['surname'] = data['surname']
        if data.get('name'):
            delete_params['name'] = data['name']
        if data.get('patronymic'):
            delete_params['patronymic'] = data['patronymic']
        if data.get('account_number'):
            try:
                delete_params['account_number'] = int(data['account_number'])
            except ValueError:
                messagebox.showerror("Ошибка", "Номер счёта должен быть числом")
                return 0
        if data.get('registration_address'):
            delete_params['registration_address'] = data['registration_address']
        if data.get('mobile_phone'):
            delete_params['mobile_phone'] = data['mobile_phone']
        if data.get('landline_phone'):
            delete_params['landline_phone'] = data['landline_phone']
        if data.get('number_contains'):
            delete_params['number_contains'] = data['number_contains']

        count = self.model.delete_data_with_count(**delete_params)
        self.load_data()
        return count