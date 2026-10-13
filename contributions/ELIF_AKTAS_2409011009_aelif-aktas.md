# Contribution – Elif Aktaş

- **Student ID:** 2409011009
- **GitHub:** aelif-aktas
- **Role:** Episode detection (business logic) and statistics report

## Files I wrote
- `episode.py`
- `report.py`

## What I implemented
- Two regular expressions recognise `EP12`, `ep-012`, `Episode 12`, `Bolum_12` and `S02E05` styles; `extract_episode()` normalizes them to `EP012` / `S02E05` and rejects false matches such as `deep12` or episode 0.
- `group_by_episode()` and `find_missing()` list the required deliverables each episode is still missing.
- `build_statistics()` counts files and bytes per category and collects unique episode ids.
- `render_report()` builds the multi-line report; `format_size()` shows bytes as KiB/MiB/GiB.
- `save_report()` writes the report only to a new `.txt`/`.md` file and never overwrites.

## Design decisions
- Season style is checked before episode style so `S01E02` is never read as episode 2 of no season.
- Look-behind / look-ahead in the regex stop matches inside other words and numbers.
- A set of present categories per episode makes the missing check simple and ignores duplicates.

## Course topics I applied
- Accumulator pattern and stats dictionary (W2, W3 S59-61)
- `format_size` helper (W3 S58)
- f-strings, alignment, multi-line report (W3 S37-39)
- Sets for unique values (W3 S20)
- Returning a dictionary of results (W3 S18)
- Regular expressions (course syllabus)
- `with open(..., "w")` (W2)

## Commits
- Add episode detection from file names
- Add statistics report and size formatting
- Add contribution file
