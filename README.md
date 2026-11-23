# ycos

A portable snapshot of **6,120 Y Combinator company records**, collected on
**September 21–22, 2026**. Read it from GitHub, clone it, or load the JSON locally.

## Data

- [`data/companies.json`](data/companies.json): a JSON array, sorted by unique
  `slug`, containing company descriptions, batches, industries, websites, locations,
  status, tags, founder profiles, news, and launch posts. About 26 MB uncompressed.
- [`data/manifest.json`](data/manifest.json): snapshot dates, source provenance,
  record counts, batch counts, transformations, and a SHA-256 checksum.
- [`SCHEMA.md`](SCHEMA.md): field meanings and source distinctions.

There are **6,112 companies with YC page enrichment**, **11,704 directory founder
records**, and **11,669 YC founder records**. These are overlapping founder sources,
not counts to add together. Eight YC pages returned 404; their directory records
remain in the dataset. All company slugs and non-null YC IDs are unique.

This preserves every company in the saved archive. It is **not a verified complete
or current list of every YC company**. There is no automatic refresh; status, team
size, jobs, and URLs describe the snapshot and may have changed.

## Read from another machine or project

Clone with an authenticated GitHub CLI, including when the repository is private:

```sh
gh repo clone pauljump/ycos
```

Or download only the data from a private or public repository:

```sh
gh api -H 'Accept: application/vnd.github.raw+json' \
  'repos/pauljump/ycos/contents/data/companies.json?ref=main' > companies.json
```

Load it in Python (standard library only):

```python
import json
from pathlib import Path

companies = json.loads(Path("companies.json").read_text(encoding="utf-8"))
by_slug = {company["slug"]: company for company in companies}
print(by_slug["airbnb"]["one_liner"])
```

If the repository is public, it is also readable without authentication:

```javascript
const response = await fetch(
  "https://raw.githubusercontent.com/pauljump/ycos/main/data/companies.json"
);
if (!response.ok) throw new Error(`ycos: HTTP ${response.status}`);
const companies = await response.json();
const winter2024 = companies.filter(company => company.batch === "Winter 2024");
```

For reproducible consumers, replace `main` with a specific commit SHA. Keep private
repository credentials in your server or local credential manager; browser access
without credentials requires public visibility.

## Provenance and rebuilding

The original archive combines a public founder-directory export from September 21
with public YC company pages fetched on September 22. The manifest records the
original JSONL checksum. The larger source archive, raw HTML, database, and image
files are preserved separately and are not required to consume this repository.

This export keeps public company/founder information and news/launch content while
omitting archive-only image paths, avatar URLs, duplicate embedded objects,
sharing/moderation metadata, and email-availability flags. AWS signed URL query
parameters are removed, including from links inside launch text. Remaining image
links can be expired or relative; no images are bundled.

Regenerate from the original archive without any network or provider API calls:

```sh
python3 scripts/export.py /path/to/original/companies.jsonl
python3 scripts/validate.py
```

The exporter is deliberately pinned to this snapshot. A future refresh should
update the dates, provenance, coverage expectations, and schema intentionally.

Validation checks JSON parsing, unique IDs and slugs, counts, sorting, source URL
construction, checksum, and common unwanted credential/path patterns. It does not
verify that websites are still live or that descriptions remain accurate.

This is an independent archive, not an official YC dataset. Source text and images
remain subject to their respective owners' rights; this repository does not claim
to relicense third-party content.
