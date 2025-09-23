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

def expand_with_neighbors(snippets: List[Dict], left: int = 1, right: int = 1, max_chars: int = 12000) -> List[Dict]:
    """
    Expand snippets with neighboring chunks for better narrative continuity
    
    Args:
        snippets: Original snippets from search
        left: Number of chunks to include before each snippet
        right: Number of chunks to include after each snippet
        max_chars: Maximum total characters for all expanded snippets
        
    Returns:
        Expanded list of snippets including neighbors
    """
    from sqlalchemy import text as sql
    from state.db import engine
    from core.logging import logger
    
    if not snippets:
        return snippets
    
    out = []
    seen = set()
    
    logger.debug(f"Expanding {len(snippets)} snippets with neighbors (left={left}, right={right})")
    
    try:
        with engine.begin() as conn:
            for s in snippets:
                snippet_id = s.get("id")
                if snippet_id in seen:
                    continue
                
                # Add the original snippet
                out.append(s)
                seen.add(snippet_id)
                
                # Get document and sequence info
                doc_id = s.get("doc")
                base_seq = s.get("seq")
                
                if not doc_id or base_seq is None:
                    continue
                
                # Calculate neighbor sequences
                neighbor_seqs = []
                
                # Add left neighbors (seq-1, seq-2, etc.)
                for i in range(1, left + 1):
                    neighbor_seq = base_seq - i
                    if neighbor_seq >= 0:  # Don't go below sequence 0
                        neighbor_seqs.append(neighbor_seq)
                
                # Add right neighbors (seq+1, seq+2, etc.)
                for i in range(1, right + 1):
                    neighbor_seq = base_seq + i
                    neighbor_seqs.append(neighbor_seq)
                
                if not neighbor_seqs:
                    continue
                
                # Query for neighbor chunks
                seq_placeholders = ",".join([f":seq{i}" for i in range(len(neighbor_seqs))])
                query = f"""
                    SELECT id, document_id, seq, text 
                    FROM chunks 
                    WHERE document_id = :doc_id AND seq IN ({seq_placeholders})
                    ORDER BY seq
                """
                
                params = {"doc_id": doc_id}
                for i, seq in enumerate(neighbor_seqs):
                    params[f"seq{i}"] = seq
                
                rows = conn.execute(sql(query), params).fetchall()
                
                # Add neighbor chunks
                for row in rows:
                    neighbor_id, neighbor_doc_id, neighbor_seq, neighbor_text = row
                    
                    if neighbor_id in seen:
                        continue
                    
                    neighbor_snippet = {
                        "id": neighbor_id,
                        "doc": neighbor_doc_id,
                        "seq": neighbor_seq,
                        "text": neighbor_text,
                        "score": s.get("score", 0.0),  # Inherit score from original snippet
                        "neighbor_of": snippet_id  # Mark as neighbor for debugging
                    }
                    
                    out.append(neighbor_snippet)
                    seen.add(neighbor_id)
        
        # Sort by document and sequence for better readability
        out.sort(key=lambda x: (x.get("doc", ""), x.get("seq", 0)))
        
        # Trim by character budget
        trimmed = []
        total_chars = 0
        
        for snippet in out:
            chunk_text = snippet.get("text", "")
            if total_chars + len(chunk_text) > max_chars:
                logger.debug(f"Late windowing: trimmed at {len(trimmed)} snippets due to character limit")
                break
            
            trimmed.append(snippet)
            total_chars += len(chunk_text)
        
        logger.info(f"Late windowing: expanded {len(snippets)} → {len(trimmed)} snippets ({total_chars} chars)")
        return trimmed
        
    except Exception as e:
        logger.warning(f"Late windowing failed: {e}")
        # Return original snippets on error
        return snippets
