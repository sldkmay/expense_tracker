import sqlite3
from datetime import datetime
from typing import List, Tuple, Optional
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_NAME = "expenses.db"

class DatabaseManager:
    """Класс для управления базой данных расходов"""
    
    def __init__(self, db_name: str = DB_NAME):
        self.db_name = db_name
        self.init_database()
    
    def connect_db(self) -> sqlite3.Connection:
        """Создание подключения к базе данных"""
        try:
            conn = sqlite3.connect(self.db_name)
            conn.row_factory = sqlite3.Row  # Для доступа к колонкам по имени
            return conn
        except sqlite3.Error as e:
            logger.error(f"Ошибка подключения к БД: {e}")
            raise
    
    def init_database(self):
        """Инициализация базы данных и создание таблиц"""
        try:
            with self.connect_db() as conn:
                cursor = conn.cursor()
                
                # Создание таблиц
                self._create_tables(cursor)
                conn.commit()
                logger.info("База данных инициализирована успешно")
        except sqlite3.Error as e:
            logger.error(f"Ошибка инициализации БД: {e}")
            raise
    
    def _create_tables(self, cursor: sqlite3.Cursor):
        """Создание всех необходимых таблиц"""
        tables = {
            'users': '''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''',
            'categories': '''
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    color TEXT DEFAULT '#2E86AB',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''',
            'payment_methods': '''
                CREATE TABLE IF NOT EXISTS payment_methods (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    method_name TEXT NOT NULL UNIQUE,
                    icon TEXT DEFAULT '💳',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''',
            'expenses': '''
                CREATE TABLE IF NOT EXISTS expenses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    category_id INTEGER NOT NULL,
                    payment_method_id INTEGER NOT NULL,
                    amount REAL NOT NULL CHECK(amount > 0),
                    description TEXT DEFAULT '',
                    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE,
                    FOREIGN KEY (payment_method_id) REFERENCES payment_methods(id) ON DELETE CASCADE
                )
            ''',
            'budgets': '''
                CREATE TABLE IF NOT EXISTS budgets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    category_id INTEGER,
                    amount REAL NOT NULL CHECK(amount > 0),
                    period TEXT DEFAULT 'monthly',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE
                )
            '''
        }
        
        for table_name, sql in tables.items():
            cursor.execute(sql)
            logger.info(f"Таблица {table_name} создана/проверена")
        
        # Обновляем существующие таблицы для совместимости
        self._update_existing_tables(cursor)
    
    def _update_existing_tables(self, cursor: sqlite3.Cursor):
        """Обновление существующих таблиц для совместимости"""
        try:
            # Проверяем и добавляем колонки в payment_methods
            cursor.execute("PRAGMA table_info(payment_methods)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'icon' not in columns:
                cursor.execute("ALTER TABLE payment_methods ADD COLUMN icon TEXT DEFAULT '💳'")
                logger.info("Добавлена колонка icon в payment_methods")
            
            if 'created_at' not in columns:
                cursor.execute("ALTER TABLE payment_methods ADD COLUMN created_at TIMESTAMP")
                logger.info("Добавлена колонка created_at в payment_methods")
            
            # Проверяем и добавляем колонки в categories
            cursor.execute("PRAGMA table_info(categories)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'color' not in columns:
                cursor.execute("ALTER TABLE categories ADD COLUMN color TEXT DEFAULT '#2E86AB'")
                logger.info("Добавлена колонка color в categories")
            
            if 'created_at' not in columns:
                cursor.execute("ALTER TABLE categories ADD COLUMN created_at TIMESTAMP")
                logger.info("Добавлена колонка created_at в categories")
            
            # Проверяем и добавляем колонки в users
            cursor.execute("PRAGMA table_info(users)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'created_at' not in columns:
                cursor.execute("ALTER TABLE users ADD COLUMN created_at TIMESTAMP")
                logger.info("Добавлена колонка created_at в users")
            
            # Проверяем и добавляем колонки в expenses
            cursor.execute("PRAGMA table_info(expenses)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'description' not in columns:
                cursor.execute("ALTER TABLE expenses ADD COLUMN description TEXT DEFAULT ''")
                logger.info("Добавлена колонка description в expenses")
            
            if 'created_at' not in columns:
                cursor.execute("ALTER TABLE expenses ADD COLUMN created_at TIMESTAMP")
                logger.info("Добавлена колонка created_at в expenses")
                
        except sqlite3.Error as e:
            logger.warning(f"Ошибка обновления таблиц: {e}")
    
    def add_user(self, username: str) -> int:
        """Добавление пользователя"""
        try:
            with self.connect_db() as conn:
                cursor = conn.cursor()
                cursor.execute('INSERT OR IGNORE INTO users (username) VALUES (?)', (username,))
                if cursor.rowcount == 0:
                    # Пользователь уже существует, получаем его ID
                    cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
                    result = cursor.fetchone()
                    return result['id'] if result else None
                conn.commit()
                return cursor.lastrowid
        except sqlite3.Error as e:
            logger.error(f"Ошибка добавления пользователя: {e}")
            raise
    
    def add_category(self, name: str, color: str = '#2E86AB') -> int:
        """Добавление категории"""
        try:
            with self.connect_db() as conn:
                cursor = conn.cursor()
                cursor.execute('INSERT OR IGNORE INTO categories (name, color) VALUES (?, ?)', (name, color))
                if cursor.rowcount == 0:
                    # Категория уже существует, получаем её ID
                    cursor.execute('SELECT id FROM categories WHERE name = ?', (name,))
                    result = cursor.fetchone()
                    return result['id'] if result else None
                conn.commit()
                return cursor.lastrowid
        except sqlite3.Error as e:
            logger.error(f"Ошибка добавления категории: {e}")
            raise
    
    def add_payment_method(self, method_name: str, icon: str = '💳') -> int:
        """Добавление способа оплаты"""
        try:
            with self.connect_db() as conn:
                cursor = conn.cursor()
                cursor.execute('INSERT OR IGNORE INTO payment_methods (method_name, icon) VALUES (?, ?)', 
                             (method_name, icon))
                if cursor.rowcount == 0:
                    # Способ оплаты уже существует, получаем его ID
                    cursor.execute('SELECT id FROM payment_methods WHERE method_name = ?', (method_name,))
                    result = cursor.fetchone()
                    return result['id'] if result else None
                conn.commit()
                return cursor.lastrowid
        except sqlite3.Error as e:
            logger.error(f"Ошибка добавления способа оплаты: {e}")
            raise
    
    def get_user_id(self, username: str) -> Optional[int]:
        """Получение ID пользователя"""
        try:
            with self.connect_db() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
                result = cursor.fetchone()
                return result['id'] if result else None
        except sqlite3.Error as e:
            logger.error(f"Ошибка получения ID пользователя: {e}")
            raise
    
    def get_category_id(self, category_name: str) -> Optional[int]:
        """Получение ID категории"""
        try:
            with self.connect_db() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT id FROM categories WHERE name = ?', (category_name,))
                result = cursor.fetchone()
                return result['id'] if result else None
        except sqlite3.Error as e:
            logger.error(f"Ошибка получения ID категории: {e}")
            raise
    
    def get_payment_method_id(self, method_name: str) -> Optional[int]:
        """Получение ID способа оплаты"""
        try:
            with self.connect_db() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT id FROM payment_methods WHERE method_name = ?', (method_name,))
                result = cursor.fetchone()
                return result['id'] if result else None
        except sqlite3.Error as e:
            logger.error(f"Ошибка получения ID способа оплаты: {e}")
            raise
    
    def add_expense(self, user_id: int, category_id: int, payment_method_id: int, 
                   amount: float, description: str = '') -> int:
        """Добавление расхода"""
        try:
            with self.connect_db() as conn:
                cursor = conn.cursor()
                date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cursor.execute('''
                    INSERT INTO expenses (user_id, category_id, payment_method_id, amount, description, date)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (user_id, category_id, payment_method_id, amount, description, date))
                conn.commit()
                return cursor.lastrowid
        except sqlite3.Error as e:
            logger.error(f"Ошибка добавления расхода: {e}")
            raise
    
    def get_expenses(self, user_id: Optional[int] = None, 
                    start_date: Optional[str] = None, 
                    end_date: Optional[str] = None,
                    category_id: Optional[int] = None) -> List[Tuple]:
        """Получение расходов с фильтрацией"""
        try:
            with self.connect_db() as conn:
                cursor = conn.cursor()
                
                # Проверяем, есть ли колонка description
                cursor.execute("PRAGMA table_info(expenses)")
                columns = [column[1] for column in cursor.fetchall()]
                has_description = 'description' in columns
                
                if has_description:
                    query = '''
                        SELECT e.date, e.amount, c.name, pm.method_name, e.description, e.id
                        FROM expenses e
                        JOIN categories c ON e.category_id = c.id
                        JOIN payment_methods pm ON e.payment_method_id = pm.id
                    '''
                else:
                    query = '''
                        SELECT e.date, e.amount, c.name, pm.method_name, '', e.id
                        FROM expenses e
                        JOIN categories c ON e.category_id = c.id
                        JOIN payment_methods pm ON e.payment_method_id = pm.id
                    '''
                
                conditions = []
                params = []
                
                if user_id:
                    conditions.append("e.user_id = ?")
                    params.append(user_id)
                
                if start_date:
                    conditions.append("DATE(e.date) >= ?")
                    params.append(start_date)
                
                if end_date:
                    conditions.append("DATE(e.date) <= ?")
                    params.append(end_date)
                
                if category_id:
                    conditions.append("e.category_id = ?")
                    params.append(category_id)
                
                if conditions:
                    query += " WHERE " + " AND ".join(conditions)
                
                query += " ORDER BY e.date DESC"
                
                cursor.execute(query, params)
                return cursor.fetchall()
        except sqlite3.Error as e:
            logger.error(f"Ошибка получения расходов: {e}")
            raise
    
    def get_all_payment_methods(self) -> List[str]:
        """Получение всех способов оплаты"""
        try:
            with self.connect_db() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT method_name FROM payment_methods ORDER BY method_name')
                return [row['method_name'] for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error(f"Ошибка получения способов оплаты: {e}")
            raise
    
    def get_all_categories(self) -> List[Tuple[int, str, str]]:
        """Получение всех категорий с ID, именем и цветом"""
        try:
            with self.connect_db() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT id, name, color FROM categories ORDER BY name')
                return [(row['id'], row['name'], row['color']) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error(f"Ошибка получения категорий: {e}")
            raise
    
    def get_expenses_by_category(self, user_id: Optional[int] = None, 
                               start_date: Optional[str] = None,
                               end_date: Optional[str] = None) -> dict:
        """Получение расходов сгруппированных по категориям"""
        try:
            expenses = self.get_expenses(user_id, start_date, end_date)
            category_totals = {}
            
            for date, amount, category, payment_method, description, expense_id in expenses:
                if category not in category_totals:
                    category_totals[category] = 0
                category_totals[category] += amount
            
            return category_totals
        except Exception as e:
            logger.error(f"Ошибка группировки расходов по категориям: {e}")
            raise
    
    def get_monthly_expenses(self, year: int, month: int) -> List[Tuple]:
        """Получение расходов за конкретный месяц"""
        start_date = f"{year:04d}-{month:02d}-01"
        if month == 12:
            end_date = f"{year+1:04d}-01-01"
        else:
            end_date = f"{year:04d}-{month+1:02d}-01"
        
        return self.get_expenses(start_date=start_date, end_date=end_date)
    
    def delete_expense(self, expense_id: int) -> bool:
        """Удаление расхода"""
        try:
            with self.connect_db() as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM expenses WHERE id = ?', (expense_id,))
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            logger.error(f"Ошибка удаления расхода: {e}")
            raise
    
    def get_total_expenses(self, user_id: Optional[int] = None,
                          start_date: Optional[str] = None,
                          end_date: Optional[str] = None) -> float:
        """Получение общей суммы расходов"""
        try:
            with self.connect_db() as conn:
                cursor = conn.cursor()
                
                query = "SELECT SUM(amount) FROM expenses"
                conditions = []
                params = []
                
                if user_id:
                    conditions.append("user_id = ?")
                    params.append(user_id)
                
                if start_date:
                    conditions.append("DATE(date) >= ?")
                    params.append(start_date)
                
                if end_date:
                    conditions.append("DATE(date) <= ?")
                    params.append(end_date)
                
                if conditions:
                    query += " WHERE " + " AND ".join(conditions)
                
                cursor.execute(query, params)
                result = cursor.fetchone()
                return result[0] or 0.0
        except sqlite3.Error as e:
            logger.error(f"Ошибка получения общей суммы расходов: {e}")
            raise

# Создаем глобальный экземпляр менеджера БД
db_manager = DatabaseManager()

# Функции для обратной совместимости
def connect_db():
    return db_manager.connect_db()

def create_tables():
    db_manager.init_database()

def add_user(username):
    return db_manager.add_user(username)

def add_category(name):
    return db_manager.add_category(name)

def add_payment_method(method_name):
    return db_manager.add_payment_method(method_name, '💳')

def get_user_id(username):
    return db_manager.get_user_id(username)

def get_category_id(category_name):
    return db_manager.get_category_id(category_name)

def get_payment_method_id(method_name):
    return db_manager.get_payment_method_id(method_name)

def add_expense_to_db(user_id, category_id, payment_method_id, amount):
    return db_manager.add_expense(user_id, category_id, payment_method_id, amount)

def get_expenses():
    return db_manager.get_expenses()

def get_all_payment_methods():
    return db_manager.get_all_payment_methods()