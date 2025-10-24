import chromadb
from chromadb.config import Settings


class DocStore:
    def __init__(self, collection="docs"):
        self.client = chromadb.Client(Settings(anonymized_telemetry=False))
        self.col = self.client.get_or_create_collection(collection)

    # add documents to the collection
    def add_docs(self, docs: list[tuple[str, str]]):
        ids = [f"doc-{i}" for i, _ in enumerate(docs)]
        self.col.add(
            documents=[d[1] for d in docs],
            metadatas=[{"title": d[0]} for d in docs],
            ids=ids,
        )

    # query the collection
    def query(self, q: str, k: int = 3):
        res = self.col.query(query_texts=[q], n_results=k)
        docs = res.get("documents", [[]])[0]
        metadatas = res.get("metadatas", [[]])[0]
        return list(zip([m["title"] for m in metadatas], docs))
