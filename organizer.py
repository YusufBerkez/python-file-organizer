"""Plan, apply and undo file moves safely.

Planning and moving are separate steps: build_plan() only calculates the
targets, so the same plan can be previewed (dry run) or applied (W3 S65).
Every applied move is written to a small text log so it can be undone.
"""

import os
import shutil

from scanner import validate_directory

# One line per move: run number <TAB> original path <TAB> new path
LOG_FILENAME = ".organizer_log.txt"


def is_inside(path, folder):
    """Return True if path is folder itself or anywhere below it.

    Compared in lower case because Windows paths ignore letter case.
    """
    path = os.path.abspath(path).lower()
    folder = os.path.abspath(folder).lower()
    return path == folder or path.startswith(os.path.join(folder, ""))


def relative_to(path, folder):
    """Return path without the leading folder part, for short output lines."""
    prefix = os.path.join(os.path.abspath(folder), "")
    if os.path.abspath(path).lower().startswith(prefix.lower()):
        return os.path.abspath(path)[len(prefix):]
    return path


def validate_paths(source, dest):
    """Check the source and destination folders and return absolute paths."""
    source = validate_directory(source)
    if dest.strip() == "":
        raise ValueError("Destination folder is empty.")
    dest = os.path.abspath(dest)
    if source.lower() == dest.lower():
        raise ValueError("Source and destination must be different folders.")
    if os.path.exists(dest) and not os.path.isdir(dest):
        raise NotADirectoryError(f"Destination exists but is not a folder: {dest}")
    return source, dest


def unique_target(target, planned):
    """Return target, or "name (1).ext", "name (2).ext"... if the name is taken.

    A name is taken if it exists on disk (W3 S56 collision guard) or was
    already given to another file in this plan. Names are compared in
    lower case because Windows treats "A.mp4" and "a.mp4" as the same file.
    """
    stem, extension = os.path.splitext(target)
    candidate = target
    counter = 1
    while os.path.lexists(candidate) or candidate.lower() in planned:
        candidate = f"{stem} ({counter}){extension}"
        counter += 1
    return candidate


def build_plan(records, dest, unsorted_folder):
    """Return a list of planned moves; nothing on disk is changed.

    Target layout: <dest>/<episode or unsorted_folder>/<category>/<name>
    """
    plan = []
    planned = set()
    for record in records:
        episode_folder = record["episode"]
        if episode_folder is None:
            episode_folder = unsorted_folder
        folder = os.path.join(dest, episode_folder, record["category"])
        target = os.path.join(folder, record["name"])
        if not is_inside(target, dest):
            raise ValueError(f"Refusing to move outside the destination: {target}")
        final_target = unique_target(target, planned)
        planned.add(final_target.lower())
        plan.append({
            "source": record["path"],
            "target": final_target,
            "renamed": final_target != target,
        })
    return plan
