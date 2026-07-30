# Blog publishing validation memory

Use this alongside `AGENTS.md` and `CLAUDE.md` for every blog publication or SEO
audit.

## Failure pattern to avoid

A July 2026 audit of `Relative To What` passed the old checklist while still
missing five classes of defect:

1. Honest image dimensions were checked, but card-type minimums and crop shape
   were not. A 296 by 433 portrait was incorrectly assigned
   `summary_large_image`.
2. The new post sitemap entry was checked in isolation. The changed Genomic
   Relativity collection page was left stale, while an untouched History Book
   landing page was advanced.
3. `wordCount` was inherited from an ad hoc counting convention and did not
   match a clearly defined article-body count.
4. Source prose was treated as outside the SEO audit, hiding an internal link
   that used the apex domain instead of canonical `www`.
5. A top-to-bottom read focused on meaning but did not include a character-level
   typography scan, so one U+2019 apostrophe survived among ASCII apostrophes.

## Required audit habits

- Validate the physical thumbnail against the selected platform card. X large
  cards require at least 300 by 157 pixels and need a usable landscape crop.
  Use `summary` for a qualifying portrait or square asset when a large card
  would fail or crop badly.
- Build an explicit inventory of every page changed by publication. Update each
  corresponding sitemap entry and inspect all neighboring root-page entries for
  accidental date bumps.
- Recompute `wordCount` from rendered article content with the repository's
  declared boundary. Never accept a number merely because JSON parses.
- Scan Markdown and HTML for absolute internal links using
  `https://gptomics.com/`; canonicalize them to
  `https://www.gptomics.com/`.
- Scan the source for mixed ASCII and typographic apostrophes and preserve the
  draft's dominant style.
- A precedent post proves consistency, not correctness. Validate external
  constraints independently when the repository checklist specifies a platform
  behavior.
