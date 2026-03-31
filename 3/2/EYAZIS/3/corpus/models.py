import logging
from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, Table, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker, Session
from datetime import datetime
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)
Base = declarative_base()

text_word_association = Table(
    "text_word",
    Base.metadata,
    Column("text_id", Integer, ForeignKey("texts.id"), primary_key=True),
    Column("word_id", Integer, ForeignKey("words.id"), primary_key=True),
)


class TextDocument(Base):
    __tablename__ = "texts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)
    source_file = Column(String(500))
    domain = Column(String(100), default="Animals")
    author = Column(String(200))
    genre = Column(String(100))
    date_created = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    word_count = Column(Integer, default=0)

    words = relationship("CorpusWord", secondary=text_word_association, back_populates="texts")

    def __repr__(self):
        return f"<TextDocument(title='{self.title}', words={self.word_count})>"


class CorpusWord(Base):
    __tablename__ = "words"

    id = Column(Integer, primary_key=True, autoincrement=True)
    word = Column(String(255), nullable=False, index=True)
    lemma = Column(String(255), nullable=False, index=True)
    pos = Column(String(50), index=True)
    morph_tags = Column(String(255))
    frequency = Column(Integer, default=1)

    texts = relationship("TextDocument", secondary=text_word_association, back_populates="words")

    def __repr__(self):
        return f"<CorpusWord(word='{self.word}', lemma='{self.lemma}', pos='{self.pos}')>"


class CorpusDB:
    def __init__(self, db_path: str = "corpus.db"):
        self.engine = create_engine(f"sqlite:///{db_path}", echo=False)
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)

    def get_session(self) -> Session:
        return self.SessionLocal()

    def add_text_document(
        self,
        title: str,
        content: str,
        source_file: Optional[str] = None,
        domain: str = "Animals",
        author: Optional[str] = None,
        genre: Optional[str] = None,
        date_created: Optional[str] = None,
    ) -> TextDocument:
        session = self.get_session()
        try:
            doc = TextDocument(
                title=title,
                content=content,
                source_file=source_file,
                domain=domain,
                author=author,
                genre=genre,
                date_created=date_created,
                word_count=len(content.split()),
            )
            session.add(doc)
            session.commit()
            session.refresh(doc)
            return doc
        finally:
            session.close()

    def update_text_document(
        self,
        text_id: int,
        title: Optional[str] = None,
        content: Optional[str] = None,
        domain: Optional[str] = None,
        author: Optional[str] = None,
        genre: Optional[str] = None,
        date_created: Optional[str] = None,
    ) -> Optional[TextDocument]:
        session = self.get_session()
        try:
            doc = session.query(TextDocument).filter_by(id=text_id).first()
            if doc:
                if title is not None: doc.title = title
                if content is not None: 
                    doc.content = content
                    doc.word_count = len(content.split())
                if domain is not None: doc.domain = domain
                if author is not None: doc.author = author
                if genre is not None: doc.genre = genre
                if date_created is not None: doc.date_created = date_created
                session.commit()
                session.refresh(doc)
            return doc
        finally:
            session.close()

    def add_word(
        self,
        word: str,
        lemma: str,
        pos: str,
        morph_tags: Optional[str] = None, 
    ) -> CorpusWord:
        session = self.get_session()
        try:
            existing = session.query(CorpusWord).filter_by(word=word, lemma=lemma).first()
            if existing:
                existing.frequency += 1
                session.commit()
                session.refresh(existing)
                return existing
            else:
                w = CorpusWord(
                    word=word,
                    lemma=lemma,
                    pos=pos,
                    morph_tags=morph_tags,
                )
                session.add(w)
                session.commit()
                session.refresh(w)
                return w
        finally:
            session.close()

    def link_word_to_text(self, text_id: int, word_id: int) -> None:
        session = self.get_session()
        try:
            text = session.query(TextDocument).filter_by(id=text_id).first()
            word = session.query(CorpusWord).filter_by(id=word_id).first()
            if text and word and word not in text.words:
                text.words.append(word)
                session.commit()
        finally:
            session.close()

    def get_all_words(self) -> List[CorpusWord]:
        session = self.get_session()
        try:
            return session.query(CorpusWord).order_by(CorpusWord.frequency.desc()).all()
        finally:
            session.close()

    def get_all_texts(self) -> List[TextDocument]:
        session = self.get_session()
        try:
            return session.query(TextDocument).order_by(TextDocument.created_at.desc()).all()
        finally:
            session.close()

    def search_words(self, query: str) -> List[CorpusWord]:
        session = self.get_session()
        try:
            return (
                session.query(CorpusWord)
                .filter(
                    (CorpusWord.word.like(f"%{query}%")) |
                    (CorpusWord.lemma.like(f"%{query}%"))
                )
                .order_by(CorpusWord.frequency.desc())
                .all()
            )
        finally:
            session.close()

    def get_word_by_lemma(self, lemma: str) -> List[CorpusWord]:
        session = self.get_session()
        try:
            return session.query(CorpusWord).filter_by(lemma=lemma).all()
        finally:
            session.close()

    def get_texts_by_domain(self, domain: str) -> List[TextDocument]:
        session = self.get_session()
        try:
            return session.query(TextDocument).filter_by(domain=domain).all()
        finally:
            session.close()

    def get_frequency_stats(self) -> Dict[str, int]:
        session = self.get_session()
        try:
            words = session.query(CorpusWord).all()
            return {
                "total_words": sum(w.frequency for w in words),
                "unique_words": len(words),
                "total_texts": session.query(TextDocument).count(),
            }
        finally:
            session.close()

    def get_pos_distribution(self) -> Dict[str, int]:
        session = self.get_session()
        try:
            words = session.query(CorpusWord).all()
            dist = {}
            for w in words:
                pos = w.pos or "UNKNOWN"
                dist[pos] = dist.get(pos, 0) + w.frequency
            return dist
        finally:
            session.close()

    def get_concordance(self, lemma: str, window: int = 5) -> List[Dict[str, Any]]:
        session = self.get_session()
        try:
            texts = session.query(TextDocument).all()
            results = []
            for text in texts:
                words = text.content.split()
                for i, w in enumerate(words):
                    w_clean = w.lower().strip(".,!?;:\"'()[]")
                    if w_clean == lemma.lower():
                        start = max(0, i - window)
                        end = min(len(words), i + window + 1)
                        context = " ".join(words[start:end])
                        results.append({
                            "text_id": text.id,
                            "text_title": text.title,
                            "context": context,
                            "position": i,
                        })
            return results
        finally:
            session.close()

    def delete_text(self, text_id: int) -> bool:
        session = self.get_session()
        try:
            text = session.query(TextDocument).filter_by(id=text_id).first()
            if text:
                session.delete(text)
                session.commit()
                return True
            return False
        finally:
            session.close()

    def clear_corpus(self) -> tuple:
        session = self.get_session()
        try:
            text_count = session.query(TextDocument).count()
            word_count = session.query(CorpusWord).count()
            
            session.query(TextDocument).delete()
            session.query(CorpusWord).delete()
            session.commit()
            return (text_count, word_count)
        finally:
            session.close()
