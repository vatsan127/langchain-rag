import os

from dotenv import load_dotenv
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_postgres import PGEngine, PGVectorStore

TOP_K = 4
SYSTEM_PROMPT = """Answer using ONLY the context below. If it is not there, reply: I don't know.

Context:
{context}"""


def main() -> None:
    load_dotenv()
    question = "How much do I get for weekend on-call?"
    engine = PGEngine.from_connection_string(url=os.environ["PG_CONNECTION"])
    embeddings = OllamaEmbeddings(model=os.environ["OLLAMA_EMBED_MODEL"], base_url=os.environ["OLLAMA_BASE_URL"])
    store = PGVectorStore.create_sync(engine=engine, table_name=os.environ["PG_COLLECTION"], embedding_service=embeddings)
    results = store.similarity_search_with_score(question, k=TOP_K)

    context = "\n\n".join(doc.page_content for doc, _ in results)
    llm = ChatOllama(model=os.environ["OLLAMA_MODEL"], base_url=os.environ["OLLAMA_BASE_URL"])
    response = llm.invoke([("system", SYSTEM_PROMPT.format(context=context)), ("human", question)])
    print(response.content)
