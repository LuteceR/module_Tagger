import logging
from typing import Optional, Dict, Any, List

from .utils import (
    clean_text,
    extract_tags1,
    read_docx_paragraphs,
    read_docx_first_page_text,
    select_main_paragraph_range,
    build_chunks_by_sentences,
    build_chunks_by_paragraphs,
    build_chunks_by_characters,
    sha256_file,
)

LOG = logging.getLogger(__name__)

SUPERVISOR_SURNAMES = [
    "аврискин",
    "воробьева",
    "глазкова",
    "захарова",
    "мельникова",
    "павлова",
    "перевалова",
    "плотоненко",
    "ступников",
    "шенгелия",
    "ялдыгин",
    "свиязов",
    "стоянов",
    "коцур",
    "ниссенбаум",
]

def _normalize_lower(s: str) -> str:
    return (s or "").lower().replace("ё", "е")

def detect_supervisors(first_page_text: str) -> str:
    norm = _normalize_lower(first_page_text)
    present: List[str] = []
    for surname in SUPERVISOR_SURNAMES:
        base = _normalize_lower(surname)
        import re
        pattern = r"\b" + re.escape(base) + r"[а-яё]*\b"
        if re.search(pattern, norm):
            present.append(base)

    if not present:
        return "неизвестно"

    unique: List[str] = []
    seen = set()
    for s in present:
        if s not in seen:
            unique.append(s)
            seen.add(s)

    if len(unique) == 1:
        return unique[0]

    if "воробьева" in unique:
        others = [s for s in unique if s != "воробьева"]
        if others:
            return "/".join(others)
        return "воробьева"

    return "/".join(unique)


class TagExtractor:
    def __init__(self, model: Optional[object] = None):
        self.model = model

    def _predict_tags_from_text(self, text_chunks: List[str]) -> List[str]:
        if not self.model:
            return []
        preds = self.model.predict(text_chunks)
        tags: List[str] = []
        for out in preds:
            tags += extract_tags1(out)
        return tags

    def extract_from_path(
        self,
        path: str,
        seg_mode: str = "sentences",
        sentences_per_chunk: int = 4,
        paragraphs_per_chunk: int = 1,
        chars_per_chunk: int = 2000,
        stride_chars: Optional[int] = None,
        preannotated_only: bool = False,
    ) -> Dict[str, Any]:
        LOG.info(f"Файл: {path}")
        file_hash = sha256_file(path)

        paragraphs = read_docx_paragraphs(path)
        s_idx, e_idx = select_main_paragraph_range(path, paragraphs)
        main_paragraphs = paragraphs[s_idx:e_idx + 1] if paragraphs else []
        main_text = clean_text("\n".join(main_paragraphs))

        first_page_text = clean_text(read_docx_first_page_text(path))
        supervisors = detect_supervisors(first_page_text or main_text)

        if preannotated_only:
            tags = extract_tags1(main_text)
        else:
            if seg_mode == "paragraphs":
                chunks = build_chunks_by_paragraphs(main_paragraphs, paragraphs_per_chunk)
            elif seg_mode == "chars":
                chunks = build_chunks_by_characters(main_text, chars_per_chunk, stride_chars)
            else:
                chunks = build_chunks_by_sentences(main_text, sentences_per_chunk)
            tags = self._predict_tags_from_text(chunks)

        tags_unique = sorted(set(tags))
        return {
            "tags": tags_unique,
            "supervisors": supervisors,
            "range": {"start": s_idx, "end": e_idx},
            "meta": {"file_hash": file_hash},
        }


