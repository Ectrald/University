"""Ридер для DOC и DOCX файлов."""
from pathlib import Path
from docx import Document
from .base_reader import BaseReader


class DocReader(BaseReader):
    
    supported_extensions = ['.doc', '.docx']
    
    def read(self) -> str:
        try:
            doc = Document(self.file_path)
            paragraphs = []
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    paragraphs.append(paragraph.text)
            return '\n'.join(paragraphs)
        except Exception as e:
            raise IOError(f"Ошибка при чтении DOC/DOCX файла: {e}")
