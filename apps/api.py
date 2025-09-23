from fastapi import FastAPI
from index.embedder import embed_texts
from rag.retriever import vector_search
from rag.context_builder import hydrate_matches, build_context
from rag.generator import answer

app = FastAPI(title="Vectorpenter API")

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/query")
def query(payload: dict):
    q = payload.get("q", "")
    k = int(payload.get("k", 12))
    vec = embed_texts([q])[0]
    matches = vector_search(vec, top_k=k)
    snippets = hydrate_matches(matches)
    pack = build_context(snippets)
    ans = answer(q, pack)
    return {"answer": ans, "k": k}
