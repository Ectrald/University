"""Ридер для RTF файлов."""
from pathlib import Path
from striprtf.striprtf import rtf_to_text
from .base_reader import BaseReader


class RtfReader(BaseReader):
    
    supported_extensions = ['.rtf']
    
    def read(self) -> str:
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                rtf_content = f.read()
            return rtf_to_text(rtf_content)
        except UnicodeDecodeError:
            with open(self.file_path, 'r', encoding='latin-1') as f:
                rtf_content = f.read()
            return rtf_to_text(rtf_content)
