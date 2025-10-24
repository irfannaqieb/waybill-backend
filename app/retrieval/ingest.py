from pathlib import Path
from .store import DocStore


def ingest_docs():
    store = DocStore()
    docs = []
    docs_dir = Path(__file__).with_suffix("").parent.joinpath("docs")
    for p in docs_dir.glob("*.md"):
        docs.append((p.stem, p.read_text(encoding="utf-8")))
    if docs:
        store.add_docs(docs)
        print(f"Ingested {len(docs)} documents into {store.col.name}")
