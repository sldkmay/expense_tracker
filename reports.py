import sqlite3
from collections import defaultdict
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
import logging
from database import db_manager

logger = logging.getLogger(__name__)

REPORT_FILE = "monthly_report.txt"

class ReportGenerator:
    """Класс для генерации различных отчетов"""
    
    def __init__(self):
        self.db_manager = db_manager
    
    def generate_monthly_report(self, year: int = None, month: int = None) -> str:
        """Генерация месячного отчета"""
        try:
            if year is None or month is None:
                now = datetime.now()
                year = now.year
                month = now.month
            
            # Получаем расходы за месяц
            expenses = self.db_manager.get_monthly_expenses(year, month)
            
            # Анализируем данные
            analysis = self._analyze_expenses(expenses)
            
            # Генерируем отчет
            report_content = self._format_monthly_report(year, month, analysis)
            
            # Сохраняем в файл
            self._save_report_to_file(report_content, f"monthly_report_{year}_{month:02d}.txt")
            
            return f"Отчет за {year}-{month:02d} создан: monthly_report_{year}_{month:02d}.txt"
            
        except Exception as e:
            logger.error(f"Ошибка генерации месячного отчета: {e}")
            raise
    
    def generate_weekly_report(self, start_date: str = None) -> str:
        """Генерация недельного отчета"""
        try:
            if start_date is None:
                start_date = datetime.now().strftime("%Y-%m-%d")
            
            end_date = (datetime.strptime(start_date, "%Y-%m-%d") + timedelta(days=6)).strftime("%Y-%m-%d")
            
            expenses = self.db_manager.get_expenses(start_date=start_date, end_date=end_date)
            analysis = self._analyze_expenses(expenses)
            
            report_content = self._format_weekly_report(start_date, end_date, analysis)
            self._save_report_to_file(report_content, f"weekly_report_{start_date}.txt")
            
            return f"Недельный отчет создан: weekly_report_{start_date}.txt"
            
        except Exception as e:
            logger.error(f"Ошибка генерации недельного отчета: {e}")
            raise
    
    def generate_category_analysis(self, start_date: str = None, end_date: str = None) -> Dict:
        """Анализ расходов по категориям"""
        try:
            expenses = self.db_manager.get_expenses(start_date=start_date, end_date=end_date)
            return self._analyze_expenses(expenses)
            
        except Exception as e:
            logger.error(f"Ошибка анализа по категориям: {e}")
            raise
    
    def generate_payment_method_analysis(self, start_date: str = None, end_date: str = None) -> Dict:
        """Анализ расходов по способам оплаты"""
        try:
            expenses = self.db_manager.get_expenses(start_date=start_date, end_date=end_date)
            
            payment_totals = defaultdict(float)
            total = 0.0
            
            for date, amount, category, payment_method, description, expense_id in expenses:
                payment_totals[payment_method] += amount
                total += amount
            
            return {
                'payment_methods': dict(payment_totals),
                'total': total,
                'count': len(expenses)
            }
            
        except Exception as e:
            logger.error(f"Ошибка анализа по способам оплаты: {e}")
            raise
    
    def generate_daily_breakdown(self, start_date: str = None, end_date: str = None) -> Dict:
        """Разбивка расходов по дням"""
        try:
            expenses = self.db_manager.get_expenses(start_date=start_date, end_date=end_date)
            
            daily_totals = defaultdict(float)
            daily_categories = defaultdict(lambda: defaultdict(float))
            
            for date, amount, category, payment_method, description, expense_id in expenses:
                day = date.split(' ')[0]  # Берем только дату без времени
                daily_totals[day] += amount
                daily_categories[day][category] += amount
            
            return {
                'daily_totals': dict(daily_totals),
                'daily_categories': dict(daily_categories)
            }
            
        except Exception as e:
            logger.error(f"Ошибка генерации разбивки по дням: {e}")
            raise
    
    def _analyze_expenses(self, expenses: List[Tuple]) -> Dict:
        """Анализ списка расходов"""
        expenses_by_category = defaultdict(float)
        expenses_by_payment_method = defaultdict(float)
        total = 0.0
        count = len(expenses)
        
        for date, amount, category, payment_method, description, expense_id in expenses:
            expenses_by_category[category] += amount
            expenses_by_payment_method[payment_method] += amount
            total += amount
        
        # Сортируем по убыванию суммы
        sorted_categories = sorted(expenses_by_category.items(), key=lambda x: x[1], reverse=True)
        sorted_payment_methods = sorted(expenses_by_payment_method.items(), key=lambda x: x[1], reverse=True)
        
        return {
            'categories': dict(expenses_by_category),
            'sorted_categories': sorted_categories,
            'payment_methods': dict(expenses_by_payment_method),
            'sorted_payment_methods': sorted_payment_methods,
            'total': total,
            'count': count,
            'average': total / count if count > 0 else 0
        }
    
    def _format_monthly_report(self, year: int, month: int, analysis: Dict) -> str:
        """Форматирование месячного отчета"""
        month_names = [
            "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
            "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"
        ]
        
        report = []
        report.append("=" * 50)
        report.append(f"📊 ОТЧЕТ ЗА {month_names[month-1].upper()} {year}")
        report.append("=" * 50)
        report.append("")
        
        # Общая статистика
        report.append("💰 ОБЩАЯ СТАТИСТИКА:")
        report.append(f"   Всего расходов: {analysis['total']:.2f} ₽")
        report.append(f"   Количество транзакций: {analysis['count']}")
        report.append(f"   Средний чек: {analysis['average']:.2f} ₽")
        report.append("")
        
        # Расходы по категориям
        if analysis['sorted_categories']:
            report.append("📂 РАСХОДЫ ПО КАТЕГОРИЯМ:")
            for category, amount in analysis['sorted_categories']:
                percentage = (amount / analysis['total']) * 100 if analysis['total'] > 0 else 0
                report.append(f"   {category}: {amount:.2f} ₽ ({percentage:.1f}%)")
            report.append("")
        
        # Расходы по способам оплаты
        if analysis['sorted_payment_methods']:
            report.append("💳 РАСХОДЫ ПО СПОСОБАМ ОПЛАТЫ:")
            for method, amount in analysis['sorted_payment_methods']:
                percentage = (amount / analysis['total']) * 100 if analysis['total'] > 0 else 0
                report.append(f"   {method}: {amount:.2f} ₽ ({percentage:.1f}%)")
            report.append("")
        
        
        report.append("=" * 50)
        report.append(f"Отчет сгенерирован: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
        report.append("=" * 50)
        
        return "\n".join(report)
    
    def _format_weekly_report(self, start_date: str, end_date: str, analysis: Dict) -> str:
        """Форматирование недельного отчета"""
        report = []
        report.append("=" * 50)
        report.append(f"📊 НЕДЕЛЬНЫЙ ОТЧЕТ ({start_date} - {end_date})")
        report.append("=" * 50)
        report.append("")
        
        # Общая статистика
        report.append("💰 ОБЩАЯ СТАТИСТИКА:")
        report.append(f"   Всего расходов: {analysis['total']:.2f} ₽")
        report.append(f"   Количество транзакций: {analysis['count']}")
        report.append(f"   Средний чек: {analysis['average']:.2f} ₽")
        report.append(f"   Среднедневные расходы: {analysis['total'] / 7:.2f} ₽")
        report.append("")
        
        # Расходы по категориям
        if analysis['sorted_categories']:
            report.append("📂 РАСХОДЫ ПО КАТЕГОРИЯМ:")
            for category, amount in analysis['sorted_categories']:
                percentage = (amount / analysis['total']) * 100 if analysis['total'] > 0 else 0
                report.append(f"   {category}: {amount:.2f} ₽ ({percentage:.1f}%)")
        
        return "\n".join(report)
    
    def _save_report_to_file(self, content: str, filename: str):
        """Сохранение отчета в файл"""
        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(content)
            logger.info(f"Отчет сохранен в файл: {filename}")
        except Exception as e:
            logger.error(f"Ошибка сохранения отчета: {e}")
            raise

# Создаем глобальный экземпляр генератора отчетов
report_generator = ReportGenerator()

# Функции для обратной совместимости
def generate_monthly_report():
    return report_generator.generate_monthly_report()