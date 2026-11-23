# Company schema — version 1

`data/companies.json` is a UTF-8 JSON array, ordered by `slug`. Each company is one
physical line within that array. Consumers should parse it as JSON, not JSONL.
Absent scalar source fields become `null`; absent nested collections become `[]`.
Source empty strings and placeholders such as `—` are preserved.

| Field | Meaning |
| --- | --- |
| `slug` | Unique stable key within this snapshot. |
| `company` | Company name from the founder directory. |
| `yc_url` | YC profile URL constructed from the slug; eight returned 404. |
| `yc_id` | Unique numeric YC company ID, or null without enrichment. |
| `batch` | Source batch label, e.g. `Winter 2024`. |
| `industry`, `location` | Directory category and location text. |
| `team_size` | Directory string, including 105 `—` placeholders; not numeric. |
| `status`, `stage` | Directory status and stage. |
| `yc_status` | YC page status. Preserved separately; 24 differ from `status`. |
| `one_liner`, `website` | Directory summary and company website; 36 websites are `—`. |
| `long_description` | Full YC company description, when present. |
| `year_founded`, `country` | YC founding year and country value. |
| `tags`, `yc_tags` | Separate directory and YC tag lists. Unenriched `yc_tags` is null. |
| `company_linkedin`, `company_x`, `github`, `crunchbase` | Company links from YC. |
| `group_partner` | YC group partner name when available. |
| `open_jobs` | Number of jobs at capture time, or null without enrichment. |
| `founders` | Directory founder records, described below. |
| `yc_founders` | YC founder profiles, described below. |
| `news` | Source news items: `title`, `url`, `date`. |
| `launches` | YC launch posts, described below. |

`founders` contains `peek_id`, `name`, `role`, `linkedin_url`, and `x_url`.
`peek_id` is the directory identifier, distinct from a YC user ID.

`yc_founders` contains `user_id`, `is_active`, `founder_bio`, `full_name`, `title`,
`twitter_url`, and `linkedin_url`. These overlap the directory founder records;
they have not been merged or matched into a deduplicated person table.

`launches` contains `id`, `title`, `body`, `tagline`, `created_at`, `slug`, `url`,
`ycdc_launch_url`, and `launch_embed_url`. `body` preserves source Markdown, which
may include HTML and relative links. Treat it as third-party content when rendering.
Dates and timestamps retain their source representation. Relative YC links can be
resolved against `https://www.ycombinator.com/`.

See `data/manifest.json` for exact counts, coverage, exclusions, and file integrity.
