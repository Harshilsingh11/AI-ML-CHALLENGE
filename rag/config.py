import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

PDF_DIR = ROOT / "data" / "pdfs"
STORE_DIR = ROOT / "storage" / "chroma"
COLLECTION = "pdf_chunks"

EMBED_MODEL = "BAAI/bge-small-en-v1.5"
QUERY_PREFIX = "Represent this sentence for searching relevant passages: "

# Chunking is word based (~0.75 words per token): 400 words ~ 530 tokens.
CHUNK_WORDS = 400
CHUNK_OVERLAP = 0.2

# A page with fewer native characters than this is treated as scanned and OCR'd.
MIN_NATIVE_CHARS = 40

TOP_K = 5
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")
# Free-tier limits are per model (8k tokens/min), so rate-limited calls fall through to the next.
GROQ_FALLBACKS = ["openai/gpt-oss-120b", "qwen/qwen3.8-27b"]
