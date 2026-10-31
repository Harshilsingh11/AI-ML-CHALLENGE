import time

import streamlit as st

from rag import config
from rag.ingest import ingest
from rag.pipeline import RagPipeline

st.set_page_config(page_title="PDF RAG Chatbot", layout="wide")


@st.cache_resource
def pipeline() -> RagPipeline:
    return RagPipeline()


rag = pipeline()
chat_tab, ingest_tab = st.tabs(["Chat", "Ingestion"])

with ingest_tab:
    st.markdown(
        "**Pipeline:** PDF (native text / OCR) → strip headers & footers → "
        f"{config.CHUNK_WORDS}-word chunks, {int(config.CHUNK_OVERLAP * 100)}% overlap → "
        f"`{config.EMBED_MODEL}` embeddings → Chroma HNSW index"
    )
    st.metric("Chunks in vector DB", rag.col.count())
    st.caption(f"Drop PDFs into `{config.PDF_DIR}`, then run ingestion.")
    if st.button("Run ingestion"):
        box = st.empty()
        lines: list[str] = []

        def log(msg):
            lines.append(msg)
            box.code("\n".join(lines))

        ingest(log=log)
        st.cache_resource.clear()

with chat_tab:
    st.session_state.setdefault("history", [])
    for turn in st.session_state.history:
        with st.chat_message(turn["role"]):
            st.markdown(turn["content"])

    if q := st.chat_input("Ask a question about the PDFs"):
        st.session_state.history.append({"role": "user", "content": q})
        with st.chat_message("user"):
            st.markdown(q)
        with st.chat_message("assistant"):
            t0 = time.perf_counter()
            chunks = rag.retrieve(q)
            t_ret = time.perf_counter() - t0
            with st.expander(f"Retrieved chunks ({t_ret * 1000:.0f} ms)", expanded=True):
                for c in chunks:
                    st.markdown(f"**{rag.cite(c)}** · similarity {c['score']:.3f}")
                    st.caption(c["text"][:400] + "…")
            answer = st.write_stream(rag.stream_answer(q, chunks))
            total = time.perf_counter() - t0
            st.markdown("**Sources:** " + "; ".join(sorted({rag.cite(c) for c in chunks})))
            st.caption(f"retrieval {t_ret:.2f}s · total {total:.2f}s")
        st.session_state.history.append({"role": "assistant", "content": answer})
