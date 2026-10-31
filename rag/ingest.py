"""PDF -> clean text -> overlapping chunks -> embeddings -> Chroma (HNSW)."""
import re
import sys
from collections import Counter
from pathlib import Path

import chromadb
import pymupdf
from fastembed import TextEmbedding

from . import config

_ocr = None


def _ocr_page(page) -> str:
    global _ocr
    if _ocr is None:
        from rapidocr_onnxruntime import RapidOCR
        _ocr = RapidOCR()
    result, _ = _ocr(page.get_pixmap(dpi=200).tobytes("png"))
    return "\n".join(r[1] for r in result) if result else ""


def extract_pages(pdf_path: Path) -> list[str]:
    """Native text where available, OCR for scanned pages."""
    pages = []
    with pymupdf.open(pdf_path) as doc:
        for page in doc:
            text = page.get_text("text")
            if len(text.strip()) < config.MIN_NATIVE_CHARS:
                text = _ocr_page(page)
            pages.append(text)
    return pages


def _norm(line: str) -> str:
    return re.sub(r"\d+", "#", line.strip().lower())


def strip_headers_footers(pages: list[str]) -> list[str]:
    """Drop lines repeated on >40% of pages (running headers, footers, page numbers)."""
    if len(pages) < 5:
        return pages
    counts = Counter()
    for text in pages:
        counts.update({_norm(l) for l in text.splitlines() if l.strip()})
    limit = 0.4 * len(pages)
    return [
        "\n".join(l for l in text.splitlines() if counts[_norm(l)] <= limit)
        for text in pages
    ]


def chunk_pages(pages: list[str]) -> list[dict]:
    """Deterministic sliding window over words, remembering each word's page."""
    words = [(w, i + 1) for i, text in enumerate(pages) for w in text.split()]
    size = config.CHUNK_WORDS
    step = max(1, int(size * (1 - config.CHUNK_OVERLAP)))
    chunks = []
    for start in range(0, len(words), step):
        window = words[start:start + size]
        chunks.append({
            "text": " ".join(w for w, _ in window),
            "page_start": window[0][1],
            "page_end": window[-1][1],
        })
        if start + size >= len(words):
            break
    return chunks


def get_collection():
    client = chromadb.PersistentClient(path=str(config.STORE_DIR))
    return client.get_or_create_collection(
        config.COLLECTION, metadata={"hnsw:space": "cosine"}
    )


def ingest(pdf_dir: Path = config.PDF_DIR, log=print) -> None:
    pdfs = sorted(pdf_dir.glob("*.pdf"))
    if not pdfs:
        sys.exit(f"No PDFs found in {pdf_dir}")
    embedder = TextEmbedding(config.EMBED_MODEL)
    col = get_collection()
    for doc_id, pdf in enumerate(pdfs):
        if col.get(where={"filename": pdf.name}, limit=1)["ids"]:
            log(f"skip  {pdf.name} (already indexed)")
            continue
        log(f"read  {pdf.name}")
        pages = strip_headers_footers(extract_pages(pdf))
        chunks = chunk_pages(pages)
        log(f"      {len(pages)} pages -> {len(chunks)} chunks, embedding...")
        vectors = [v.tolist() for v in embedder.embed([c["text"] for c in chunks])]
        for i in range(0, len(chunks), 500):
            batch = chunks[i:i + 500]
            col.add(
                ids=[f"{pdf.stem}-{i + j}" for j in range(len(batch))],
                documents=[c["text"] for c in batch],
                embeddings=vectors[i:i + 500],
                metadatas=[{
                    "pdf_id": doc_id,
                    "filename": pdf.name,
                    "page_start": c["page_start"],
                    "page_end": c["page_end"],
                } for c in batch],
            )
        log(f"done  {pdf.name}")
    log(f"index holds {col.count()} chunks")


if __name__ == "__main__":
    ingest()
