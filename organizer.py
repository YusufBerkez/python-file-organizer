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


def move_file(source, target):
    """Move one file; return None on success or a short reason on failure (W3 S67)."""
    try:
        if not os.path.isfile(source):
            return "source file is missing"
        if os.path.lexists(target):
            return "target was created by someone else during the run"
        os.makedirs(os.path.split(target)[0], exist_ok=True)
        shutil.move(source, target)
        return None
    except FileNotFoundError:
        return "source file is missing"
    except PermissionError:
        return "permission denied (is the file open in another program?)"
    except OSError as error:
        return f"move failed: {error}"


def load_log(dest):
    """Return the logged moves as a list of [run, source, target] lists."""
    log_path = os.path.join(dest, LOG_FILENAME)
    entries = []
    if not os.path.isfile(log_path):
        return entries
    try:
        with open(log_path, encoding="utf-8") as file:
            for line in file:
                parts = line.strip("\n").split("\t")
                if len(parts) != 3:
                    raise ValueError("wrong number of columns")
                entries.append([int(parts[0]), parts[1], parts[2]])
    except ValueError:
        raise ValueError(f"Undo log is damaged: {log_path}")
    except OSError as error:
        raise ValueError(f"Undo log cannot be read: {error}")
    return entries


def save_log(dest, entries):
    """Write the log entries to dest; delete the log file when nothing is left."""
    log_path = os.path.join(dest, LOG_FILENAME)
    if len(entries) == 0:
        if os.path.isfile(log_path):
            os.remove(log_path)
        return
    with open(log_path, "w", encoding="utf-8") as file:
        for run, source, target in entries:
            file.write(f"{run}\t{source}\t{target}\n")


def last_run_number(entries):
    """Return the highest run number in the log, or 0 for an empty log."""
    highest = 0
    for entry in entries:
        if entry[0] > highest:
            highest = entry[0]
    return highest


def apply_plan(plan, dest):
    """Move every file in plan and log each move; return (moved, failed)."""
    entries = load_log(dest)  # read first: a damaged log stops the run before any move
    run = last_run_number(entries) + 1
    moved = []
    failed = []
    for move in plan:
        reason = move_file(move["source"], move["target"])
        if reason is None:
            moved.append(move)
            entries.append([run, move["source"], move["target"]])
        else:
            failed.append((move, reason))
    if len(moved) > 0:
        save_log(dest, entries)
    return moved, failed


def remove_empty_folders(folder, dest):
    """Delete folder and its empty parent folders, but never dest or above it."""
    while is_inside(folder, dest) and os.path.abspath(folder).lower() != os.path.abspath(dest).lower():
        if not os.path.isdir(folder) or len(os.listdir(folder)) > 0:
            return
        shutil.rmtree(folder)  # the folder is empty, so nothing else is removed
        folder = os.path.split(os.path.abspath(folder))[0]


def undo_last_run(dest, apply=False):
    """Move the files of the last run back; return (restored, failed).

    With apply=False this is only a preview of what would happen.
    """
    if not os.path.isdir(dest):
        raise NotADirectoryError(f"Destination folder does not exist: {dest}")
    entries = load_log(dest)
    if len(entries) == 0:
        raise ValueError("Nothing to undo: no previous run was found in this folder.")

    last_run = last_run_number(entries)
    keep = []  # log entries that stay for a later undo
    restored = []
    failed = []
    for entry in entries:
        run, source, target = entry
        if run != last_run:
            keep.append(entry)
            continue
        move = {"source": source, "target": target}
        if not is_inside(target, dest):
            reason = "logged target is outside the destination"
        elif not os.path.isfile(target):
            reason = "file is no longer in the destination"
        elif os.path.lexists(source):
            reason = "original location is already taken"
        elif apply:
            reason = move_file(target, source)
        else:
            reason = None
        if reason is None:
            restored.append(move)
            if apply:
                remove_empty_folders(os.path.split(target)[0], dest)
        else:
            failed.append((move, reason))
            keep.append(entry)

    if apply:
        save_log(dest, keep)
    return restored, failed
