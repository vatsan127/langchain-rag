# langchain-rag

A RAG (Retrieval-Augmented Generation) app that answers questions about a fictional company, Kestrel Freightworks. The data is private and made up, so a correct answer can only come from retrieval, not from the model's training. Embeddings and the chat model run on a local Ollama; chunks and vectors are stored in Postgres with pgvector.

## How it works

```
INDEXING (ingest.py, run once)            QUERY (__init__.py, every question)
load data/*.md                            question
  -> split by markdown headings             -> embed question (1024 numbers)
  -> embed each chunk (1024 numbers)        -> pgvector: 4 nearest chunks
  -> store in Postgres table                -> prompt = rules + chunks + question
                                            -> gemma4 -> answer
```

| File | Does |
|---|---|
| `src/langchain_rag/ingest.py` | Loads `data/*.md`, splits with `MarkdownHeaderTextSplitter` (`#`, `##`) then `RecursiveCharacterTextSplitter` (800 / 100), embeds and stores with `PGVectorStore`. Drops and re-creates the table on every run |
| `src/langchain_rag/__init__.py` | Embeds the question, gets the top 4 chunks (`similarity_search_with_score`), sends them as context to the chat model with an "answer only from context, else I don't know" prompt |
| `data/*.md` | 6 fictional company documents: leave policy, on-call runbook, product catalogue, expense policy, office FAQ, incident postmortem |

| Setting | Value |
|---|---|
| Chat model | `gemma4:e4b` |
| Embedding model | `qwen3-embedding:0.6b` (1024 dimensions) |
| Vector store | pgvector, table `kestrel_chunks`, cosine distance |
| Chunks | 6 files -> 39 chunks |

## Requirements

- Python 3.14+
- [uv](https://docs.astral.sh/uv/)
- [Ollama](https://ollama.com)
- Docker (for Postgres + pgvector)

## Setup

Models:

```bash
ollama pull gemma4:e4b
ollama pull qwen3-embedding:0.6b
```

Postgres with pgvector (host port 5434):

```bash
docker run -d --name pgvec -p 5434:5432 \
  -e POSTGRES_USER=srivatsan \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=kestrel \
  -v pgvec-data:/var/lib/postgresql/data \
  pgvector/pgvector:pg17
```

Python dependencies and config:

```bash
uv sync
cp .env.example .env
```

`.env`:

| Key | Example |
|---|---|
| `OLLAMA_MODEL` | `gemma4:e4b` |
| `OLLAMA_EMBED_MODEL` | `qwen3-embedding:0.6b` |
| `OLLAMA_BASE_URL` | `http://localhost:11434` |
| `PG_CONNECTION` | `postgresql+asyncpg://srivatsan:password@localhost:5434/kestrel` |
| `PG_COLLECTION` | `kestrel_chunks` (table name) |

## Run

1. Index the documents (once, or after changing `data/`):

```bash
uv run python -m langchain_rag.ingest
```

Expected: `6 files -> 39 chunks -> 39 rows in kestrel_chunks`

2. Ask a question (edit `question` in `main()` in `src/langchain_rag/__init__.py`):

```bash
uv run python -c "from langchain_rag import main; main()"
```

Sample questions:

| Question | Expected answer |
|---|---|
| How much do I get for weekend on-call? | ₹3,450 |
| Who approves a 50000 rupee claim? | Line manager and department head |
| How many annual leave days do I get? | 23 |
| What is the IT helpdesk extension? | 4400 |
| What is the dental insurance limit? | I don't know |

## Check the data in Postgres

```bash
docker exec -it pgvec psql -U srivatsan -d kestrel
```

```sql
-- table structure
\d kestrel_chunks

-- number of chunks
SELECT count(*) FROM kestrel_chunks;

-- chunks per file
SELECT langchain_metadata->>'source' AS source, count(*) FROM kestrel_chunks GROUP BY 1 ORDER BY 1;

-- source, section and start of each chunk
SELECT langchain_metadata->>'source' AS source, langchain_metadata->>'section' AS section, left(content, 60) AS content_start FROM kestrel_chunks;

-- vector size and the first numbers of one vector
SELECT vector_dims(embedding), left(embedding::text, 80) FROM kestrel_chunks LIMIT 1;

-- chunks nearest to the "2. Allowance" chunk (<=> = cosine distance, lower = closer)
SELECT langchain_metadata->>'section' AS section,
       embedding <=> (SELECT embedding FROM kestrel_chunks WHERE langchain_metadata->>'section' = '2. Allowance') AS distance
FROM kestrel_chunks ORDER BY distance LIMIT 5;
```

## Project creation

```bash
uv init --package --python 3.14
uv add langchain langchain-ollama langchain-text-splitters python-dotenv
uv add langchain-postgres "psycopg[binary]"
uv add asyncpg
```

## Notes

- `PGVectorStore` uses async database calls. On Windows, psycopg's async mode fails with `Psycopg cannot use the 'ProactorEventLoop'`, so the connection uses the `asyncpg` driver (`postgresql+asyncpg://`).
- The Postgres password above is for a local lab only.
- If Windows Smart App Control blocks the `langchain-rag.exe` launcher, use the `uv run python -c ...` command above instead of `uv run langchain-rag`.
