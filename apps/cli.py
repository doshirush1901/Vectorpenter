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
    from core.config import is_grounding_enabled, grounding_threshold, max_google_results
    from rag.context_builder import build_combined_context
    from gcp.search import google_ground, should_use_grounding
    
    # Embed query
    vec = embed_texts([q])[0]
    
    # Search for relevant chunks
    best_score = 0.0
    if hybrid and typesense_available():
        matches, best_score = hybrid_search(q, vec, top_k=k)
        search_type = "hybrid"
    else:
        # Oversample for potential reranking
        search_k = k * 2 if rerank else k
        matches, best_score = vector_search(vec, top_k=search_k)
        search_type = "vector"
    
    # Hydrate matches with full text
    snippets = hydrate_matches(matches)
    
    # Optional reranking
    if rerank and is_rerank_available() and snippets:
        snippets = rerank(q, snippets)
        snippets = snippets[:k]  # Trim to final k
        search_type += "+rerank"
    
    # Google grounding fallback
    external_snippets = []
    if is_grounding_enabled() and should_use_grounding(best_score, len(snippets), k):
        try:
            external_snippets = google_ground(q, max_results=max_google_results())
            if external_snippets:
                logger.info(f"Grounding: added {len(external_snippets)} Google snippets (threshold {grounding_threshold():.3f})")
                search_type += "+grounding"
            else:
                logger.info("Grounding: no Google results found")
        except Exception as e:
            logger.warning(f"Grounding failed: {e}")
    else:
        logger.info("Grounding: local only")
    
    # Build context pack (local + external)
    pack = build_combined_context(snippets, external_snippets)
    
    # Generate answer
    if pack.strip():
        ans = answer(q, pack)
        total_sources = len(snippets) + len(external_snippets)
        logger.info(f"Query processed ({search_type}): {len(snippets)} local + {len(external_snippets)} external sources")
    else:
        ans = "I don't have enough context to answer this question. Please make sure you have ingested and indexed some documents first."
        total_sources = 0
    
    print(f"\n=== ANSWER ({search_type}) ===\n{ans}\n")
    
    if snippets:
        print(f"📚 Local Sources: {len(snippets)} chunks")
    if external_snippets:
        print(f"🌐 External Sources: {len(external_snippets)} Google results")


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
