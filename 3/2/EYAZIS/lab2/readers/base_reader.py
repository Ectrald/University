"""Базовый класс для ридеров различных форматов файлов."""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional


class BaseReader(ABC):
    """Абстрактный базовый класс для чтения текстовых файлов."""
    
    def __init__(self, file_path: Path):
        """
        Инициализация ридера.
        
        Args:
            file_path: Путь к файлу для чтения
        """
        self.file_path = Path(file_path)
        if not self.file_path.exists():
            raise FileNotFoundError(f"Файл не найден: {self.file_path}")
    
    @abstractmethod
    def read(self) -> str:
        """
        Читает содержимое файла и возвращает текст.
        
        Returns:
            Строка с текстом из файла
            
        Raises:
            IOError: Если произошла ошибка при чтении файла
        """
        pass
    
    # Подклассы переопределяют как классовый атрибут, например: supported_extensions = ['.txt']
    supported_extensions: list[str] = []
    
    @property
    def _supported_extensions(self) -> list[str]:
        """Список поддерживаемых расширений (для доступа через экземпляр)."""
        return type(self).supported_extensions
    
    @classmethod
    def can_read(cls, file_path: Path) -> bool:
        """
        Проверяет, может ли ридер обработать данный файл.
        
        Args:
            file_path: Путь к файлу
            
        Returns:
            True, если файл может быть прочитан
        """
        return Path(file_path).suffix.lower() in cls.supported_extensions
