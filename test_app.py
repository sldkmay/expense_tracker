"""
Простой тест приложения
"""

import sys
import os

# Добавляем текущую директорию в путь
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_database():
    """Тест базы данных"""
    try:
        from database import db_manager
        
        print("🧪 Тестирование базы данных...")
        
        # Инициализация
        db_manager.init_database()
        print("✅ База данных инициализирована")
        
        # Добавление тестовых данных
        user_id = db_manager.add_user("test_user")
        print(f"✅ Пользователь создан: {user_id}")
        
        category_id = db_manager.add_category("Тест", "#FF0000")
        print(f"✅ Категория создана: {category_id}")
        
        payment_id = db_manager.add_payment_method("💳 Тест", "💳")
        print(f"✅ Способ оплаты создан: {payment_id}")
        
        # Добавление расхода
        expense_id = db_manager.add_expense(user_id, category_id, payment_id, 100.50, "Тестовый расход")
        print(f"✅ Расход добавлен: {expense_id}")
        
        # Получение расходов
        expenses = db_manager.get_expenses()
        print(f"✅ Получено расходов: {len(expenses)}")
        
        for expense in expenses:
            print(f"   {expense}")
        
        print("✅ Все тесты базы данных прошли успешно!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка в тестах базы данных: {e}")
        return False

def test_reports():
    """Тест отчетов"""
    try:
        from reports import report_generator
        
        print("\n🧪 Тестирование отчетов...")
        
        # Месячный отчет
        report = report_generator.generate_monthly_report()
        print(f"✅ Месячный отчет: {report}")
        
        # Анализ по категориям
        analysis = report_generator.generate_category_analysis()
        print(f"✅ Анализ по категориям: {len(analysis.get('insights', {}))} категорий")
        
        print("✅ Все тесты отчетов прошли успешно!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка в тестах отчетов: {e}")
        return False

def test_notifications():
    """Тест уведомлений"""
    try:
        from notifications import notification_manager
        
        print("\n🧪 Тестирование уведомлений...")
        
        # Проверка лимитов
        warnings = notification_manager.check_spending_limits()
        print(f"✅ Проверка лимитов: {len(warnings)} предупреждений")
        
        # Прогноз
        forecast = notification_manager.get_spending_forecast()
        if forecast:
            print(f"✅ Прогноз: {forecast.get('total_spent', 0):.2f} ₽")
        
        print("✅ Все тесты уведомлений прошли успешно!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка в тестах уведомлений: {e}")
        return False

def main():
    """Главная функция тестирования"""
    print("🚀 Запуск тестов приложения...")
    print("=" * 50)
    
    tests = [
        test_database,
        test_reports,
        test_notifications
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Результаты тестирования: {passed}/{total} тестов прошли успешно")
    
    if passed == total:
        print("🎉 Все тесты прошли успешно! Приложение готово к использованию.")
    else:
        print("⚠️ Некоторые тесты не прошли. Проверьте ошибки выше.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

