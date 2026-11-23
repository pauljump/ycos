#!/usr/bin/env python3
"""Build the portable snapshot from the existing company JSONL archive, offline."""
import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

ROOT = Path(__file__).resolve().parents[1]
SOURCE_SHA256 = "9b594bea3e231a044368d08a2cb9c2d52032af7977ec232f95c42c24542efdd4"
COMPANY_FIELDS = (
    "slug company batch industry location team_size status stage one_liner website "
    "tags yc_id long_description year_founded yc_status yc_tags country "
    "company_linkedin company_x github crunchbase group_partner open_jobs"
).split()
FOUNDER_FIELDS = "peek_id name role linkedin_url x_url".split()
YC_FOUNDER_FIELDS = (
    "user_id is_active founder_bio full_name title twitter_url linkedin_url"
).split()
NEWS_FIELDS = "title url date".split()
LAUNCH_FIELDS = (
    "id title body tagline created_at slug url ycdc_launch_url launch_embed_url"
).split()
URL_PATTERN = re.compile(r"https?://[^\s<>\"'\]\)]+")


def clean_url(match):
    """Remove signed query parameters even from URLs embedded in Markdown."""
    url = match.group(0)
    parts = urlsplit(url)
    query = parse_qsl(parts.query.replace("&amp;", "&"), keep_blank_values=True)
    safe = [(k, v) for k, v in query if not (
        k.lower().startswith("x-amz-") or
        k.lower() in {"awsaccesskeyid", "signature", "expires", "security-token"}
    )]
    if safe == query:
        return url
    return urlunsplit(parts._replace(query=urlencode(safe)))


def sanitize(value):
    if isinstance(value, str):
        return URL_PATTERN.sub(clean_url, value)
    if isinstance(value, list):
        return [sanitize(item) for item in value]
    if isinstance(value, dict):
        return {key: sanitize(item) for key, item in value.items()}
    return value


def select(record, fields):
    return {key: record.get(key) for key in fields}


def convert(record):
    out = select(record, COMPANY_FIELDS)
    out["yc_url"] = f"https://www.ycombinator.com/companies/{out['slug']}"
    for key, fields in (
        ("founders", FOUNDER_FIELDS), ("yc_founders", YC_FOUNDER_FIELDS),
        ("news", NEWS_FIELDS), ("launches", LAUNCH_FIELDS),
    ):
        out[key] = [select(item, fields) for item in record.get(key) or []]
    return sanitize(out)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("--output", type=Path, default=ROOT / "data")
    args = parser.parse_args()
    source = args.source.read_bytes()
    if hashlib.sha256(source).hexdigest() != SOURCE_SHA256:
        raise SystemExit("Source checksum differs from the original September snapshot; review provenance before exporting a replacement.")
    rows = sorted(
        (convert(json.loads(line)) for line in source.decode("utf-8").split("\n") if line.strip()),
        key=lambda item: item["slug"],
    )
    if len(rows) != 6120 or len({r["slug"] for r in rows}) != len(rows):
        raise SystemExit("Expected the original 6,120 unique-company snapshot; review a new snapshot explicitly.")
    # One object per physical line inside a standard JSON array, for readable diffs.
    payload = ("[\n" + ",\n".join(json.dumps(r, ensure_ascii=False, separators=(",", ":")) for r in rows) + "\n]\n").encode("utf-8")
    manifest = {
        "schema_version": 1,
        "snapshot_dates_utc": ["2026-09-21", "2026-09-22"],
        "company_count": len(rows),
        "yc_enriched_company_count": sum(r["yc_id"] is not None for r in rows),
        "directory_founder_record_count": sum(len(r["founders"]) for r in rows),
        "yc_founder_record_count": sum(len(r["yc_founders"]) for r in rows),
        "news_record_count": sum(len(r["news"]) for r in rows),
        "launch_record_count": sum(len(r["launches"]) for r in rows),
        "missing_yc_enrichment": [r["slug"] for r in rows if r["yc_id"] is None],
        "batch_counts": dict(sorted(Counter(r["batch"] for r in rows).items())),
        "sources": [
            {"name": "Archived public founder-directory export", "fetched_dates_utc": ["2026-09-21"], "sha256": hashlib.sha256(source).hexdigest()},
            {"name": "Y Combinator public company pages", "url_template": "https://www.ycombinator.com/companies/{slug}", "fetched_dates_utc": ["2026-09-22"]},
        ],
        "coverage": "All 6,120 company records in the original archive; not a claim of complete or current YC directory coverage.",
        "transformations": [
            "Sort by slug and expose a JSON array; add yc_url derived from slug.",
            "Use explicit company, founder, news, and launch field lists; absent scalar fields become null and absent collections become empty arrays.",
            "Omit local image filenames, avatar URLs, duplicated nested company/user objects, sharing metadata, moderation fields, and has_email flags.",
            "Remove AWS signed URL query parameters, including links in launch text; remaining image URLs may no longer resolve.",
            "Preserve source team-size strings, placeholders, and distinct directory/YC status, tag, and founder fields without inference or deduplication.",
        ],
        "files": {"companies.json": {"bytes": len(payload), "sha256": hashlib.sha256(payload).hexdigest()}},
    }
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "companies.json").write_bytes(payload)
    (args.output / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Exported {len(rows):,} companies; {len(payload):,} bytes")


if __name__ == "__main__":
    main()
