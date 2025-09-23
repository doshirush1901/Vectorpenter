from __future__ import annotations
from pathlib import Path
from datetime import datetime
import hashlib
import json
from ingest.loaders import iter_files
from ingest.parsers import read_text
from ingest.chunkers import simple_chunks
from state.db import init_db, engine
from sqlalchemy import text as sql


def _hash_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def ingest_path(root: str | Path) -> dict:
    from core.config import is_translation_enabled, is_gcs_enabled, translate_target_lang, translate_min_chars
    from core.logging import logger
    
    init_db()
    root = Path(root)
    docs = 0
    chs = 0
    
    # Log processing configuration
    logger.info(f"Translation: {'enabled (target=' + translate_target_lang() + ')' if is_translation_enabled() else 'disabled'}")
    logger.info(f"Archival (GCS): {'enabled → ' + (settings.gcs_bucket or 'no bucket') if is_gcs_enabled() else 'disabled'}")
    
    with engine.begin() as conn:
        for f in iter_files(root):
            raw = f.read_bytes()
            h = _hash_bytes(raw)
            # skip if same hash exists
            exists = conn.execute(sql("SELECT id FROM documents WHERE id=:id"), {"id": str(f)}).fetchone()
            if exists:
                prev = conn.execute(sql("SELECT hash FROM documents WHERE id=:id"), {"id": str(f)}).fetchone()
                if prev and prev[0] == h:
                    continue
            
            # Step 1: Parse document (includes DocAI auto-upgrade)
            raw_text, meta = read_text(f)
            
            # Step 2: Translation (if enabled and text is long enough)
            translated_text = None
            translation_meta = {}
            
            if is_translation_enabled() and len(raw_text.strip()) >= translate_min_chars():
                try:
                    from gcp.translation import translate_text, should_translate
                    
                    if should_translate(raw_text, translate_target_lang()):
                        translated_text, translation_meta = translate_text(raw_text, translate_target_lang())
                        if translation_meta.get("translated", False):
                            logger.info(f"Document translated: {f.name} ({translation_meta.get('source_language')} → {translation_meta.get('target_language')})")
                        else:
                            logger.debug(f"Translation skipped for {f.name}: {translation_meta.get('reason', 'unknown')}")
                except Exception as e:
                    logger.warning(f"Translation failed for {f.name}: {e}")
            
            # Use translated text for processing if available
            final_text = translated_text if translated_text else raw_text
            
            # Step 3: Chunk the (possibly translated) text
            seqs = simple_chunks(final_text)
            
            # Step 4: GCS Archival (if enabled)
            gcs_uris = {}
            if is_gcs_enabled():
                try:
                    from gcp.gcs import archive_document_artifacts
                    
                    archive_metadata = {
                        **meta,
                        **translation_meta,
                        "processing_timestamp": datetime.utcnow().isoformat(),
                        "chunk_count": len(seqs)
                    }
                    
                    gcs_uris = archive_document_artifacts(
                        document_path=str(f),
                        raw_text=raw_text,
                        translated_text=translated_text,
                        redacted_text=None,  # TODO: Add DLP integration here
                        metadata=archive_metadata
                    )
                    
                    if gcs_uris:
                        logger.info(f"GCS archived {f.name}: {', '.join(gcs_uris.keys())} → {list(gcs_uris.values())}")
                        
                except Exception as e:
                    logger.warning(f"GCS archival failed for {f.name}: {e}")
            
            # Step 5: Store document and chunks
            now = datetime.utcnow().isoformat()
            
            # Enhance metadata with processing info
            enhanced_meta = {
                **meta,
                **translation_meta,
                "gcs_uris": gcs_uris
            }
            
            conn.execute(sql(
                "REPLACE INTO documents(id,path,source,title,author,mime,created_at,updated_at,hash,tags)"
                " VALUES(:id,:path,:source,:title,:author,:mime,:created_at,:updated_at,:hash,:tags)"
            ), {
                "id": str(f),
                "path": str(f),
                "source": "local",
                "title": f.name,
                "author": "",
                "mime": f.suffix.lower(),
                "created_at": now,
                "updated_at": now,
                "hash": h,
                "tags": json.dumps(enhanced_meta),
            })
            
            for c in seqs:
                chunk_id = f"{f}::#{c['seq']}"
                conn.execute(sql(
                    "REPLACE INTO chunks(id,document_id,seq,text,tokens,metadata,created_at)"
                    " VALUES(:id,:document_id,:seq,:text,:tokens,:metadata,:created_at)"
                ), {
                    "id": chunk_id,
                    "document_id": str(f),
                    "seq": c["seq"],
                    "text": c["text"],
                    "tokens": len(c["text"].split()),
                    "metadata": json.dumps({"source": str(f), **enhanced_meta}),
                    "created_at": now,
                })
            docs += 1
            chs += len(seqs)
    return {"documents": docs, "chunks": chs}
