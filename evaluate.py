"""Latency + retrieval check. questions.tsv lines: question<TAB>expected_filename<TAB>expected_page"""
import statistics
import sys

from rag.pipeline import RagPipeline

path = sys.argv[1] if len(sys.argv) > 1 else "questions.tsv"
rag = RagPipeline()
times, hits, rr = [], 0, []
rows = [l.rstrip("\n").split("\t") for l in open(path, encoding="utf-8") if l.strip()]
for q, fname, page in rows:
    r = rag.ask(q)
    times.append(r["total_s"])
    rank = next(
        (i + 1 for i, c in enumerate(r["chunks"])
         if c["filename"] == fname and c["page_start"] <= int(page) <= c["page_end"]), None)
    hits += rank is not None
    rr.append(1 / rank if rank else 0)
    print(f"{r['total_s']:.2f}s  rank={rank}  {q[:60]}")
times.sort()
p95 = times[min(len(times) - 1, int(0.95 * len(times)))]
print(f"\nN={len(rows)}  p50={statistics.median(times):.2f}s  p95={p95:.2f}s  "
      f"Recall@{len(r['chunks'])}={hits / len(rows):.2f}  MRR={statistics.mean(rr):.2f}")
