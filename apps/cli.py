from __future__ import annotations
import argparse
from core.logging import logger
from ingest.pipeline import ingest_path
from index.upsert import build_and_upsert
from index.embedder import embed_texts
from rag.retriever import vector_search
from rag.context_builder import hydrate_matches, build_context
from rag.generator import answer


def cmd_ingest(path: str):
    res = ingest_path(path)
    logger.info(f"Ingested documents={res['documents']} chunks={res['chunks']}")


def cmd_index():
    res = build_and_upsert()
    logger.info(f"Upserted {res['upserts']} vectors to namespace={res['namespace']}")


def cmd_ask(q: str, k: int = 12):
    # embed query, search vectors, hydrate, build context, answer
    vec = embed_texts([q])[0]
    matches = vector_search(vec, top_k=k)
    snippets = hydrate_matches(matches)
    pack = build_context(snippets)
    ans = answer(q, pack)
    print("\n=== ANSWER ===\n" + ans + "\n")


def main():
    p = argparse.ArgumentParser("Vectorpenter CLI")
    sub = p.add_subparsers(dest="cmd")

    pi = sub.add_parser("ingest"); pi.add_argument("path")
    px = sub.add_parser("index")
    pa = sub.add_parser("ask"); pa.add_argument("q"); pa.add_argument("--k", type=int, default=12)

    args = p.parse_args()
    if args.cmd == "ingest":
        cmd_ingest(args.path)
    elif args.cmd == "index":
        cmd_index()
    elif args.cmd == "ask":
        cmd_ask(args.q, args.k)
    else:
        p.print_help()

if __name__ == "__main__":
    main()
