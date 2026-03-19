"""FastAPI backend для Corpus Manager."""
import logging
import os
import tempfile
from typing import Optional

from fastapi import FastAPI, UploadFile, File, Form, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from controller import CorpusController

logger = logging.getLogger(__name__)

app = FastAPI(title="Corpus Manager API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

controller = CorpusController()


# ── Pydantic models ──────────────────────────────────────────────

class AddTextRequest(BaseModel):
    title: str
    content: str
    domain: str = "Animals"
    author: Optional[str] = None
    genre: Optional[str] = None
    date_created: Optional[str] = None


class AnalyzeTextRequest(BaseModel):
    text: str


class UpdateTextRequest(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    domain: Optional[str] = None
    author: Optional[str] = None
    genre: Optional[str] = None
    date_created: Optional[str] = None


class SaveSyntacticRequest(BaseModel):
    text_id: int
    sentence_index: int
    original_sentence: str
    result_json: str


class UpdateSyntacticRequest(BaseModel):
    result_json: str
# ── Endpoints ─────────────────────────────────────────────────────

@app.get("/api/texts")
def get_texts():
    """Получить все тексты корпуса."""
    return controller.get_all_texts()


@app.post("/api/texts")
def add_text(req: AddTextRequest):
    """Добавить текст в корпус."""
    return controller.add_text(
        title=req.title,
        content=req.content,
        domain=req.domain,
        author=req.author,
        genre=req.genre,
        date_created=req.date_created,
    )


@app.post("/api/texts/upload")
def upload_file(
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    domain: str = Form("Animals"),
    author: Optional[str] = Form(None),
    genre: Optional[str] = Form(None),
    date_created: Optional[str] = Form(None),
):
    """Загрузить файл в корпус."""
    suffix = os.path.splitext(file.filename)[1] if file.filename else ".txt"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(file.file.read())
        tmp_path = tmp.name

    try:
        result = controller.add_text_from_file(
            file_path=tmp_path,
            title=title,
            domain=domain,
            author=author,
            genre=genre,
            date_created=date_created,
        )
    finally:
        os.unlink(tmp_path)

    return result


@app.delete("/api/texts/{text_id}")
def delete_text(text_id: int):
    """Удалить текст."""
    return controller.delete_text(text_id)


@app.put("/api/texts/{text_id}")
def update_text(text_id: int, req: UpdateTextRequest):
    """Обновить текст."""
    return controller.update_text(
        text_id,
        title=req.title,
        content=req.content,
        domain=req.domain,
        author=req.author,
        genre=req.genre,
        date_created=req.date_created,
    )


@app.get("/api/search")
def search_words(query: str = Query("")):
    """Поиск слов."""
    return controller.search_words(query)


@app.get("/api/statistics")
def get_statistics():
    """Статистика корпуса."""
    return controller.get_statistics()


@app.get("/api/frequency")
def get_frequency(top_n: int = Query(20)):
    """Частотные данные."""
    return controller.get_frequency_data(top_n)


@app.get("/api/concordance/kwic")
def get_kwic(lemma: str = Query(""), window: int = Query(3)):
    """KWIC данные."""
    return controller.get_kwic(lemma, window)


@app.get("/api/concordance/collocates")
def get_collocates(lemma: str = Query(""), window: int = Query(3)):
    """Коллокаты."""
    return controller.get_collocates(lemma, window)


@app.post("/api/analyze")
def analyze_text(req: AnalyzeTextRequest):
    """Анализ текста без сохранения."""
    return controller.analyze_text(req.text)


@app.post("/api/corpus/clear")
def clear_corpus():
    """Очистить корпус."""
    return controller.clear_corpus()


@app.get("/api/word/{lemma}")
def get_word_info(lemma: str):
    """Информация о слове."""
    return controller.get_word_info(lemma)


@app.get("/api/texts/{text_id}/content")
def get_text_content(text_id: int):
    """Получить содержимое текста."""
    return controller.get_text_content(text_id)


@app.post("/api/syntactic-analysis/analyze-and-save/{text_id}")
def analyze_and_save_text(text_id: int):
    """Анализировать текст и сохранить результаты."""
    return controller.analyze_and_save_text(text_id)


@app.post("/api/syntactic-analysis/analyze")
def analyze_syntax(req: AnalyzeTextRequest):
    """Синтаксический анализ текста."""
    return controller.analyze_syntax(req.text)


@app.post("/api/syntactic-analysis/save")
def save_syntactic_analysis(req: SaveSyntacticRequest):
    """Сохранить синтаксический анализ."""
    return controller.save_syntactic_analysis(
        req.text_id, req.sentence_index, req.original_sentence, req.result_json
    )


@app.get("/api/syntactic-analysis/{text_id}")
def get_syntactic_analysis(text_id: int):
    """Получить сохраненные синтаксические анализы."""
    return controller.get_syntactic_analysis(text_id)


@app.put("/api/syntactic-analysis/update/{analysis_id}")
def update_syntactic_analysis(analysis_id: int, req: UpdateSyntacticRequest):
    """Обновить сохраненный синтаксический анализ."""
    return controller.update_syntactic_analysis(analysis_id, req.result_json)


@app.delete("/api/syntactic-analysis/{analysis_id}")
def delete_syntactic_analysis(analysis_id: int):
    """Удалить сохраненный синтаксический анализ."""
    return controller.delete_syntactic_analysis(analysis_id)
