"""Detect which episode a file belongs to, using only its file name.

Recording apps, editors and designers all name files differently:
"EP12_final.mp4", "ep-012 thumb.png", "Episode 12.srt", "Bolum_12.wav",
"S02E05_raw.mov". This module turns all of them into one episode id,
so that every file of an episode ends up in the same folder.
"""

import os

# Characters that separate the words of a file name.
SEPARATORS = {" ", "_", "-", "."}

# Words that announce an episode number, e.g. "EP12" or "Episode 12".
EPISODE_WORDS = ("episode", "bolum", "bölüm", "ep")

MAX_EPISODE = 999
MAX_SEASON = 99


def split_words(filename):
    """Split a file name (without its extension) into lower-case words.

    "EP12_final cut.mp4" -> ["ep12", "final", "cut"]
    """
    stem = os.path.splitext(filename)[0].lower()
    words = []
    current = ""
    for character in stem:
        if character in SEPARATORS:
            if current != "":
                words.append(current)
            current = ""
        else:
            current += character
    if current != "":
        words.append(current)
    return words


def to_number(text):
    """Return text as a whole number from 1 to 999, or None.

    Only the digits 0-9 are accepted, so "12" works but "", "0", "1234"
    and "twelve" do not.
    """
    if text == "" or len(text) > 3:
        return None
    for character in text:
        if character not in "0123456789":
            return None
    number = int(text)
    if number < 1 or number > MAX_EPISODE:
        return None
    return number


def read_season_episode(word):
    """Read "s02e05" as the tuple (2, 5); return None for any other word."""
    if not word.startswith("s"):
        return None
    parts = word[1:].split("e")
    if len(parts) != 2:
        return None
    season = to_number(parts[0])
    number = to_number(parts[1])
    if season is None or number is None or season > MAX_SEASON:
        return None
    return season, number


def read_episode_number(word):
    """Read "ep12", "episode12" or "bolum12" as 12; return None otherwise."""
    for prefix in EPISODE_WORDS:
        if word.startswith(prefix):
            number = to_number(word[len(prefix):])
            if number is not None:
                return number
    return None


def extract_episode(filename):
    """Return a normalized episode id ("S02E05" or "EP012") or None.

    Season style is checked first, so "S01E02" is never read as "EP002".
    A word must START with "ep", so "deep12.mp4" is not episode 12.
    """
    words = split_words(filename)

    for index in range(len(words)):
        pair = read_season_episode(words[index])
        if pair is None and index + 1 < len(words):
            pair = read_season_episode(words[index] + words[index + 1])  # "S02 E05"
        if pair is not None:
            season, number = pair
            return f"S{season:02d}E{number:02d}"

    for index in range(len(words)):
        number = read_episode_number(words[index])
        if number is None and words[index] in EPISODE_WORDS and index + 1 < len(words):
            number = to_number(words[index + 1])  # "Episode 12"
        if number is not None:
            return f"EP{number:03d}"
    return None


def assign_episodes(records):
    """Add an "episode" key (an id or None) to every file record."""
    for record in records:
        record["episode"] = extract_episode(record["name"])
    return records


def group_by_episode(records):
    """Return {episode_id: [records]} for the records that have an episode."""
    groups = {}
    for record in records:
        episode = record["episode"]
        if episode is None:
            continue
        if episode not in groups:
            groups[episode] = []
        groups[episode].append(record)
    return groups


def find_missing(records, required):
    """Return {episode_id: [missing categories]} for incomplete episodes.

    A set of the categories present per episode makes the "is it there?"
    check simple and ignores duplicates (W3 S20).
    """
    missing = {}
    groups = group_by_episode(records)
    for episode in sorted(groups):
        present = set()
        for record in groups[episode]:
            present.add(record["category"])
        absent = []
        for category in required:
            if category not in present:
                absent.append(category)
        if len(absent) > 0:
            missing[episode] = absent
    return missing
