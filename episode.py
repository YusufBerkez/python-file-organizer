"""Detect which episode a file belongs to, using only its file name.

Recording apps, editors and designers all name files differently:
"EP12_final.mp4", "ep-012 thumb.png", "Episode 12.srt", "Bolum_12.wav",
"S02E05_raw.mov". This module turns all of them into one episode id,
so that every file of an episode ends up in the same folder.
"""

import re

# Season + episode style, e.g. "S02E05", "s2_e5", "S02.E05".
SEASON_PATTERN = re.compile(r"(?<![a-z0-9])s(\d{1,2})[ ._-]?e(\d{1,3})(?!\d)", re.IGNORECASE)

# Episode-only style, e.g. "EP12", "ep-012", "Episode 12", "Bolum_12".
EPISODE_PATTERN = re.compile(r"(?<![a-z0-9])(?:episode|ep|bolum|bölüm)[ ._-]?(\d{1,3})(?!\d)", re.IGNORECASE)


def extract_episode(filename):
    """Return a normalized episode id ("S02E05" or "EP012") or None.

    Season style is checked first, so "S01E02" is never read as "EP002".
    Episode number 0 is treated as "no episode".
    """
    match = SEASON_PATTERN.search(filename)
    if match:
        season, number = int(match.group(1)), int(match.group(2))
        if season > 0 and number > 0:
            return f"S{season:02d}E{number:02d}"

    match = EPISODE_PATTERN.search(filename)
    if match:
        number = int(match.group(1))
        if number > 0:
            return f"EP{number:03d}"
    return None


def assign_episodes(records):
    """Add an "episode" key (an id or None) to every file record."""
    for record in records:
        record["episode"] = extract_episode(record["name"])
    return records


def group_by_episode(records):
    """Return {episode_id: [records]} for records that have an episode."""
    groups = {}
    for record in records:
        episode = record.get("episode")
        if episode is not None:
            groups.setdefault(episode, []).append(record)
    return groups


def find_missing(records, required):
    """Return {episode_id: [missing categories]} for incomplete episodes.

    A set of the categories present per episode makes the "is it there?"
    check fast and ignores duplicates (W3 S20).
    """
    missing = {}
    for episode, files in sorted(group_by_episode(records).items()):
        present = {record["category"] for record in files}
        absent = [category for category in required if category not in present]
        if absent:
            missing[episode] = absent
    return missing
