# Contribution – Yusuf Berke Zengin

- **Student ID:** [2409111002]
- **GitHub:** [yusufberkez]
- **Role:** Team coordinator, command-line interface, documentation and merges
- **Branch / Pull Request:** `feature/cli-docs`

## Files I wrote
- `cli.py`
- `README.md`
- `.gitignore`
- `contributions/YUSUF_BERKE_ZENGIN_2409111002_YusufBerkez.md`

## What I implemented
- Created the repository, invited the team and set up one feature branch per member so nobody edited the same file; merged the pull requests in dependency order.
- `cli.py`: argparse with an `action` positional (`choices`: scan, organize, undo, sample), a `folder` positional and options such as `--dest`, `--apply` (`store_true`) and `--episodes` (`type=int`).
- The action is chosen from a dictionary of functions (`ACTIONS`) instead of an if/elif chain.
- `run_organize()` shows the plan, requires `--apply` and asks for confirmation with a validated yes/no loop (`--yes` skips it).
- `main()` turns `ValueError`, `OSError` and Ctrl+C into readable messages instead of tracebacks.
- Wrote the README with the project's purpose, usage, configuration reference, structure and course-topic map.

## Design decisions
- `cli.py` contains no business logic; it connects the existing modules.
- Script order follows the lecture: docstring → imports → helpers → `main()` → execution guard.

## Course topics I applied
- argparse: positionals, `choices`, options, `store_true`, `type=int` (W3 S28-31)
- Input validation loop with `input()` (W3 S26-27)
- A dictionary instead of repeated branches (W3 S17)
- Helpers, `main()`, `if __name__ == "__main__"` (W3 S40-43)
- f-strings for user feedback (W3 S37)
- Exception handling (W3 S67)

## Commits and repository management
1. Initial commit: add gitignore
2. Add initial README for Episode Organizer project
3. Add command-line interface with scan, organize, undo and sample
4. Write full README with usage, structure and course topics
5. Merged team pull requests into `main` in dependency order.
6. Added this contribution file.