# PDF RAG Chatbot

Open-source stack: PyMuPDF + RapidOCR, `bge-small-en-v1.5` (fastembed), Chroma (HNSW), Groq LLM (gpt-oss-20b), Streamlit.

## Setup (Windows, Python 3.12)
```
py -3.12 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env      # then set GROQ_API_KEY
```

## Run
1. Put 10+ PDFs in `data/pdfs/`
2. `python -m rag.ingest` (once; embeddings persist in `storage/`)
3. `streamlit run app.py`
4. Optional: `python evaluate.py questions.tsv` for p50/p95 latency, Recall@k, MRR.

## Security notes
- The API key is read from the environment / `.env` only; `.env` is git-ignored.
- The question and retrieved chunks are sent to Groq. Do not use with sensitive or cardholder data without approval for that data flow.
