import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_ollama import OllamaEmbeddings
from langchain_postgres import PGEngine, PGVectorStore
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
CHUNK_SIZE = 800
CHUNK_OVERLAP = 100
VECTOR_SIZE = 1024


def load_documents() -> list[Document]:
    docs = []
    for path in sorted(DATA_DIR.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        docs.append(Document(page_content=text, metadata={"source": path.name}))
    return docs


def split_documents(docs: list[Document]) -> list[Document]:
    header_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=[("#", "title"), ("##", "section")],
        strip_headers=False,
    )
    size_splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
    chunks = []
    for doc in docs:
        for section in header_splitter.split_text(doc.page_content):
            section.metadata["source"] = doc.metadata["source"]
            chunks.extend(size_splitter.split_documents([section]))
    return chunks


def store_chunks(chunks: list[Document]) -> list[str]:
    table = os.environ["PG_COLLECTION"]
    engine = PGEngine.from_connection_string(url=os.environ["PG_CONNECTION"])
    engine.init_vectorstore_table(table_name=table, vector_size=VECTOR_SIZE, overwrite_existing=True)
    embeddings = OllamaEmbeddings(model=os.environ["OLLAMA_EMBED_MODEL"], base_url=os.environ["OLLAMA_BASE_URL"])
    store = PGVectorStore.create_sync(engine=engine, table_name=table, embedding_service=embeddings)
    return store.add_documents(chunks)


def main() -> None:
    load_dotenv()
    docs = load_documents()
    chunks = split_documents(docs)
    ids = store_chunks(chunks)
    print(f"{len(docs)} files -> {len(chunks)} chunks -> {len(ids)} rows in {os.environ['PG_COLLECTION']}")


if __name__ == "__main__":
    main()