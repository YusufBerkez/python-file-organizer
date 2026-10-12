"""Build the statistics report shown by "scan" and saved with --output.

Statistics are collected with the accumulator pattern from the lecture
analyzer (W3 S59-61) and printed with f-strings (W3 S37-39).
"""

import os

ALLOWED_REPORT_EXTENSIONS = (".txt", ".md")


def format_size(size):
    """Return a byte count in readable units, e.g. 1536000 -> "1.5 MiB" (W3 S58)."""
    amount = float(size)
    for unit in ("B", "KiB", "MiB", "GiB"):
        if amount < 1024:
            return f"{amount:.1f} {unit}"
        amount /= 1024
    return f"{amount:.1f} TiB"


def build_statistics(records):
    """Return a dictionary with totals per category and per episode."""
    stats = {
        "total_files": 0,
        "total_size": 0,
        "categories": {},
        "episodes": set(),
        "unsorted": 0,
    }
    for record in records:
        stats["total_files"] += 1
        stats["total_size"] += record["size"]

        entry = stats["categories"].setdefault(record["category"], {"files": 0, "size": 0})
        entry["files"] += 1
        entry["size"] += record["size"]

        if record.get("episode"):
            stats["episodes"].add(record["episode"])
        else:
            stats["unsorted"] += 1
    return stats


def render_report(stats, missing, source):
    """Return the full report as one multi-line string."""
    lines = [
        "Episode Organizer report",
        "========================",
        f"Source folder : {source}",
        f"Files         : {stats['total_files']} ({format_size(stats['total_size'])})",
        f"Episodes      : {len(stats['episodes'])} ({', '.join(sorted(stats['episodes'])) or '-'})",
        f"No episode id : {stats['unsorted']} files",
        "",
        "Files per category:",
    ]
    for category, entry in sorted(stats["categories"].items()):
        lines.append(f"  {category:<12} {entry['files']:>5} files  {format_size(entry['size']):>10}")

    lines.append("")
    if missing:
        lines.append("Missing deliverables:")
        for episode, categories in missing.items():
            lines.append(f"  {episode}: {', '.join(categories)}")
    else:
        lines.append("Every episode has all required file types.")
    return "\n".join(lines)


def save_report(text, path):
    """Write the report to a new .txt or .md file; never overwrite a file."""
    if not path.lower().endswith(ALLOWED_REPORT_EXTENSIONS):
        raise ValueError("Report file must end with .txt or .md")
    if os.path.lexists(path):
        raise FileExistsError(f"Report file already exists: {path}")
    folder = os.path.dirname(os.path.abspath(path))
    if not os.path.isdir(folder):
        raise NotADirectoryError(f"Folder for the report does not exist: {folder}")
    with open(path, "w", encoding="utf-8") as file:
        file.write(text + "\n")
    return path
