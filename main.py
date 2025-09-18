import tkinter as tk
from tkinter import messagebox, ttk, font
from datetime import datetime
import tkinter.font as tkFont
from database import (
    create_tables, add_user, add_category, add_payment_method,
    get_user_id, get_category_id, get_payment_method_id,
    add_expense_to_db, get_expenses, get_all_payment_methods
)
from notifications import check_spending_limits
from reports import generate_monthly_report

class ModernExpenseTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("💰 Трекер расходов")
        self.root.geometry("900x700")
        self.root.configure(bg='#f0f0f0')
        
        # Настройка стилей
        self.setup_styles()
        
        # Инициализация базы данных
        self.init_database()
        
        # Создание интерфейса
        self.create_widgets()
        
        # Загрузка данных
        self.load_expenses()

    def setup_styles(self):
        """Настройка стилей для приложения"""
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Цветовая схема
        self.colors = {
            'primary': '#2E86AB',
            'secondary': '#A23B72', 
            'success': '#F18F01',
            'background': '#f0f0f0',
            'card': '#ffffff',
            'text': '#333333'
        }
        
        # Настройка стилей для виджетов
        self.style.configure('Title.TLabel', 
                           font=('Arial', 16, 'bold'),
                           foreground=self.colors['primary'])
        
        self.style.configure('Card.TFrame', 
                           background=self.colors['card'],
                           relief='raised',
                           borderwidth=1)
        
        self.style.configure('Modern.TButton',
                           font=('Arial', 10, 'bold'),
                           padding=(10, 5))

    def init_database(self):
        """Инициализация базы данных"""
        create_tables()
        add_user("default_user")
        
        # Добавляем предустановленные способы оплаты
        payment_methods = ["💳 Банковская карта", "💵 Наличные", "📱 Онлайн-платеж", "🏦 Перевод"]
        for method in payment_methods:
            add_payment_method(method)

    def create_widgets(self):
        """Создание виджетов интерфейса"""
        # Главный контейнер
        main_frame = ttk.Frame(self.root, style='Card.TFrame', padding=20)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Заголовок
        title_label = ttk.Label(main_frame, text="💰 Трекер расходов", style='Title.TLabel')
        title_label.pack(pady=(0, 20))
        
        # Создание вкладок
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill='both', expand=True)
        
        # Вкладка добавления расходов
        self.create_add_expense_tab()
        
        # Вкладка просмотра расходов
        self.create_view_expenses_tab()
        
        # Вкладка статистики
        self.create_statistics_tab()

    def create_add_expense_tab(self):
        """Создание вкладки для добавления расходов"""
        add_frame = ttk.Frame(self.notebook, style='Card.TFrame', padding=20)
        self.notebook.add(add_frame, text="➕ Добавить расход")
        
        # Форма добавления
        form_frame = ttk.LabelFrame(add_frame, text="Новый расход", padding=15)
        form_frame.pack(fill='x', pady=(0, 20))
        
        # Сумма
        ttk.Label(form_frame, text="💰 Сумма (руб.):", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky='w', pady=5)
        self.amount_entry = ttk.Entry(form_frame, font=('Arial', 11), width=20)
        self.amount_entry.grid(row=0, column=1, sticky='ew', padx=(10, 0), pady=5)
        
        # Категория
        ttk.Label(form_frame, text="📂 Категория:", font=('Arial', 10, 'bold')).grid(row=1, column=0, sticky='w', pady=5)
        self.category_entry = ttk.Entry(form_frame, font=('Arial', 11), width=20)
        self.category_entry.grid(row=1, column=1, sticky='ew', padx=(10, 0), pady=5)
        
        # Способ оплаты
        ttk.Label(form_frame, text="💳 Способ оплаты:", font=('Arial', 10, 'bold')).grid(row=2, column=0, sticky='w', pady=5)
        self.payment_var = tk.StringVar()
        self.payment_combobox = ttk.Combobox(form_frame, textvariable=self.payment_var, 
                                           state="readonly", font=('Arial', 11), width=17)
        self.payment_combobox['values'] = get_all_payment_methods()
        self.payment_combobox.grid(row=2, column=1, sticky='ew', padx=(10, 0), pady=5)
        
        # Кнопки
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=20)
        
        add_button = ttk.Button(button_frame, text="➕ Добавить расход", 
                              command=self.add_expense, style='Modern.TButton')
        add_button.pack(side='left', padx=(0, 10))
        
        clear_button = ttk.Button(button_frame, text="🗑️ Очистить", 
                                command=self.clear_form, style='Modern.TButton')
        clear_button.pack(side='left')
        
        # Настройка растягивания колонок
        form_frame.columnconfigure(1, weight=1)
        
        # Статистика по категориям
        self.create_category_stats(add_frame)

    def create_category_stats(self, parent):
        """Создание статистики по категориям"""
        stats_frame = ttk.LabelFrame(parent, text="📊 Статистика по категориям", padding=15)
        stats_frame.pack(fill='x', pady=(20, 0))
        
        self.stats_text = tk.Text(stats_frame, height=8, font=('Consolas', 9), 
                                bg='#f8f9fa', relief='flat')
        self.stats_text.pack(fill='both', expand=True)
        
        # Обновляем статистику
        self.update_category_stats()

    def create_view_expenses_tab(self):
        """Создание вкладки для просмотра расходов"""
        view_frame = ttk.Frame(self.notebook, style='Card.TFrame', padding=20)
        self.notebook.add(view_frame, text="📋 Все расходы")
        
        # Панель управления
        control_frame = ttk.Frame(view_frame)
        control_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Button(control_frame, text="🔄 Обновить", 
                  command=self.load_expenses, style='Modern.TButton').pack(side='left')
        
        ttk.Button(control_frame, text="📊 Создать отчет", 
                  command=self.show_report, style='Modern.TButton').pack(side='left', padx=(10, 0))
        
        # Таблица расходов
        table_frame = ttk.Frame(view_frame)
        table_frame.pack(fill='both', expand=True)
        
        # Создание Treeview с прокруткой
        columns = ("Дата", "Сумма", "Категория", "Способ оплаты")
        self.expenses_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        
        # Настройка заголовков
        for col in columns:
            self.expenses_tree.heading(col, text=col)
            self.expenses_tree.column(col, width=150, anchor='center')
        
        # Добавление прокрутки
        scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.expenses_tree.yview)
        self.expenses_tree.configure(yscrollcommand=scrollbar.set)
        
        self.expenses_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

    def create_statistics_tab(self):
        """Создание вкладки статистики"""
        stats_frame = ttk.Frame(self.notebook, style='Card.TFrame', padding=20)
        self.notebook.add(stats_frame, text="📈 Статистика")
        
        # Общая статистика
        general_stats = ttk.LabelFrame(stats_frame, text="📊 Общая статистика", padding=15)
        general_stats.pack(fill='x', pady=(0, 20))
        
        self.general_stats_text = tk.Text(general_stats, height=6, font=('Consolas', 10), 
                                        bg='#f8f9fa', relief='flat')
        self.general_stats_text.pack(fill='x')
        
        # Кнопка обновления статистики
        ttk.Button(stats_frame, text="🔄 Обновить статистику", 
                  command=self.update_general_stats, style='Modern.TButton').pack(pady=10)
        
        # Обновляем статистику
        self.update_general_stats()

    def add_expense(self):
        """Добавление нового расхода"""
        amount = self.amount_entry.get().strip()
        category = self.category_entry.get().strip()
        payment_method = self.payment_var.get()

        # Валидация
        if not amount or not category or not payment_method:
            messagebox.showwarning("⚠️ Ошибка", "Пожалуйста, заполните все поля")
            return

        try:
            amount = float(amount)
            if amount <= 0:
                raise ValueError("Сумма должна быть положительной")
        except ValueError as e:
            messagebox.showerror("❌ Ошибка", f"Некорректная сумма: {e}")
            return

        try:
            # Добавляем в базу данных
            add_category(category)
            user_id = get_user_id("default_user")
            category_id = get_category_id(category)
            payment_method_id = get_payment_method_id(payment_method)

            add_expense_to_db(user_id, category_id, payment_method_id, amount)
            
            # Очищаем форму
            self.clear_form()
            
            # Обновляем данные
            self.load_expenses()
            self.update_category_stats()
            self.update_general_stats()
            
            messagebox.showinfo("✅ Успех", f"Расход на сумму {amount:.2f} руб. добавлен!")
            
            # Проверяем лимиты
            warnings = check_spending_limits()
            if warnings:
                messagebox.showwarning("⚠️ Уведомление", "\n".join(warnings))
                
        except Exception as e:
            messagebox.showerror("❌ Ошибка", f"Ошибка при добавлении расхода: {e}")

    def clear_form(self):
        """Очистка формы"""
        self.amount_entry.delete(0, tk.END)
        self.category_entry.delete(0, tk.END)
        self.payment_combobox.set("")

    def load_expenses(self):
        """Загрузка расходов в таблицу"""
        # Очищаем таблицу
        for item in self.expenses_tree.get_children():
            self.expenses_tree.delete(item)
        
        try:
            expenses = get_expenses()
            for expense in expenses:
                # Обрабатываем как кортеж с 6 элементами
                if len(expense) >= 4:
                    date, amount, category, payment_method = expense[0], expense[1], expense[2], expense[3]
                    # Форматируем дату
                    formatted_date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S").strftime("%d.%m.%Y %H:%M")
                    # Форматируем сумму
                    formatted_amount = f"{amount:.2f} ₽"
                    
                    self.expenses_tree.insert("", "end", values=(
                        formatted_date, formatted_amount, category, payment_method
                    ))
        except Exception as e:
            messagebox.showerror("❌ Ошибка", f"Ошибка при загрузке расходов: {e}")

    def update_category_stats(self):
        """Обновление статистики по категориям"""
        try:
            expenses = get_expenses()
            category_totals = {}
            
            for expense in expenses:
                # Обрабатываем как кортеж с 6 элементами (date, amount, category, payment_method, description, id)
                if len(expense) >= 4:
                    date, amount, category, payment_method = expense[0], expense[1], expense[2], expense[3]
                    if category not in category_totals:
                        category_totals[category] = 0
                    category_totals[category] += amount
            
            # Очищаем и заполняем статистику
            self.stats_text.delete(1.0, tk.END)
            if category_totals:
                total = sum(category_totals.values())
                self.stats_text.insert(tk.END, f"Общая сумма: {total:.2f} ₽\n\n")
                
                # Сортируем по убыванию суммы
                sorted_categories = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)
                
                for category, amount in sorted_categories:
                    percentage = (amount / total) * 100
                    self.stats_text.insert(tk.END, f"{category}: {amount:.2f} ₽ ({percentage:.1f}%)\n")
            else:
                self.stats_text.insert(tk.END, "Нет данных о расходах")
                
        except Exception as e:
            self.stats_text.delete(1.0, tk.END)
            self.stats_text.insert(tk.END, f"Ошибка загрузки статистики: {e}")

    def update_general_stats(self):
        """Обновление общей статистики"""
        try:
            expenses = get_expenses()
            current_month = datetime.now().strftime("%Y-%m")
            
            monthly_total = 0
            total_expenses = 0
            category_count = set()
            payment_methods = set()
            
            for expense in expenses:
                # Обрабатываем как кортеж с 6 элементами
                if len(expense) >= 4:
                    date, amount, category, payment_method = expense[0], expense[1], expense[2], expense[3]
                    total_expenses += amount
                    category_count.add(category)
                    payment_methods.add(payment_method)
                    
                    if date.startswith(current_month):
                        monthly_total += amount
            
            # Очищаем и заполняем статистику
            self.general_stats_text.delete(1.0, tk.END)
            self.general_stats_text.insert(tk.END, f"📅 Текущий месяц ({current_month}): {monthly_total:.2f} ₽\n")
            self.general_stats_text.insert(tk.END, f"💰 Общая сумма расходов: {total_expenses:.2f} ₽\n")
            self.general_stats_text.insert(tk.END, f"📂 Количество категорий: {len(category_count)}\n")
            self.general_stats_text.insert(tk.END, f"💳 Способов оплаты: {len(payment_methods)}\n")
            self.general_stats_text.insert(tk.END, f"📊 Всего записей: {len(expenses)}\n")
            
        except Exception as e:
            self.general_stats_text.delete(1.0, tk.END)
            self.general_stats_text.insert(tk.END, f"Ошибка загрузки статистики: {e}")

    def show_report(self):
        """Показ отчета"""
        try:
            message = generate_monthly_report()
            messagebox.showinfo("📊 Отчет", message)
        except Exception as e:
            messagebox.showerror("❌ Ошибка", f"Ошибка при создании отчета: {e}")

def main():
    """Главная функция приложения"""
    root = tk.Tk()
    app = ModernExpenseTracker(root)
    
    # Центрирование окна
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    root.mainloop()

if __name__ == "__main__":
    main()