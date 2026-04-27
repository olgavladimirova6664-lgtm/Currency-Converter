import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
import os
from datetime import datetime


class CurrencyConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("Currency Converter")
        self.root.geometry("700x600")

        # API ключ (замените на ваш)
        self.api_key = "YOUR_API_KEY_HERE"  # Получите на exchangerate-api.com
        self.base_url = "https://api.exchangerate-api.com/v4/latest/"

        # Переменные
        self.currencies = []
        self.history = []

        self.setup_ui()
        self.load_currencies()
        self.load_history()

    def setup_ui(self):
        # Выбор валюты FROM
        tk.Label(self.root, text="Из валюты:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.from_currency = ttk.Combobox(self.root, width=27)
        self.from_currency.grid(row=0, column=1, padx=10, pady=5)

        # Выбор валюты TO
        tk.Label(self.root, text="В валюту:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.to_currency = ttk.Combobox(self.root, width=27)
        self.to_currency.grid(row=1, column=1, padx=10, pady=5)

        # Поле ввода суммы
        tk.Label(self.root, text="Сумма:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.amount_entry = tk.Entry(self.root, width=30)
        self.amount_entry.grid(row=2, column=1, padx=10, pady=5)


        # Кнопка конвертации
        tk.Button(self.root, text="Конвертировать", command=self.convert_currency,
                 bg="lightgreen", width=20).grid(row=3, column=0, columnspan=2, pady=10)

        # Результат
        tk.Label(self.root, text="Результат:").grid(row=4, column=0, padx=10, pady=5, sticky="w")
        self.result_label = tk.Label(self.root, text="", font=("Arial", 12, "bold"), fg="blue")
        self.result_label.grid(row=4, column=1, padx=10, pady=5, sticky="w")

        # Таблица истории
        tk.Label(self.root, text="История конвертаций:").grid(row=5, column=0, columnspan=2, padx=10, pady=5)

        columns = ("Дата", "Из", "В", "Сумма", "Результат")
        self.history_tree = ttk.Treeview(self.root, columns=columns, show="headings", height=10)

        for col in columns:
            self.history_tree.heading(col, text=col)
            self.history_tree.column(col, width=120)

        self.history_tree.grid(row=6, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        # Полоса прокрутки для таблицы
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.history_tree.yview)
        scrollbar.grid(row=6, column=2, sticky="ns", pady=10)
        self.history_tree.configure(yscrollcommand=scrollbar.set)

        # Кнопки управления историей
        button_frame = tk.Frame(self.root)
        button_frame.grid(row=7, column=0, columnspan=2, pady=10)

        tk.Button(button_frame, text="Сохранить историю", command=self.save_history,
                 bg="yellow", width=15).pack(side="left", padx=5)
        tk.Button(button_frame, text="Загрузить историю", command=self.load_history,
                 bg="orange", width=15).pack(side="left", padx=5)
        tk.Button(button_frame, text="Очистить историю", command=self.clear_history,
                 bg="lightcoral", width=15).pack(side="left", padx=5)

        # Настройка растягивания
        self.root.grid_rowconfigure(6, weight=1)
        self.root.grid_columnconfigure(1, weight=1)


    def load_currencies(self):
        """Загрузка списка валют из API"""
        try:
            response = requests.get(f"{self.base_url}USD")
            data = response.json()
            self.currencies = sorted(data['rates'].keys())

            self.from_currency['values'] = self.currencies
            self.to_currency['values'] = self.currencies

            # Устанавливаем значения по умолчанию
            if 'USD' in self.currencies:
                self.from_currency.set('USD')
            if 'EUR' in self.currencies:
                self.to_currency.set('EUR')
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить список валют: {e}")
            # Используем базовые валюты при ошибке
            self.currencies = ['USD', 'EUR', 'RUB', 'GBP', 'JPY', 'CNY']
            self.from_currency['values'] = self.currencies
            self.to_currency['values'] = self.currencies
            self.from_currency.set('USD')
            self.to_currency.set('EUR')

    def convert_currency(self):
        """Конвертация валюты"""
        from_curr = self.from_currency.get()
        to_curr = self.to_currency.get()
        amount_str = self.amount_entry.get().strip()

        # Проверка на пустые поля
        if not from_curr or not to_curr or not amount_str:
            messagebox.showerror("Ошибка", "Все поля должны быть заполнены!")
            return

        # Проверка суммы
        try:
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Ошибка", "Сумма должна быть положительным числом!")
            return

        try:
            # Получаем курс
            response = requests.get(f"{self.base_url}{from_curr}")
            data = response.json()

            if to_curr in data['rates']:
                rate = data['rates'][to_curr]
                result = amount * rate

                # Отображаем результат
                self.result_label.config(text=f"{result:.2f} {to_curr}")

                # Добавляем в историю
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                history_entry = {
                    "date": timestamp,
                    "from": from_curr,
                    "to": to_curr,
                    "amount": amount,
                    "result": result
                }
                self.history.append(history_entry)
                self.add_to_history_table(history_entry)

                messagebox.showinfo("Успех", "Конвертация выполнена!")
            else:
                messagebox.showerror("Ошибка", "Не удалось найти курс для выбранной валюты!")
        except requests.exceptions.RequestException:
            messagebox.showerror("Ошибка", "Проблема с подключением к интернету. Проверьте соединение.")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при конвертации: {e}")

    def add_to_history_table(self, entry):
        """Добавление записи в таблицу истории"""
        self.history_tree.insert("", "end", values=(
            entry["date"],
            entry["from"],
            entry["to"],
            f"{entry['amount']:.2f}",
            f"{entry['result']:.2f}"
        ))

    def save_history(self):
        """Сохранение истории в JSON-файл"""
        try:
            with
