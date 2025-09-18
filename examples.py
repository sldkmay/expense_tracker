"""
Примеры использования трекера расходов
"""

from database import db_manager
from reports import report_generator
from notifications import notification_manager
from utils import format_currency, format_date, get_date_range
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def example_basic_usage():
    """Базовый пример использования"""
    print("=== Базовый пример использования ===")
    
    # Инициализация базы данных
    db_manager.init_database()
    
    # Добавление пользователя
    user_id = db_manager.add_user("example_user")
    print(f"Создан пользователь с ID: {user_id}")
    
    # Добавление категорий
    food_id = db_manager.add_category("Еда", "#FF6B6B")
    transport_id = db_manager.add_category("Транспорт", "#4ECDC4")
    print(f"Созданы категории: Еда (ID: {food_id}), Транспорт (ID: {transport_id})")
    
    # Добавление способов оплаты
    card_id = db_manager.add_payment_method("💳 Банковская карта", "💳")
    cash_id = db_manager.add_payment_method("💵 Наличные", "💵")
    print(f"Созданы способы оплаты: Карта (ID: {card_id}), Наличные (ID: {cash_id})")
    
    # Добавление расходов
    expense1 = db_manager.add_expense(user_id, food_id, card_id, 1500.50, "Обед в ресторане")
    expense2 = db_manager.add_expense(user_id, transport_id, cash_id, 200.00, "Такси")
    expense3 = db_manager.add_expense(user_id, food_id, card_id, 300.75, "Продукты")
    
    print(f"Добавлены расходы: {expense1}, {expense2}, {expense3}")
    
    # Получение расходов
    expenses = db_manager.get_expenses(user_id=user_id)
    print(f"\nВсего расходов: {len(expenses)}")
    for date, amount, category, payment_method, description, expense_id in expenses:
        print(f"  {format_date(date)} | {format_currency(amount)} | {category} | {payment_method}")

def example_reports():
    """Пример генерации отчетов"""
    print("\n=== Пример генерации отчетов ===")
    
    # Месячный отчет
    monthly_report = report_generator.generate_monthly_report()
    print(f"Месячный отчет: {monthly_report}")
    
    # Анализ по категориям
    category_analysis = report_generator.generate_category_analysis()
    print(f"\nАнализ по категориям:")
    for category, data in category_analysis['insights'].items():
        print(f"  {category}: {format_currency(data['total'])} ({data['percentage']:.1f}%)")
    
    # Анализ по способам оплаты
    payment_analysis = report_generator.generate_payment_method_analysis()
    print(f"\nАнализ по способам оплаты:")
    for method, amount in payment_analysis['payment_methods'].items():
        print(f"  {method}: {format_currency(amount)}")

def example_notifications():
    """Пример работы с уведомлениями"""
    print("\n=== Пример работы с уведомлениями ===")
    
    # Проверка лимитов
    warnings = notification_manager.check_spending_limits()
    if warnings:
        print("Уведомления:")
        for warning in warnings:
            print(f"  {warning}")
    else:
        print("Нет предупреждений")
    
    # Прогноз расходов
    forecast = notification_manager.get_spending_forecast()
    if forecast:
        print(f"\nПрогноз расходов:")
        print(f"  Потрачено: {format_currency(forecast['total_spent'])}")
        print(f"  Среднедневно: {format_currency(forecast['daily_average'])}")
        print(f"  Прогноз на месяц: {format_currency(forecast['forecast'])}")
    
    # Рекомендации
    recommendations = notification_manager.get_budget_recommendations()
    print(f"\nРекомендации:")
    for rec in recommendations:
        print(f"  {rec}")

def example_analytics():
    """Пример аналитики"""
    print("\n=== Пример аналитики ===")
    
    # Получение расходов за разные периоды
    today_start, today_end = get_date_range("today")
    week_start, week_end = get_date_range("week")
    month_start, month_end = get_date_range("month")
    
    print(f"Периоды:")
    print(f"  Сегодня: {today_start} - {today_end}")
    print(f"  Неделя: {week_start} - {week_end}")
    print(f"  Месяц: {month_start} - {month_end}")
    
    # Статистика по категориям
    category_stats = db_manager.get_expenses_by_category()
    total = sum(category_stats.values())
    
    print(f"\nСтатистика по категориям (всего: {format_currency(total)}):")
    for category, amount in sorted(category_stats.items(), key=lambda x: x[1], reverse=True):
        percentage = (amount / total) * 100 if total > 0 else 0
        print(f"  {category}: {format_currency(amount)} ({percentage:.1f}%)")

def example_utilities():
    """Пример использования утилит"""
    print("\n=== Пример использования утилит ===")
    
    # Форматирование валюты
    print(f"Форматирование валюты:")
    print(f"  1234.56 -> {format_currency(1234.56)}")
    print(f"  0.99 -> {format_currency(0.99)}")
    
    # Форматирование даты
    print(f"\nФорматирование даты:")
    date_str = "2024-01-15 14:30:00"
    formatted = format_date(date_str)
    print(f"  {date_str} -> {formatted}")
    
    # Валидация суммы
    print(f"\nВалидация суммы:")
    test_amounts = ["100.50", "0", "-10", "abc", "1000001"]
    for amount in test_amounts:
        valid, value, error = validate_amount(amount)
        print(f"  {amount}: {'✓' if valid else '✗'} {value} {error}")

def main():
    """Главная функция с примерами"""
    try:
        print("🚀 Примеры использования трекера расходов")
        print("=" * 50)
        
        example_basic_usage()
        example_reports()
        example_notifications()
        example_analytics()
        example_utilities()
        
        print("\n✅ Все примеры выполнены успешно!")
        
    except Exception as e:
        logger.error(f"Ошибка в примерах: {e}")
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    main()

