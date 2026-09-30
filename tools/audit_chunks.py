"""Record the unchanged Unit 1 sample and audit every chunk's word boundaries.

Run from the activated environment: python tools/audit_chunks.py --label before
This is evaluation instrumentation; it does not rebuild or change the index.
"""
import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import config
import store
from ingest import load_documents
from chunker import split_documents, _split_title, _sections

SAMPLE = ["guide_accessibility.md#0", "guide_corry_vale.md#5",
          "guide_givens_mill.md#2", "guide_kestrelford.md#4",
          "guide_pellew_sands.md#6"]


def audit():
    documents = load_documents()
    chunks = split_documents(documents)
    checks = []
    for chunk in chunks:
        document = next(d for d in documents if d.source == chunk.source)
        title, body = _split_title(document.text)
        header, payload = chunk.text.split("\n\n", 1)
        starts_at_heading = any(h and header == f"{title} \u2014 {h}"
                                for h, _ in _sections(body))
        pos = document.text.find(payload)
        end = pos + len(payload)
        intact = (pos >= 0
                  and (pos == 0 or not (document.text[pos - 1].isalnum() and payload[0].isalnum()))
                  and (end == len(document.text)
                       or not (payload[-1].isalnum() and document.text[end].isalnum())))
        checks.append({"label": chunk.label, "word_boundaries_intact": intact,
                       "section_heading": starts_at_heading})
    collection = store._client().get_collection(config.collection_name())
    raw = collection.get(include=["documents", "metadatas"])
    stored = {f"{m['source']}#{m['index']}": t
              for m, t in zip(raw["metadatas"], raw["documents"])}
    sample = [next(c for c in chunks if c.label == label) for label in SAMPLE]
    return {"produced_by": "tools/audit_chunks.py::audit",
            "total_chunks": len(chunks), "index_chunks": collection.count(),
            "index_matches_current_chunker": stored == {c.label: c.text for c in chunks},
            "word_boundary_violations": [r["label"] for r in checks
                                         if not r["word_boundaries_intact"]],
            "sample_labels": SAMPLE,
            "sample_heading_count": sum(next(r for r in checks if r["label"] == c.label)
                                        ["section_heading"] for c in sample),
            "sample": [asdict(c) for c in sample], "checks": checks}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--label", required=True)
    args = parser.parse_args()
    record = audit()
    config.RESULTS_DIR.mkdir(exist_ok=True)
    path = config.RESULTS_DIR / f"chunks-{args.label}.json"
    path.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n")
    print(f"{record['total_chunks']} chunks; {len(record['word_boundary_violations'])} "
          f"word-boundary violations; {record['sample_heading_count']}/5 sample section starts; "
          f"index matches: {record['index_matches_current_chunker']}")
    print(path.relative_to(config.ROOT))
