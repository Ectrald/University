"""Фабрика для создания ридеров различных форматов."""
from pathlib import Path
from typing import Optional
from .base_reader import BaseReader
from .txt_reader import TxtReader
from .rtf_reader import RtfReader
from .pdf_reader import PdfReader
from .doc_reader import DocReader
from .html_reader import HtmlReader
from .docx_reader import DocxReader


class ReaderFactory:
    """Фабрика для создания подходящего ридера для файла."""
    
    _readers = [
        TxtReader,
        RtfReader,
        PdfReader,
        DocReader,
        HtmlReader,
        DocxReader,
    ]
    
    @classmethod
    def create_reader(cls, file_path: Path) -> Optional[BaseReader]:
        """
        Создает ридер для указанного файла.
        
        Args:
            file_path: Путь к файлу
            
        Returns:
            Экземпляр ридера или None, если формат не поддерживается
            
        Raises:
            ValueError: Если формат файла не поддерживается
        """
        file_path = Path(file_path)
        extension = file_path.suffix.lower()
        
        for reader_class in cls._readers:
            if extension in reader_class.supported_extensions:
                return reader_class(file_path)
        
        raise ValueError(
            f"Формат файла '{extension}' не поддерживается. "
            f"Поддерживаемые форматы: {cls.get_supported_extensions()}"
        )
    
    @classmethod
    def get_supported_extensions(cls) -> list[str]:
        """Возвращает список всех поддерживаемых расширений файлов."""
        extensions = []
        for reader_class in cls._readers:
            extensions.extend(reader_class.supported_extensions)
        return sorted(set(extensions))
    
    @classmethod
    def can_read_file(cls, file_path: Path) -> bool:
        """
        Проверяет, может ли быть прочитан файл.
        
        Args:
            file_path: Путь к файлу
            
        Returns:
            True, если файл может быть прочитан
        """
        file_path = Path(file_path)
        extension = file_path.suffix.lower()
        return extension in cls.get_supported_extensions()
