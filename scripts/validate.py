#!/usr/bin/env python3
"""Verify the checked-in dataset, coverage counts, and integrity offline."""
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    payload = (ROOT / "data/companies.json").read_bytes()
    manifest = json.loads((ROOT / "data/manifest.json").read_text(encoding="utf-8"))
    rows = json.loads(payload)
    info = manifest["files"]["companies.json"]
    assert len(payload) == info["bytes"], "File size differs from manifest"
    assert hashlib.sha256(payload).hexdigest() == info["sha256"], "Checksum differs from manifest"
    assert len(rows) == manifest["company_count"] == 6120
    slugs = [r["slug"] for r in rows]
    assert slugs == sorted(set(slugs)), "Company slugs must be unique and sorted"
    ids = [r["yc_id"] for r in rows if r["yc_id"] is not None]
    assert len(ids) == len(set(ids)) == manifest["yc_enriched_company_count"] == 6112
    assert [r["slug"] for r in rows if r["yc_id"] is None] == manifest["missing_yc_enrichment"]
    assert dict(Counter(r["batch"] for r in rows)) == manifest["batch_counts"]
    for key, count_key in (
        ("founders", "directory_founder_record_count"),
        ("yc_founders", "yc_founder_record_count"),
        ("news", "news_record_count"), ("launches", "launch_record_count"),
    ):
        assert sum(len(r[key]) for r in rows) == manifest[count_key], key
    for row in rows:
        assert re.fullmatch(r"[a-z0-9_-]+", row["slug"]), row["slug"]
        assert row["company"].strip(), row["slug"]
        assert row["yc_url"] == f"https://www.ycombinator.com/companies/{row['slug']}"
    # No signed AWS credentials, local paths, or known token prefixes in exports.
    text = payload.decode("utf-8")
    for pattern in (r"X-Amz-(?:Credential|Signature|Security-Token)", r"AWSAccessKeyId=", r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b", r"\bgh[pousr]_[A-Za-z0-9]{30,}\b", r"/Users/mini-home/", r"/Volumes/Backup Plus/"):
        assert not re.search(pattern, text, re.I), f"Unwanted export content: {pattern}"
    assert len(payload) < 50 * 1024 * 1024, "Review dataset size before Git publication"
    print(f"Validated {len(rows):,} unique companies, {len(ids):,} YC IDs, collection counts, and SHA-256.")


if __name__ == "__main__":
    main()
