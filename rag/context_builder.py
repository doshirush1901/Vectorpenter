from __future__ import annotations
from typing import List, Dict
from sqlalchemy import text as sql
from state.db import engine


def hydrate_matches(matches: List[Dict]) -> List[Dict]:
    ids = [m["id"] for m in matches]
    if not ids:
        return []
    with engine.begin() as conn:
        rows = conn.execute(sql(
            "SELECT id, document_id, seq, text FROM chunks WHERE id IN (%s)" % (",".join([":id"+str(i) for i in range(len(ids))]))
        ), {("id"+str(i)): ids[i] for i in range(len(ids))}).fetchall()
    maprow = {r[0]: {"doc": r[1], "seq": r[2], "text": r[3]} for r in rows}
    out = []
    for m in matches:
        meta = maprow.get(m["id"], {})
        m["text"] = meta.get("text", "")
        m["doc"] = meta.get("doc")
        m["seq"] = meta.get("seq")
        out.append(m)
    return out


def build_context(snippets: List[Dict], max_chars: int = 12000) -> str:
    buf = []
    total = 0
    for i, s in enumerate(snippets, start=1):
        chunk = f"[#{i}] {s['doc']}::{s['seq']}\n{s['text']}\n\n"
        if total + len(chunk) > max_chars:
            break
        buf.append(chunk)
        total += len(chunk)
    return "".join(buf)
