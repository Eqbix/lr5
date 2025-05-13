import os
import csv
from abc import ABC, abstractmethod

class BaseReference(ABC):
    """Абстрактный базовый класс для справок"""
    @abstractmethod
    def validate(self):
        """Проверяет заполненность всех обязательных полей"""
        pass

class StudentReference(BaseReference):
    """Класс для представления студенческой справки"""
    _fields = ['id', 'date', 'full_name', 'stipend', 'destination']
    
    def __init__(self, **kwargs):
        object.__setattr__(self, '_initialized', False)
        for key in self._fields:
            object.__setattr__(self, key, kwargs.get(key, None))
        object.__setattr__(self, '_initialized', True)
    
    def __setattr__(self, name, value):
        if name not in self._fields and self._initialized:
            raise AttributeError(f"Недопустимое поле: {name}")
        object.__setattr__(self, name, value)
    
    def __repr__(self):
        return (f"Справка №{self.id} от {self.date}\n"
                f"Студент: {self.full_name}\n"
                f"Стипендия: {self.stipend}\n"
                f"Назначение: {self.destination}\n")
    
    def validate(self):
        if not all([self.id, self.date, self.full_name, self.stipend, self.destination]):
            raise ValueError("Не все поля заполнены")
    
    def to_dict(self):
        """Преобразует объект в словарь для CSV"""
        return {
            '№': self.id,
            'дата': self.date,
            'ФИО студента': self.full_name,
            'размер стипендии': self.stipend,
            'куда выдается справка': self.destination
        }

class ReferenceCollection:
    """Коллекция для управления справками"""
    def __init__(self):
        self._data = []
    
    def __iter__(self):
        self._index = 0
        return self
    
    def __next__(self):
        if self._index < len(self._data):
            result = self._data[self._index]
            self._index += 1
            return result
        raise StopIteration
    
    def __getitem__(self, index):
        return self._data[index]
    
    def __repr__(self):
        return "\n".join(str(item) for item in self._data)
    
    def add(self, item):
        if not isinstance(item, StudentReference):
            raise TypeError("Можно добавлять только объекты StudentReference")
        self._data.append(item)
    
    @staticmethod
    def from_csv(filename):
        """Создает коллекцию из CSV-файла"""
        collection = ReferenceCollection()
        try:
            with open(filename, 'r', encoding='utf-8-sig') as file:
                reader = csv.DictReader(file, delimiter=';')
                for row in reader:
                    try:
                        ref = StudentReference(
                            id=row['№'],
                            date=row['дата'],
                            full_name=row['ФИО студента'],
                            stipend=float(row['размер стипендии']),
                            destination=row['куда выдается справка']
                        )
                        ref.validate()
                        collection.add(ref)
                    except (KeyError, ValueError) as e:
                        print(f"Ошибка загрузки: {e}")
                        return None
            return collection
        except FileNotFoundError:
            print(f"Файл {filename} не найден")
            return None

    def save_to_csv(self, filename):
        """Сохраняет коллекцию в CSV"""
        if not self._data:
            print("Нет данных для сохранения!")
            return
        try:
            with open(filename, 'w', newline='', encoding='utf-8-sig') as file:
                writer = csv.DictWriter(
                    file, 
                    fieldnames=['№', 'дата', 'ФИО студента', 'размер стипендии', 'куда выдается справка'],
                    delimiter=';'
                )
                writer.writeheader()
                for item in self._data:
                    writer.writerow(item.to_dict())
                print(f"Данные сохранены в {filename}")
        except Exception as e:
            print(f"Ошибка сохранения: {e}")

    def filter_by_stipend(self, value):
        """Генератор для фильтрации по стипендии"""
        for item in self._data:
            if item.stipend > value:
                yield item

class EnhancedReferenceCollection(ReferenceCollection):
    """Расширенная коллекция с сортировкой"""
    def sort_by(self, field):
        if field == 'name':
            self._data.sort(key=lambda x: x.full_name)
        elif field == 'stipend':
            self._data.sort(key=lambda x: x.stipend)

def main():
    collection = None
    while True:
        print("\nМеню:")
        print("1. Посчитать файлы в директории")
        print("2. Загрузить данные")
        print("3. Сортировать по ФИО")
        print("4. Сортировать по стипендии")
        print("5. Фильтровать по стипендии > X")
        print("6. Добавить запись")
        print("7. Сохранить данные")
        print("8. Выход")
        
        choice = input("Выберите пункт: ")
        
        if choice == '1':
            path = input("Путь: ")
            print(f"Файлов: {len(os.listdir(path))}")
        
        elif choice == '2':
            collection = ReferenceCollection.from_csv('data.csv')
            print("Данные загружены" if collection else "Ошибка")
        
        elif choice == '3':
            if not collection:
                print("Сначала загрузите данные!")
                continue
            EnhancedReferenceCollection.sort_by(collection, 'name')
            print(collection)
        
        elif choice == '4':
            if not collection:
                print("Сначала загрузите данные!")
                continue
            EnhancedReferenceCollection.sort_by(collection, 'stipend')
            print(collection)
        
        elif choice == '5':
            try:
                x = float(input("Введите X: "))
                for item in collection.filter_by_stipend(x):
                    print(item)
            except ValueError:
                print("Ошибка ввода!")
        
        elif choice == '6':
            try:
                new_ref = StudentReference(
                    id=input("№: "),
                    date=input("Дата: "),
                    full_name=input("ФИО: "),
                    stipend=float(input("Стипендия: ")),
                    destination=input("Назначение: ")
                )
                new_ref.validate()
                collection.add(new_ref)
                print("Добавлено!")
            except Exception as e:
                print(f"Ошибка: {e}")
        
        elif choice == '7':
            if not collection:
                print("Сначала загрузите данные!")
                continue
            collection.save_to_csv('data.csv')
        
        elif choice == '8':
            break

if __name__ == "__main__":
    main()#Текст для копии
