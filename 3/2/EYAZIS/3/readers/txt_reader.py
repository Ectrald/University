"""Ридер для TXT файлов."""
from pathlib import Path
from .base_reader import BaseReader


class TxtReader(BaseReader):
    
    supported_extensions = ['.txt', '.text']
    
    def read(self) -> str:
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            # Попытка с другой кодировкой
            with open(self.file_path, 'r', encoding='latin-1') as f:
                return f.read()
