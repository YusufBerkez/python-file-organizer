"""Episode Organizer - a command-line tool for podcast and YouTube editors.

Sorts a messy recording/export folder into one folder per episode and one
sub-folder per file type, and reports which deliverables are missing.

Examples (run from the project folder):
    python cli.py sample demo_inbox
    python cli.py scan demo_inbox
    python cli.py organize demo_inbox --dest Episodes
    python cli.py organize demo_inbox --dest Episodes --apply
    python cli.py undo Episodes --apply
"""

import argparse
import os

from config_loader import DEFAULT_CONFIG_PATH, load_config
from episode import assign_episodes, find_missing
from organizer import (
    apply_plan,
    build_plan,
    relative_to,
    undo_last_run,
    validate_paths,
)
from report import build_statistics, render_report, save_report
from sample import MAX_SAMPLE_EPISODES, create_sample
from scanner import assign_categories, scan_directory


# ---------- helper functions ----------

def collect_records(source, config):
    """Scan source and give every file a category and an episode id."""
    records = scan_directory(source)
    assign_categories(
        records,
        config["extension_map"],
        config["other_folder"],
    )
    assign_episodes(records)
    return records


def ask_yes_no(question):
    """Ask until the user types yes or no; no input counts as no."""
    while True:
        try:
            reply = input(question).strip().lower()
        except EOFError:
            return False

        if reply in ("yes", "y"):
            return True
        if reply in ("no", "n"):
            return False

        print("Please enter yes or no.")


def print_moves(moves, dest):
    """Print each move as 'new/place <- old name'."""
    lines = []

    for move in moves:
        old_name = os.path.split(move["source"])[1]
        note = ""

        if move["renamed"]:
            note = "  (renamed: name already taken)"

        lines.append(
            f"  {relative_to(move['target'], dest)}  <-  "
            f"{old_name}{note}"
        )

    for line in sorted(lines):
        print(line)


def print_failures(failed):
    """Print every (move, reason) pair that could not be completed."""
    for move, reason in failed:
        print(f"  ! {os.path.split(move['source'])[1]}: {reason}")


# ---------- actions ----------

def run_scan(args):
    """Print and optionally save the statistics report for a folder."""
    config = load_config(args.config)
    records = collect_records(args.folder, config)
    stats = build_statistics(records)
    missing = find_missing(records, config["required"])

    text = render_report(
        stats,
        missing,
        os.path.abspath(args.folder),
    )
    print(text)

    if args.output is not None:
        save_report(text, args.output)
        print(f"\nReport saved to {args.output}")


def run_organize(args):
    """Preview the move plan; move files only with --apply."""
    if args.dest is None:
        raise ValueError(
            "organize needs a destination: add --dest FOLDER"
        )

    config = load_config(args.config)
    source, dest = validate_paths(args.folder, args.dest)
    records = collect_records(source, config)

    if len(records) == 0:
        print("No files to organize.")
        return

    plan = build_plan(records, dest, config["unsorted_folder"])

    print(f"Plan: {len(plan)} files from {source}")
    print_moves(plan, dest)

    if not args.apply:
        print(
            f"\nPreview only - nothing was moved. "
            f"Add --apply to move {len(plan)} files."
        )
        return

    if not args.yes and not ask_yes_no(
        f"\nMove {len(plan)} files into {dest}? [y/n] "
    ):
        print("Cancelled - nothing was moved.")
        return

    moved, failed = apply_plan(plan, dest)

    print(f"\nMoved {len(moved)} of {len(plan)} files.")
    print_failures(failed)

    if len(moved) > 0:
        print(
            f'Undo with: python cli.py undo "{args.dest}" --apply'
        )


def run_undo(args):
    """Preview or apply moving the files of the last run back."""
    dest = os.path.abspath(args.folder)
    restored, failed = undo_last_run(dest, args.apply)

    if args.apply:
        print(f"Restored {len(restored)} files:")
    else:
        print(f"Would restore {len(restored)} files:")

    for move in restored:
        print(
            f"  {relative_to(move['target'], dest)}  ->  "
            f"{move['source']}"
        )

    print_failures(failed)

    if not args.apply:
        print("\nPreview only - add --apply to undo.")


def run_sample(args):
    """Create a demo inbox folder for trying the tool safely."""
    count = create_sample(args.folder, args.episodes)
    print(f"Created {count} demo files in {args.folder}")


# A dictionary replaces an if/elif chain to pick the action.
ACTIONS = {
    "scan": run_scan,
    "organize": run_organize,
    "undo": run_undo,
    "sample": run_sample,
}


# ---------- command-line interface ----------

def build_parser():
    """Create the argparse parser."""
    parser = argparse.ArgumentParser(
        description=(
            "Sort podcast/YouTube files into episode "
            "and file-type folders."
        ),
    )

    parser.add_argument(
        "action",
        choices=["scan", "organize", "undo", "sample"],
        help="what to do",
    )
    parser.add_argument(
        "folder",
        help=(
            "scan/organize: the unsorted folder; "
            "undo: the destination; "
            "sample: a new demo folder"
        ),
    )
    parser.add_argument(
        "--dest",
        help="organize: folder that receives the episode folders",
    )
    parser.add_argument(
        "--config",
        default=DEFAULT_CONFIG_PATH,
        help="category file (default: config.txt)",
    )
    parser.add_argument(
        "--output",
        help="scan: also save the report to a new .txt or .md file",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help=(
            "organize/undo: really move the files "
            "(default is a preview)"
        ),
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="organize: skip the confirmation question",
    )
    parser.add_argument(
        "--episodes",
        type=int,
        default=3,
        help=(
            f"sample: number of demo episodes, "
            f"1-{MAX_SAMPLE_EPISODES} (default 3)"
        ),
    )

    return parser


def main():
    """Parse arguments, run the action and explain expected errors."""
    args = build_parser().parse_args()
    action = ACTIONS[args.action]

    try:
        action(args)
    except ValueError as error:
        print(f"Error: {error}")
    except OSError as error:
        print(f"Error: {error}")
    except KeyboardInterrupt:
        print("\nStopped by user.")


if __name__ == "__main__":
    main()