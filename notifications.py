import sqlite3
from collections import defaultdict
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
import logging
from database import db_manager

logger = logging.getLogger(__name__)

class NotificationManager:
    """Класс для управления уведомлениями и лимитами расходов"""
    
    def __init__(self):
        self.db_manager = db_manager
        self.default_limits = {
            "Кофе": 1000,
            "Еда": 5000,
            "Развлечения": 2000,
            "Транспорт": 3000,
            "Покупки": 10000,
            "Здоровье": 2000,
            "Образование": 5000
        }
    
    def check_spending_limits(self, user_id: int = None, 
                            custom_limits: Dict[str, float] = None) -> List[str]:
        """Проверка превышения лимитов расходов"""
        try:
            limits = custom_limits or self.default_limits
            current_month = datetime.now().strftime("%Y-%m")
            
            # Получаем расходы за текущий месяц
            expenses = self.db_manager.get_expenses(
                user_id=user_id,
                start_date=f"{current_month}-01",
                end_date=f"{current_month}-31"
            )
            
            # Группируем расходы по категориям
            spending = defaultdict(float)
            for date, amount, category, payment_method, description, expense_id in expenses:
                spending[category] += amount
            
            # Проверяем лимиты
            warnings = []
            for category, limit in limits.items():
                if spending[category] > limit:
                    overage = spending[category] - limit
                    percentage = (spending[category] / limit) * 100
                    
                    if percentage > 200:  # Превышение более чем в 2 раза
                        message = f"🚨 КРИТИЧЕСКОЕ превышение! Категория '{category}': {spending[category]:.2f} ₽ (лимит: {limit} ₽, превышение на {overage:.2f} ₽)"
                    elif percentage > 150:  # Превышение более чем в 1.5 раза
                        message = f"⚠️ Серьезное превышение! Категория '{category}': {spending[category]:.2f} ₽ (лимит: {limit} ₽, превышение на {overage:.2f} ₽)"
                    else:
                        message = f"⚠️ Превышен лимит по категории '{category}': {spending[category]:.2f} ₽ (лимит: {limit} ₽, превышение на {overage:.2f} ₽)"
                    
                    warnings.append(message)
            
            # Дополнительные проверки
            warnings.extend(self._check_daily_spending(expenses))
            warnings.extend(self._check_weekly_trends(expenses))
            
            return warnings
            
        except Exception as e:
            logger.error(f"Ошибка проверки лимитов: {e}")
            return [f"Ошибка проверки лимитов: {e}"]
    
    def _check_daily_spending(self, expenses: List[Tuple]) -> List[str]:
        """Проверка дневных расходов"""
        warnings = []
        daily_totals = defaultdict(float)
        
        for date, amount, category, payment_method, description, expense_id in expenses:
            day = date.split(' ')[0]
            daily_totals[day] += amount
        
        # Проверяем, если в какой-то день потрачено больше 5000 рублей
        for day, total in daily_totals.items():
            if total > 5000:
                warnings.append(f"💸 Высокие дневные расходы {day}: {total:.2f} ₽")
        
        return warnings
    
    def _check_weekly_trends(self, expenses: List[Tuple]) -> List[str]:
        """Проверка недельных трендов"""
        warnings = []
        
        # Группируем по неделям
        weekly_totals = defaultdict(float)
        for date, amount, category, payment_method, description, expense_id in expenses:
            date_obj = datetime.strptime(date.split(' ')[0], "%Y-%m-%d")
            week_start = date_obj - timedelta(days=date_obj.weekday())
            week_key = week_start.strftime("%Y-%m-%d")
            weekly_totals[week_key] += amount
        
        # Проверяем, если недельные расходы превышают 20000 рублей
        for week, total in weekly_totals.items():
            if total > 20000:
                warnings.append(f"📈 Высокие недельные расходы ({week}): {total:.2f} ₽")
        
        return warnings
    
    def get_spending_forecast(self, user_id: int = None) -> Dict:
        """Прогноз расходов на основе текущих данных"""
        try:
            current_month = datetime.now().strftime("%Y-%m")
            current_day = datetime.now().day
            
            # Получаем расходы за текущий месяц
            expenses = self.db_manager.get_expenses(
                user_id=user_id,
                start_date=f"{current_month}-01",
                end_date=f"{current_month}-31"
            )
            
            total_spent = sum(amount for date, amount, category, payment_method, description, expense_id in expenses)
            
            # Рассчитываем прогноз
            days_in_month = 30  # Упрощенный расчет
            daily_average = total_spent / current_day if current_day > 0 else 0
            forecast = daily_average * days_in_month
            
            return {
                'total_spent': total_spent,
                'daily_average': daily_average,
                'forecast': forecast,
                'days_passed': current_day,
                'days_remaining': days_in_month - current_day
            }
            
        except Exception as e:
            logger.error(f"Ошибка расчета прогноза: {e}")
            return {}
    
    def get_category_insights(self, user_id: int = None) -> Dict:
        """Анализ расходов по категориям с инсайтами"""
        try:
            current_month = datetime.now().strftime("%Y-%m")
            expenses = self.db_manager.get_expenses(
                user_id=user_id,
                start_date=f"{current_month}-01",
                end_date=f"{current_month}-31"
            )
            
            category_totals = defaultdict(float)
            category_counts = defaultdict(int)
            
            for date, amount, category, payment_method, description, expense_id in expenses:
                category_totals[category] += amount
                category_counts[category] += 1
            
            total_spent = sum(category_totals.values())
            insights = {}
            
            for category, total in category_totals.items():
                percentage = (total / total_spent) * 100 if total_spent > 0 else 0
                avg_transaction = total / category_counts[category] if category_counts[category] > 0 else 0
                
                insights[category] = {
                    'total': total,
                    'percentage': percentage,
                    'count': category_counts[category],
                    'average': avg_transaction
                }
            
            return {
                'insights': insights,
                'total_spent': total_spent,
                'most_expensive': max(category_totals.items(), key=lambda x: x[1]) if category_totals else None,
                'most_frequent': max(category_counts.items(), key=lambda x: x[1]) if category_counts else None
            }
            
        except Exception as e:
            logger.error(f"Ошибка анализа категорий: {e}")
            return {}
    
    def get_budget_recommendations(self, user_id: int = None) -> List[str]:
        """Рекомендации по бюджету на основе анализа расходов"""
        try:
            insights = self.get_category_insights(user_id)
            forecast = self.get_spending_forecast(user_id)
            
            recommendations = []
            
            if not insights or not forecast:
                return ["Недостаточно данных для рекомендаций"]
            
            # Анализ прогноза
            if forecast['forecast'] > 50000:
                recommendations.append("💡 Рекомендация: Ваши расходы могут превысить 50,000 ₽ в месяц. Рассмотрите возможность сокращения трат.")
            
            # Анализ категорий
            for category, data in insights['insights'].items():
                if data['percentage'] > 40:
                    recommendations.append(f"💡 Категория '{category}' составляет {data['percentage']:.1f}% от всех расходов. Возможно, стоит пересмотреть приоритеты.")
                
                if data['average'] > 5000:
                    recommendations.append(f"💡 Средний чек в категории '{category}' составляет {data['average']:.2f} ₽. Рассмотрите более бюджетные варианты.")
            
            # Анализ частоты покупок
            if insights['most_frequent']:
                category, count = insights['most_frequent']
                if count > 10:
                    recommendations.append(f"💡 В категории '{category}' было {count} покупок за месяц. Возможно, стоит планировать покупки заранее.")
            
            return recommendations if recommendations else ["✅ Ваши расходы выглядят разумно!"]
            
        except Exception as e:
            logger.error(f"Ошибка генерации рекомендаций: {e}")
            return [f"Ошибка генерации рекомендаций: {e}"]

# Создаем глобальный экземпляр менеджера уведомлений
notification_manager = NotificationManager()

# Функции для обратной совместимости
def check_spending_limits():
    return notification_manager.check_spending_limits()