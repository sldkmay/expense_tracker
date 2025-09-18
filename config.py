"""
Конфигурационный файл для трекера расходов
"""

# Настройки базы данных
DATABASE_CONFIG = {
    'name': 'expenses.db',
    'backup_enabled': True,
    'backup_interval_days': 7
}

# Настройки интерфейса
UI_CONFIG = {
    'theme': 'clam',
    'window_size': (900, 700),
    'colors': {
        'primary': '#2E86AB',
        'secondary': '#A23B72',
        'success': '#F18F01',
        'warning': '#F18F01',
        'error': '#E74C3C',
        'background': '#f0f0f0',
        'card': '#ffffff',
        'text': '#333333'
    },
    'fonts': {
        'title': ('Arial', 16, 'bold'),
        'heading': ('Arial', 12, 'bold'),
        'body': ('Arial', 10),
        'monospace': ('Consolas', 9)
    }
}

# Настройки уведомлений
NOTIFICATION_CONFIG = {
    'default_limits': {
        'Кофе': 1000,
        'Еда': 5000,
        'Развлечения': 2000,
        'Транспорт': 3000,
        'Покупки': 10000,
        'Здоровье': 2000,
        'Образование': 5000,
        'Другое': 2000
    },
    'daily_limit': 5000,
    'weekly_limit': 20000,
    'monthly_limit': 50000
}

# Настройки отчетов
REPORT_CONFIG = {
    'default_format': 'txt',
    'include_charts': False,
    'auto_generate_monthly': True,
    'backup_reports': True
}

# Настройки приложения
APP_CONFIG = {
    'name': 'Трекер расходов',
    'version': '2.0.0',
    'author': 'Expense Tracker Team',
    'debug_mode': False,
    'auto_save_interval': 300,  # секунды
    'max_recent_expenses': 100
}

# Предустановленные категории
DEFAULT_CATEGORIES = [
    {'name': '🍕 Еда', 'color': '#FF6B6B'},
    {'name': '🚗 Транспорт', 'color': '#4ECDC4'},
    {'name': '🛍️ Покупки', 'color': '#45B7D1'},
    {'name': '🎬 Развлечения', 'color': '#96CEB4'},
    {'name': '🏥 Здоровье', 'color': '#FFEAA7'},
    {'name': '📚 Образование', 'color': '#DDA0DD'},
    {'name': '☕ Кофе', 'color': '#8B4513'},
    {'name': '🏠 Жилье', 'color': '#A0522D'},
    {'name': '💡 Коммунальные услуги', 'color': '#FFD700'},
    {'name': '📱 Связь', 'color': '#32CD32'},
    {'name': '👕 Одежда', 'color': '#FF69B4'},
    {'name': '🎁 Подарки', 'color': '#FF1493'},
    {'name': '✈️ Путешествия', 'color': '#00CED1'},
    {'name': '💼 Работа', 'color': '#696969'},
    {'name': '🏃 Спорт', 'color': '#FF4500'},
    {'name': '🎮 Игры', 'color': '#9370DB'},
    {'name': '📺 Развлечения дома', 'color': '#20B2AA'},
    {'name': '🔧 Ремонт', 'color': '#CD853F'},
    {'name': '💊 Лекарства', 'color': '#DC143C'},
    {'name': '🎓 Обучение', 'color': '#4169E1'},
    {'name': '💸 Другое', 'color': '#808080'}
]

# Настройки валидации
VALIDATION_CONFIG = {
    'min_amount': 0.01,
    'max_amount': 1000000.0,
    'max_description_length': 500,
    'max_category_length': 100,
    'required_fields': ['amount', 'category', 'payment_method']
}

# Настройки логирования
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file': 'expense_tracker.log',
    'max_size': 10485760,  # 10MB
    'backup_count': 5
}

