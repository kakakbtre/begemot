import json
import os
from datetime import datetime
from typing import List, Optional
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Декоратор для проверки корректности ввода
def validate_input(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            print(f"❌ Ошибка ввода: {e}")
            return None
        except Exception as e:
            print(f"❌ Непредвиденная ошибка: {e}")
            return None
    return wrapper

# Базовый класс для погодных явлений
class WeatherType:
    def __init__(self, description: str, precipitation: float):
        self._description = description
        self._precipitation = max(0, precipitation) # инкапсуляция
    
    @property
    def description(self):
        return self._description
    
    @property
    def precipitation(self):
        return self._precipitation
    
    def get_info(self) -> str:
        return f"{self._description}, осадки: {self._precipitation} мм"
    
    def __str__(self):
        return self.get_info()

# Наследование - разные типы погоды
class SunnyWeather(WeatherType):
    def __init__(self, precipitation: float = 0):
        super().__init__("☀️ Солнечно", precipitation)
    
    def get_info(self) -> str:
        return f"{self.description} 🌞 (осадки: {self.precipitation} мм)"

class RainyWeather(WeatherType):
    def __init__(self, precipitation: float):
        super().__init__("🌧️ Дождливо", precipitation)
    
    def get_info(self) -> str:
        intensity = "слабый" if self.precipitation < 5 else "сильный" if self.precipitation > 15 else "умеренный"
        return f"{self.description} ({intensity} дождь, {self.precipitation} мм)"

class CloudyWeather(WeatherType):
    def __init__(self, precipitation: float = 0):
        super().__init__("☁️ Облачно", precipitation)
    
    def get_info(self) -> str:
        return f"{self.description} (осадки: {self.precipitation} мм)"

class SnowyWeather(WeatherType):
    def __init__(self, precipitation: float):
        super().__init__("❄️ Снежно", precipitation)
    
    def get_info(self) -> str:
        return f"{self.description} (снегопад, {self.precipitation} мм)"

# Модель данных WeatherEntry
class WeatherEntry:
    def __init__(self, date: datetime, temperature: float, weather: WeatherType):
        self._date = date
        self._temperature = temperature
        self._weather = weather
    
    @property
    def date(self) -> datetime:
        return self._date
    
    @property
    def temperature(self) -> float:
        return self._temperature
    
    @property
    def weather(self) -> WeatherType:
        return self._weather
    
    def to_dict(self) -> dict:
        """Преобразование в словарь для JSON"""
        return {
            "date": self._date.strftime("%Y-%m-%d"),
            "temperature": self._temperature,
            "weather_type": self._weather.__class__.__name__,
            "description": self._weather.description,
            "precipitation": self._weather.precipitation
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'WeatherEntry':
        """Создание объекта из словаря"""
        date = datetime.strptime(data["date"], "%Y-%m-%d")
        temperature = data["temperature"]
        
        # Создание объекта погоды в зависимости от типа
        weather_classes = {
            "SunnyWeather": SunnyWeather,
            "RainyWeather": RainyWeather,
            "CloudyWeather": CloudyWeather,
            "SnowyWeather": SnowyWeather
        }
        
        weather_class = weather_classes.get(data["weather_type"], CloudyWeather)
        if data["weather_type"] in ["RainyWeather", "SnowyWeather"]:
            weather = weather_class(data["precipitation"])
        else:
            weather = weather_class(data["precipitation"])
        
        return cls(date, temperature, weather)
    
    def __str__(self):
        return f"{self._date.strftime('%d.%m.%Y')} | {self._temperature:+.1f}°C | {self._weather}"

# Основной класс приложения
class WeatherDiary:
    def __init__(self, filename: str = "weather_diary.json"):
        self._filename = filename
        self._entries: List[WeatherEntry] = []
        self._load_data()
    
    def _load_data(self):
        """Загрузка данных из JSON файла"""
        if os.path.exists(self._filename):
            try:
                with open(self._filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self._entries = [WeatherEntry.from_dict(entry) for entry in data]
                print(f"✅ Загружено {len(self._entries)} записей")
            except Exception as e:
                print(f"⚠️ Ошибка загрузки данных: {e}")
                self._entries = []
        else:
            print("📝 Создан новый дневник погоды")
    
    def _save_data(self):
        """Сохранение данных в JSON файл"""
        try:
            data = [entry.to_dict() for entry in self._entries]
            with open(self._filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"❌ Ошибка сохранения: {e}")
            return False
    
    @validate_input
    def add_entry(self, date_str: str, temp_str: str, weather_type: str, precipitation: str = "0"):
        """Добавление новой записи"""
        # Валидация даты
        try:
            date = datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Неверный формат даты. Используйте ГГГГ-ММ-ДД")
        
        # Проверка на дубликат даты
        if any(entry.date.date() == date.date() for entry in self._entries):
            raise ValueError(f"Запись на {date_str} уже существует")
        
        # Валидация температуры
        try:
            temperature = float(temp_str)
            if temperature < -50 or temperature > 50:
                raise ValueError("Температура должна быть в диапазоне от -50 до +50°C")
        except ValueError:
            raise ValueError("Неверный формат температуры. Используйте число")
        
        # Валидация осадков
        try:
            precipitation_val = float(precipitation) if precipitation else 0
            if precipitation_val < 0:
                raise ValueError("Осадки не могут быть отрицательными")
        except ValueError:
            raise ValueError("Неверный формат осадков")
        
        # Создание объекта погоды
        weather_types = {
            "1": ("sunny", SunnyWeather),
            "2": ("rainy", RainyWeather),
            "3": ("cloudy", CloudyWeather),
            "4": ("snowy", SnowyWeather)
        }
        
        if weather_type not in weather_types:
            raise ValueError("Неверный тип погоды")
        
        weather_obj = weather_types[weather_type][1](precipitation_val)
        
        # Добавление записи
        entry = WeatherEntry(date, temperature, weather_obj)
        self._entries.append(entry)
        self._entries.sort(key=lambda x: x.date)
        
        if self._save_data():
            print(f"✅ Запись добавлена: {entry}")
            return True
        return False
    
    def view_entries(self, entries: Optional[List[WeatherEntry]] = None):
        """Просмотр записей"""
        display_entries = entries if entries is not None else self._entries
        
        if not display_entries:
            print("📭 Нет записей в дневнике")
            return
        
        print("\n" + "=" * 60)
        print(f"{'Дата':<12} {'Температура':<12} {'Погода':<30}")
        print("=" * 60)
        
        for entry in display_entries:
            print(f"{entry.date.strftime('%d.%m.%Y'):<12} {entry.temperature:>+5.1f}°C {entry.weather}")
        
        print("=" * 60)
        print(f"Всего записей: {len(display_entries)}")
    
    @validate_input
    def delete_entry(self, date_str: str):
        """Удаление записи по дате"""
        try:
            target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError("Неверный формат даты. Используйте ГГГГ-ММ-ДД")
        
        initial_count = len(self._entries)
        self._entries = [e for e in self._entries if e.date.date() != target_date]
        
        if len(self._entries) < initial_count:
            if self._save_data():
                print(f"✅ Запись на {date_str} удалена")
            else:
                print("❌ Ошибка при сохранении после удаления")
        else:
            print(f"❌ Запись на {date_str} не найдена")
    
    def filter_by_date(self, start_date_str: str, end_date_str: str):
        """Фильтрация по диапазону дат"""
        try:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
        except ValueError:
            print("❌ Неверный формат даты. Используйте ГГГГ-ММ-ДД")
            return None
        
        filtered = [e for e in self._entries if start_date <= e.date <= end_date]
        
        if filtered:
            print(f"\n🔍 Записи с {start_date_str} по {end_date_str}:")
            self.view_entries(filtered)
        else:
            print(f"📭 Нет записей в указанном диапазоне")
        
        return filtered
    
    def filter_by_temperature(self, min_temp_str: str, max_temp_str: str):
        """Фильтрация по диапазону температур"""
        try:
            min_temp = float(min_temp_str)
            max_temp = float(max_temp_str)
        except ValueError:
            print("❌ Неверный формат температуры. Используйте числа")
            return None
        
        filtered = [e for e in self._entries if min_temp <= e.temperature <= max_temp]
        
        if filtered:
            print(f"\n🔍 Записи с температурой от {min_temp} до {max_temp}°C:")
            self.view_entries(filtered)
        else:
            print(f"📭 Нет записей в указанном диапазоне температур")
        
        return filtered
    
    def plot_temperature_graph(self):
        """Построение графика температуры"""
        if not self._entries:
            print("📭 Нет данных для построения графика")
            return
        
        # Подготовка данных
        dates = [entry.date for entry in self._entries]
        temperatures = [entry.temperature for entry in self._entries]
        
        # Создание графика
        plt.figure(figsize=(12, 6))
        plt.plot(dates, temperatures, marker='o', linestyle='-', linewidth=2, markersize=6, color='#FF6B6B')
        
        # Настройка графика
        plt.title('🌡️ График температуры по дням', fontsize=16, fontweight='bold')
        plt.xlabel('Дата', fontsize=12)
        plt.ylabel('Температура (°C)', fontsize=12)
        plt.grid(True, alpha=0.3, linestyle='--')
        
        # Форматирование оси дат
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d.%m.%Y'))
        plt.gcf().autofmt_xdate() # Поворот подписей для читаемости
        
        # Добавление значений на график
        for i, (date, temp) in enumerate(zip(dates, temperatures)):
            plt.annotate(f'{temp:.1f}°C', 
                        (date, temp), 
                        textcoords="offset points", 
                        xytext=(0, 10), 
                        ha='center',
                        fontsize=9,
                        bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.7))
        
        # Добавление горизонтальной линии 0°C
        plt.axhline(y=0, color='blue', linestyle='-', alpha=0.3, linewidth=1)
        
        # Заливка области
        plt.fill_between(dates, temperatures, 0, alpha=0.2, color='#FF6B6B')
        
        plt.tight_layout()
        plt.show()
        
        # Статистика
        avg_temp = sum(temperatures) / len(temperatures)
        max_temp = max(temperatures)
        min_temp = min(temperatures)
        
        print(f"\n📊 Статистика:")
        print(f" Средняя температура: {avg_temp:.1f}°C")
        print(f" Максимальная: {max_temp:+.1f}°C")
        print(f" Минимальная: {min_temp:+.1f}°C")
        print(f" Количество дней: {len(temperatures)}")

# Функция для отображения меню
def display_menu():
    print("\n" + "=" * 50)
    print(" 🌤️ WEATHER DIARY 🌧️")
    print("=" * 50)
    print("1. ➕ Добавить запись")
    print("2. 📋 Просмотреть все записи")
    print("3. 🗑️ Удалить запись")
    print("4. 🔍 Фильтр по дате")
    print("5. 🔍 Фильтр по температуре")
    print("6. 📈 Построить график температуры")
    print("7. 💾 Сохранить данные")
    print("8. 🚪 Выход")
    print("=" * 50)

# Главная функция
def main():
    diary = WeatherDiary()
    
    while True:
        display_menu()
        choice = input("\nВыберите действие (1-8): ").strip()
        
        if choice == "1":
            print("\n📝 Добавление новой записи:")
            date = input("Дата (ГГГГ-ММ-ДД): ").strip()
            temp = input("Температура (°C): ").strip()
            
            print("\nТип погоды:")
            print("1. ☀️ Солнечно")
            print("2. 🌧️ Дождливо")
            print("3. ☁️ Облачно")
            print("4. ❄️ Снежно")
            
            weather_type = input("Выберите тип (1-4): ").strip()
            precipitation = input("Количество осадков (мм, по умолчанию 0): ").strip()
            
            diary.add_entry(date, temp, weather_type, precipitation if precipitation else "0")
            
        elif choice == "2":
            diary.view_entries()
            
        elif choice == "3":
            date = input("Дата для удаления (ГГГГ-ММ-ДД): ").strip()
            diary.delete_entry(date)
            
        elif choice == "4":
            start = input("Начальная дата (ГГГГ-ММ-ДД): ").strip()
            end = input("Конечная дата (ГГГГ-ММ-ДД): ").strip()
            diary.filter_by_date(start, end)
            
        elif choice == "5":
            min_temp = input("Минимальная температура (°C): ").strip()
            max_temp = input("Максимальная температура (°C): ").strip()
            diary.filter_by_temperature(min_temp, max_temp)
            
        elif choice == "6":
            diary.plot_temperature_graph()
            
        elif choice == "7":
            if diary._save_data():
                print("✅ Данные сохранены")
            else:
                print("❌ Ошибка сохранения")
                
        elif choice == "8":
            print("\n👋 До свидания!")
            break
        
        else:
            print("❌ Неверный выбор. Попробуйте снова.")
        
        input("\nНажмите Enter для продолжения...")

if __name__ == "__main__":
    main()
