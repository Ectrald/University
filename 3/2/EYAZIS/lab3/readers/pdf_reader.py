"""Ридер для PDF файлов."""
from pathlib import Path
import pdfplumber
from .base_reader import BaseReader


class PdfReader(BaseReader):
    
    supported_extensions = ['.pdf']
    
    def read(self) -> str:
        try:
            text_parts = []
            with pdfplumber.open(self.file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
            return '\n'.join(text_parts)
        except Exception as e:
            raise IOError(f"Ошибка при чтении PDF файла: {e}")
