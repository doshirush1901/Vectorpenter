from __future__ import annotations
import argparse
from core.logging import logger
from ingest.pipeline import ingest_path
from index.upsert import build_and_upsert
from index.embedder import embed_texts
from rag.retriever import vector_search
from rag.context_builder import hydrate_matches, build_context
from rag.generator import answer
from rag.reranker import rerank, is_rerank_available
from search.hybrid import index_typesense, hybrid_search, is_available as typesense_available


def cmd_ingest(path: str):
    res = ingest_path(path)
    logger.info(f"Ingested documents={res['documents']} chunks={res['chunks']}")


def cmd_index():
    # Index to Pinecone
    res = build_and_upsert()
    logger.info(f"Upserted {res['upserts']} vectors to namespace={res['namespace']}")
    
    # Index to Typesense
    typesense_res = index_typesense()
    if typesense_res.get('skipped'):
        logger.warning("Typesense indexing skipped (no server or key)")
    else:
        logger.info(f"Indexed {typesense_res['indexed']} chunks to Typesense")


def cmd_ask(q: str, k: int = 12, hybrid: bool = False, rerank: bool = False):
    # Embed query
    vec = embed_texts([q])[0]
    
    # Search for relevant chunks
    if hybrid and typesense_available():
        matches = hybrid_search(q, vec, top_k=k)
        search_type = "hybrid"
    else:
        # Oversample for potential reranking
        search_k = k * 2 if rerank else k
        matches = vector_search(vec, top_k=search_k)
        search_type = "vector"
    
    # Hydrate matches with full text
    snippets = hydrate_matches(matches)
    
    # Optional reranking
    if rerank and is_rerank_available() and snippets:
        snippets = rerank(q, snippets)
        snippets = snippets[:k]  # Trim to final k
        search_type += "+rerank"
    
    # Build context pack
    pack = build_context(snippets)
    
    # Generate answer
    if pack.strip():
        ans = answer(q, pack)
        logger.info(f"Query processed ({search_type}): {len(snippets)} sources")
    else:
        ans = "I don't have enough context to answer this question. Please make sure you have ingested and indexed some documents first."
    
    print(f"\n=== ANSWER ({search_type}) ===\n{ans}\n")
    
    if snippets:
        print(f"📚 Sources: {len(snippets)} chunks")


def main():
    p = argparse.ArgumentParser("Vectorpenter CLI", description="The carpenter of context — building vectors into memory")
    sub = p.add_subparsers(dest="cmd", help="Available commands")

    # Ingest command
    pi = sub.add_parser("ingest", help="Ingest documents from a directory")
    pi.add_argument("path", help="Path to directory containing documents")
    
    # Index command  
    px = sub.add_parser("index", help="Build vector and keyword indexes")
    
    # Ask command
    pa = sub.add_parser("ask", help="Ask questions about your documents")
    pa.add_argument("q", help="Your question")
    pa.add_argument("--k", type=int, default=12, help="Number of results to retrieve (default: 12)")
    pa.add_argument("--hybrid", action="store_true", help="Use hybrid search (vector + keyword)")
    pa.add_argument("--rerank", action="store_true", help="Use reranking for better results")

    args = p.parse_args()
    
    if args.cmd == "ingest":
        cmd_ingest(args.path)
    elif args.cmd == "index":
        cmd_index()
    elif args.cmd == "ask":
        cmd_ask(args.q, args.k, args.hybrid, args.rerank)
    else:
        p.print_help()

if __name__ == "__main__":
    main()
