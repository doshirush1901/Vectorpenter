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

def build_external_snippets(snips: List[Dict]) -> str:
    """
    Format external Google search snippets for context inclusion
    
    Args:
        snips: List of Google search results
        
    Returns:
        Formatted string for context pack
    """
    if not snips:
        return ""
    
    buf = ["### External Web Context (Google)\n"]
    for i, s in enumerate(snips, 1):
        title = s.get('title', 'Unknown Title')
        snippet = s.get('snippet', 'No description available')
        link = s.get('link', '')
        
        buf.append(f"[G#{i}] {title}\n{snippet}\n({link})\n\n")
    
    return "".join(buf)

def build_combined_context(
    local_snippets: List[Dict], 
    external_snippets: List[Dict] = None,
    max_chars: int = 12000
) -> str:
    """
    Build combined context pack with local and external snippets
    
    Args:
        local_snippets: Local document snippets
        external_snippets: External Google search snippets
        max_chars: Maximum characters for context
        
    Returns:
        Combined context pack
    """
    # Start with local context
    local_context = build_context(local_snippets, max_chars=max_chars * 0.8)  # Reserve 20% for external
    
    # Add external context if available
    external_context = ""
    if external_snippets:
        external_context = build_external_snippets(external_snippets)
    
    # Combine contexts
    combined = local_context
    if external_context:
        # Check if we have room for external content
        remaining_chars = max_chars - len(local_context)
        if remaining_chars > 200:  # Minimum space for meaningful external content
            if len(external_context) <= remaining_chars:
                combined += "\n" + external_context
            else:
                # Truncate external content to fit
                truncated_external = external_context[:remaining_chars-50] + "...\n"
                combined += "\n" + truncated_external
                logger.debug("External context truncated to fit within max_chars limit")
    
    return combined
