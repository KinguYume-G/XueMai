# RAG Data Pipeline: Sourcing, Copyright, and Vector Store

This document consolidates the former `backend/docs/DAY2_COPYRIGHT_NOTICE.md`,
`DATA_SCRAPING_PLAN.md`, `RAG_DATA_COLLECTION_REPORT.md`, `FINAL_DATA_STATISTICS.md`, and
`RAG_MIGRATION.md` into one reference. Those five files have been removed; their
data-provenance and copyright content is preserved here.

## 1. Data sourcing policy (copyright/licensing)

The knowledge base backing the AI assistant's RAG retrieval was built from a mix of
self-authored content and openly-licensed third-party material. The sourcing policy that
was applied:

- **Absolutely avoid:** any ToS-prohibited scraping (LinkedIn, Glassdoor, Statista, paid
  reports, paywalled/login-gated content).
- **Prefer:** open-source datasets, RSS/Atom feeds, public educational resources (e.g.
  Purdue OWL for citation formats, Academic Phrasebank for writing guidance), and
  government/institutional public reports (e.g. Malaysia labor statistics for salary data).
- **When using MIT/CC-licensed third-party content** (e.g. the `tech-interview-handbook`
  repo, MIT licensed): the original copyright notice and license must be retained, and the
  source must be attributed. Each imported record carries `source`, `license`,
  `attribution`, and `source_url` metadata fields for this purpose.
- Every scraper was required to pass a `robots.txt` check before fetching (see
  `utils/robots_checker.py` pattern in the original scraping plan) and to respect
  conservative rate limits (1–10s/request depending on source risk tier).

## 2. What was actually collected

Per the final data-collection report (2025-11-29), the knowledge base was built in three
rounds:

| Round | Sources | Documents | Chunks | Embeddings | AI functions unlocked |
|---|---|---|---|---|---|
| Round 1 | Academic writing guides, interview questions, startup news, APU campus info | 305 | 583 | 573 | 4 |
| Round 2 | Resume templates, business-plan templates, company info, market reports | 70 | 494 | 494 | 4 |
| Round 3 | Salary data (government stats + PayScale public data + manual collection) | 150 | 238 | 238 | 1 |
| **Total** | | **525** | **1,315** | **1,305** | **9** |

(A later full-scale statistics pass reported larger totals — 554 documents / 4,552 chunks /
4,542 embeddings / 99.78% chunk-to-embedding completeness — reflecting continued ingestion
beyond the initial three rounds. Treat both sets of numbers as historical snapshots, not a
live count — see §4 for how to get current numbers.)

Per-source detail (Round 1–3):

- **Academic resources** (13 docs / 311 chunks) — academic writing guides, citation formats
- **Interview question bank** (210 docs / 210 chunks) — technical + behavioral interview Qs
- **Startup/entrepreneurship news** — Southeast Asia funding/startup news
- **APU campus data** (82 docs / 62 chunks) — course info, campus announcements, policies
- **Resume templates** (35 docs / 274 chunks) — 15 tech, 10 business, 5 design, 5 general
- **Business-plan templates** (12 docs / 168 chunks) — SaaS, e-commerce, AI/ML, fintech, etc.
- **Company info** (20 docs / 27 chunks) — Malaysian tech companies
- **Market reports** (3 docs / 25 chunks) — industry analysis
- **Salary data** (150 docs / 238 chunks) — 17 industries, 7 regions, 31 unique roles,
  ~MYR 4,498–9,297/month average range

Quality bar used during collection: retrieval test similarity > 0.7 and success rate > 80%
per source; measured overall RAG test success rate was ~97% with average similarity ~0.82.

Known gaps noted at the time (still worth checking before relying on these categories):
company-info chunk density was low (~1.35 chunks/company), and market reports numbered
only 3 documents.

## 3. Vector store architecture

The system migrated from ChromaDB (file-based, found to be serving 0 documents due to stale
data) to **PostgreSQL + pgvector** on 2025-11-23. This is the current and only supported
backend — `chromadb`/`langchain-chroma` are commented out in `backend/requirements.txt`, and
`backend/apps/ai/services/{ollama_client,groq_client,test_ollama}.py` (an older,
now-removed implementation) and `backend/test_docs/` have been deleted as dead code
superseded by `backend/apps/ai/clients/`.

- **Embedding model:** `nomic-embed-text` via Ollama, 768-dim vectors
- **Similarity:** cosine similarity, `similarity = (2 - cosine_distance) / 2`
- **Storage:** `AIEmbedding` model (`apps/ai/models.py`), `vector(768)` column
- **Index:** IVFFlat (or HNSW) on `ai_embeddings` via `vector_cosine_ops`
- **Retrieval services:** `apps/ai/services/vector_search_service.py` (pgvector queries),
  `apps/ai/services/rag_engine.py` (retrieval orchestration, supports backend switching)

### Configuration

In `backend/.env`:

```env
RAG_VECTOR_BACKEND=pgvector      # pgvector (current) | chromadb (deprecated, do not use)
RAG_PGVECTOR_TOP_K=5
RAG_PGVECTOR_SIMILARITY_THRESHOLD=0.3
```

### Rebuilding / inspecting the vector store

```bash
cd backend
python manage.py shell
>>> from scripts.rebuild_embeddings import run
>>> run()

>>> from apps.ai.services.vector_search_service import VectorSearchService
>>> VectorSearchService().get_stats()
# {'total_embeddings': ..., 'total_chunks': ..., 'total_documents': ..., 'embedding_with_vector': ...}
```

Ollama must be running locally with the embedding model pulled:

```bash
ollama pull nomic-embed-text
ollama serve
```

## 4. Getting current numbers

The counts in §2 are point-in-time snapshots from the original data-collection effort, not
live. To get the current state of the knowledge base, query it directly rather than trusting
this document:

```python
from apps.ai.models import AIDocument, AIChunk, AIEmbedding
AIDocument.objects.count(), AIChunk.objects.count(), AIEmbedding.objects.filter(embedding_vector__isnull=False).count()
```
