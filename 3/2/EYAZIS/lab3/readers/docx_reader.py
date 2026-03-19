import logging
import docx
from pathlib import Path
from .base_reader import BaseReader

logger = logging.getLogger(__name__)


class DocxReader(BaseReader):
    """Ридер для файлов DOCX."""
    
    supported_extensions = [".docx"]
    
    def read(self) -> str:
        """Чтение текста из DOCX файла."""
        logger.debug("Reading DOCX file: %s", self.file_path)
        try:
            doc = docx.Document(str(self.file_path))
            full_text = []
            for para in doc.paragraphs:
                full_text.append(para.text)
            return "\n".join(full_text)
        except Exception as e:
            logger.error(f"Error reading DOCX file {self.file_path}: {e}")
            raise
