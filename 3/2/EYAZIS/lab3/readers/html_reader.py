import logging
from pathlib import Path
from bs4 import BeautifulSoup
from .base_reader import BaseReader

logger = logging.getLogger(__name__)


class HtmlReader(BaseReader):
    """Ридер для HTML-файлов."""
    
    supported_extensions = [".html", ".htm"]
    
    def read(self) -> str:
        """
        Чтение текста из HTML-файла.
        Извлекает текст, отбрасывая HTML-теги.
        """
        logger.debug("Reading HTML file: %s", self.file_path)
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                soup = BeautifulSoup(f, "html.parser")
                return soup.get_text(separator="\n").strip()
        except UnicodeDecodeError:
            logger.warning("UTF-8 reading failed for HTML, trying ansi/cp1251")
            with open(self.file_path, "r", encoding="cp1251") as f:
                soup = BeautifulSoup(f, "html.parser")
                return soup.get_text(separator="\n").strip()
