"""
Утилиты для трекера расходов
"""

import os
import shutil
from datetime import datetime, timedelta
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

def format_currency(amount: float, currency: str = "₽") -> str:
    """Форматирование валюты"""
    return f"{amount:.2f} {currency}"

def format_date(date_str: str, input_format: str = "%Y-%m-%d %H:%M:%S", 
                output_format: str = "%d.%m.%Y %H:%M") -> str:
    """Форматирование даты"""
    try:
        date_obj = datetime.strptime(date_str, input_format)
        return date_obj.strftime(output_format)
    except ValueError as e:
        logger.error(f"Ошибка форматирования даты: {e}")
        return date_str

def format_percentage(value: float, total: float) -> str:
    """Форматирование процентов"""
    if total == 0:
        return "0.0%"
    percentage = (value / total) * 100
    return f"{percentage:.1f}%"

def get_date_range(period: str = "month") -> tuple:
    """Получение диапазона дат для различных периодов"""
    now = datetime.now()
    
    if period == "today":
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end = now.replace(hour=23, minute=59, second=59, microsecond=999999)
    elif period == "week":
        start = now - timedelta(days=now.weekday())
        start = start.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=6, hours=23, minutes=59, seconds=59)
    elif period == "month":
        start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if now.month == 12:
            end = now.replace(year=now.year + 1, month=1, day=1) - timedelta(microseconds=1)
        else:
            end = now.replace(month=now.month + 1, day=1) - timedelta(microseconds=1)
    elif period == "year":
        start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        end = now.replace(year=now.year + 1, month=1, day=1) - timedelta(microseconds=1)
    else:
        raise ValueError(f"Неподдерживаемый период: {period}")
    
    return start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")

def create_backup(source_file: str, backup_dir: str = "backups") -> str:
    """Создание резервной копии файла"""
    try:
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.basename(source_file)
        name, ext = os.path.splitext(filename)
        backup_filename = f"{name}_backup_{timestamp}{ext}"
        backup_path = os.path.join(backup_dir, backup_filename)
        
        shutil.copy2(source_file, backup_path)
        logger.info(f"Создана резервная копия: {backup_path}")
        return backup_path
    except Exception as e:
        logger.error(f"Ошибка создания резервной копии: {e}")
        raise

def cleanup_old_backups(backup_dir: str = "backups", max_files: int = 10):
    """Очистка старых резервных копий"""
    try:
        if not os.path.exists(backup_dir):
            return
        
        files = []
        for filename in os.listdir(backup_dir):
            if filename.endswith('.db') and 'backup' in filename:
                filepath = os.path.join(backup_dir, filename)
                files.append((filepath, os.path.getmtime(filepath)))
        
        # Сортируем по времени модификации (новые первыми)
        files.sort(key=lambda x: x[1], reverse=True)
        
        # Удаляем старые файлы
        for filepath, _ in files[max_files:]:
            os.remove(filepath)
            logger.info(f"Удален старый бэкап: {filepath}")
            
    except Exception as e:
        logger.error(f"Ошибка очистки старых бэкапов: {e}")

def validate_amount(amount: str) -> tuple[bool, float, str]:
    """Валидация суммы"""
    try:
        value = float(amount)
        if value <= 0:
            return False, 0.0, "Сумма должна быть положительной"
        if value > 1000000:
            return False, 0.0, "Сумма слишком большая (максимум 1,000,000)"
        return True, value, ""
    except ValueError:
        return False, 0.0, "Некорректный формат суммы"

def validate_category(category: str) -> tuple[bool, str]:
    """Валидация категории"""
    if not category or not category.strip():
        return False, "Категория не может быть пустой"
    if len(category) > 100:
        return False, "Название категории слишком длинное (максимум 100 символов)"
    return True, ""

def validate_payment_method(method: str) -> tuple[bool, str]:
    """Валидация способа оплаты"""
    if not method or not method.strip():
        return False, "Способ оплаты не может быть пустым"
    return True, ""

def get_file_size_mb(filepath: str) -> float:
    """Получение размера файла в мегабайтах"""
    try:
        size_bytes = os.path.getsize(filepath)
        return size_bytes / (1024 * 1024)
    except OSError:
        return 0.0

def is_database_corrupted(db_path: str) -> bool:
    """Проверка целостности базы данных"""
    try:
        import sqlite3
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("PRAGMA integrity_check")
        result = cursor.fetchone()
        conn.close()
        return result[0] != "ok"
    except Exception:
        return True

def get_system_info() -> Dict[str, Any]:
    """Получение информации о системе"""
    import platform
    import sys
    
    return {
        'platform': platform.platform(),
        'python_version': sys.version,
        'architecture': platform.architecture()[0],
        'processor': platform.processor(),
        'machine': platform.machine()
    }

def calculate_trend(current: float, previous: float) -> Dict[str, Any]:
    """Расчет тренда между двумя значениями"""
    if previous == 0:
        return {
            'direction': 'new',
            'percentage': 0,
            'change': current,
            'description': 'Новые данные'
        }
    
    change = current - previous
    percentage = (change / previous) * 100
    
    if change > 0:
        direction = 'up'
        description = f'Рост на {abs(percentage):.1f}%'
    elif change < 0:
        direction = 'down'
        description = f'Снижение на {abs(percentage):.1f}%'
    else:
        direction = 'stable'
        description = 'Без изменений'
    
    return {
        'direction': direction,
        'percentage': abs(percentage),
        'change': change,
        'description': description
    }

def group_by_period(data: List[tuple], period: str = "day") -> Dict[str, List[tuple]]:
    """Группировка данных по периоду"""
    grouped = {}
    
    for item in data:
        if len(item) < 1:
            continue
            
        date_str = item[0]  # Предполагаем, что дата в первом элементе
        try:
            date_obj = datetime.strptime(date_str.split(' ')[0], "%Y-%m-%d")
            
            if period == "day":
                key = date_obj.strftime("%Y-%m-%d")
            elif period == "week":
                week_start = date_obj - timedelta(days=date_obj.weekday())
                key = week_start.strftime("%Y-%m-%d")
            elif period == "month":
                key = date_obj.strftime("%Y-%m")
            elif period == "year":
                key = date_obj.strftime("%Y")
            else:
                key = date_obj.strftime("%Y-%m-%d")
            
            if key not in grouped:
                grouped[key] = []
            grouped[key].append(item)
            
        except ValueError:
            continue
    
    return grouped

def export_to_csv(data: List[tuple], headers: List[str], filename: str) -> bool:
    """Экспорт данных в CSV файл"""
    try:
        import csv
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(headers)
            writer.writerows(data)
        
        logger.info(f"Данные экспортированы в {filename}")
        return True
    except Exception as e:
        logger.error(f"Ошибка экспорта в CSV: {e}")
        return False

def get_color_for_category(category: str) -> str:
    """Получение цвета для категории на основе её названия"""
    colors = [
        '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7',
        '#DDA0DD', '#8B4513', '#A0522D', '#FFD700', '#32CD32',
        '#FF69B4', '#FF1493', '#00CED1', '#696969', '#FF4500',
        '#9370DB', '#20B2AA', '#CD853F', '#DC143C', '#4169E1'
    ]
    
    # Простой хэш для получения стабильного цвета
    hash_value = hash(category) % len(colors)
    return colors[hash_value]

