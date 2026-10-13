# Episode Organizer

A command-line tool that sorts the messy export folder of a **podcast or YouTube team** into one folder per episode and one sub-folder per file type — and tells the editor which deliverables are still missing.

COE203 Advanced Programming with Python · Project 1 (file-system automation)

## The business problem

A weekly show produces raw camera files, voice recordings, thumbnails, subtitles and editor project files for every episode. Each person names files differently (`EP12_final.mp4`, `ep-12 thumb.png`, `Episode 12 voice.wav`, `S02E05_raw.mov`) and everything lands in one shared folder. Editors lose time searching, and episodes get published without a subtitle or thumbnail.

Episode Organizer:

1. **Sorts by file type** with a category dictionary (`mp4 → Video`, `srt → Subtitle`, …) loaded from `config.txt`.
2. **Detects the episode** from common naming styles and groups the files into `EP012/`, `S02E05/`, …
3. **Reports missing deliverables**, e.g. `EP003: Subtitle`, before the episode goes live.
4. **Previews first**, moves files only with `--apply`, and can **undo** the last run.

```text
inbox/                                   Episodes/
├── EP01_raw_cam.mp4                     ├── EP001/
├── ep1-final.MOV            organize    │   ├── Audio/Episode 1 voice.wav
├── Episode 1 voice.wav     ─────────►   │   ├── Subtitle/EP1.srt
├── ep_001_thumbnail.JPEG                │   ├── Thumbnail/ep_001_thumbnail.JPEG
├── EP1.srt                              │   └── Video/EP01_raw_cam.mp4, ep1-final.MOV
├── guest_notes.txt                      └── _Unsorted/
└── old_backup.zip                           ├── Notes/guest_notes.txt
                                             └── Other/old_backup.zip
```

## Requirements

- Python 3.8 or newer
- Only standard-library modules; no external package installation is needed.

## Quick start

Run every command **from the project folder** (where `config.txt` is located):

```bash
python cli.py sample demo_inbox
python cli.py scan demo_inbox
python cli.py organize demo_inbox --dest Episodes
python cli.py organize demo_inbox --dest Episodes --apply
python cli.py undo Episodes --apply
```

The `sample` command creates demo files to try the tool safely. The `organize` command previews the plan by default; add `--apply` to move files.

## Usage

```text
python cli.py ACTION FOLDER [options]
```

| Action     | `FOLDER` is                        | What it does                                                                        | Options                                                                                                        |
| ---------- | ---------------------------------- | ----------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------- |
| `scan`     | The unsorted folder                | Prints file counts and sizes per category, episodes found and missing deliverables. | `--output FILE` saves the report; `--config FILE` selects a config.                                            |
| `organize` | The unsorted folder                | Shows the move plan. **Preview is the default.**                                    | `--dest DEST` (required); `--apply` moves files; `--yes` skips confirmation; `--config FILE` selects a config. |
| `undo`     | The destination used by `organize` | Shows which files from the last run would be restored.                              | `--apply` restores them.                                                                                       |
| `sample`   | A new or empty folder              | Creates demo files; the last episode intentionally has no subtitle.                 | `--episodes N`, from 1 to 20; default is 3.                                                                    |

Run `python cli.py --help` to see the built-in help.

## Configuration (`config.txt`)

The configuration is a plain-text file that can be edited in any text editor.

```ini
[categories]
Video = mp4, mov, mkv, m4v
Audio = wav, mp3, m4a, flac, aac
Thumbnail = png, jpg, webp
Subtitle = srt, vtt
Project = prproj, aep, drp, fcpxml
Notes = txt, md, docx, pdf

[settings]
required = Video, Audio, Thumbnail, Subtitle
other_folder = Other
unsorted_folder = _Unsorted
```

| Entry             | Meaning                                                                                                 |
| ----------------- | ------------------------------------------------------------------------------------------------------- |
| `[categories]`    | `Folder = extensions`. Extensions are case-insensitive, the dot is optional and `jpeg` counts as `jpg`. |
| `required`        | Categories every episode must have; used for the missing-deliverables report.                           |
| `other_folder`    | Folder for extensions that are not listed.                                                              |
| `unsorted_folder` | Folder for files without an episode number.                                                             |

Use another file with `--config my_show.txt`. Lines starting with `#` are comments.

Invalid configurations are rejected with a line number and a reason. Validation includes unsafe folder names, duplicate extensions across categories, unknown sections or settings, nonexistent required categories, non-UTF-8 files and files over 64 KiB.

## Recognised episode names

| File name                                                       | Episode folder |
| --------------------------------------------------------------- | -------------- |
| `EP12_final.mp4`, `ep-12.png`, `Episode 12.srt`, `Bolum_12.wav` | `EP012`        |
| `S02E05_raw.mov`, `s2_e5.wav`, `S02.E05.mp4`                    | `S02E05`       |
| `deep12.mp4`, `EP0.mp4`, `EP12345.mp4`, `holiday.jpg`           | `_Unsorted`    |

## Project structure

| File               | Purpose                                                                                                                              |
| ------------------ | ------------------------------------------------------------------------------------------------------------------------------------ |
| `cli.py`           | Entry point. Defines arguments, selects actions through a dictionary, handles confirmation and displays results and expected errors. |
| `config.txt`       | Default categories, required deliverables and folder names.                                                                          |
| `config_loader.py` | Reads and validates `config.txt`, then converts category mappings into an extension-to-category dictionary.                          |
| `scanner.py`       | Lists regular files in the source folder, skips subfolders, links and hidden files, normalizes extensions and assigns categories.    |
| `episode.py`       | Detects episode IDs from filenames and identifies missing deliverables.                                                              |
| `organizer.py`     | Builds the move plan, prevents overwrites and unsafe paths, moves files, saves the undo log and restores files.                      |
| `report.py`        | Collects statistics and formats reports and file sizes.                                                                              |
| `sample.py`        | Creates demo files for safe testing.                                                                                                 |
| `contributions/`   | Individual team members' contribution documents.                                                                                     |

**Module flow:** `cli.py` → `config_loader.py`, `organizer.py`, `report.py`, `sample.py` → `episode.py`, `scanner.py`.

The CLI connects the modules; the other modules contain their respective responsibilities.

## Safety and robustness

| Risk                        | How it is handled                                                                                                                     |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| Moving the wrong files      | `organize` and `undo` preview changes unless `--apply` is supplied. Organizing also asks for confirmation unless `--yes` is supplied. |
| Overwriting a file          | Existing files are not replaced; conflicting names receive a suffix such as `name (1).ext`.                                           |
| Escaping the destination    | Configured folder names are validated, and target paths are checked against the destination.                                          |
| Symlinks and subfolders     | Skipped during scanning.                                                                                                              |
| Locked or missing files     | Individual move failures are reported, and processing continues where possible.                                                       |
| Damaged or edited undo log  | Log entries are validated before restoration; paths outside the destination are refused.                                              |
| Invalid arguments and paths | `argparse` validates command arguments, while path and configuration checks reject invalid inputs.                                    |

## How we tested

Tests should be run against disposable demo folders created with `python cli.py sample`.

| Input                                               | Expected result                                                      |
| --------------------------------------------------- | -------------------------------------------------------------------- |
| `python cli.py scan nowhere`                        | A readable error indicating that the folder does not exist.          |
| `python cli.py organize X --dest X`                 | An error stating that source and destination must differ.            |
| A configuration containing an unsafe folder name    | A configuration error identifying the invalid entry.                 |
| `python cli.py sample demo_inbox --episodes abc`    | An `argparse` error for an invalid integer.                          |
| `python cli.py sample demo_inbox --episodes 0`      | A validation error for an episode count outside the allowed range.   |
| A file already exists at the target                 | A unique filename is selected without overwriting the existing file. |
| Organize with `--apply`, then undo with `--apply`   | Files are restored where possible.                                   |
| An undo log contains a path outside the destination | Restoration is refused for the unsafe path.                          |

## Course topics used

| Topic                                                                   | Where in the code                             |
| ----------------------------------------------------------------------- | --------------------------------------------- |
| Dictionaries and `.get(key, default)` (W3 S17, S63)                     | `scanner.assign_categories`, `config_loader`  |
| Dictionary-based action selection (W3 S17)                              | `cli.ACTIONS`                                 |
| Lists, loops, `range` and accumulators (W2, W3 S59–61)                  | `report.build_statistics`, `episode`          |
| Sets and unique values (W3 S20)                                         | `episode.find_missing`, `config_loader`       |
| Returning dictionaries and tuples (W3 S18–19)                           | `config_loader`, `organizer`, `episode`       |
| String methods such as `strip`, `lower`, `split` and `join` (W3 S32–36) | `scanner`, `config_loader`, `episode`         |
| f-strings and number formatting (W3 S37–39)                             | `report`, `episode`                           |
| File reading and writing with `open()` (W2, W3 S49)                     | `config_loader`, `organizer`, `report`        |
| Filesystem operations with `os` (W3 S50–53, S60)                        | `scanner`                                     |
| Directory creation and file moving (W3 S53–56, S65)                     | `organizer`                                   |
| Preview before changing files (W3 S65–66)                               | `cli.run_organize`, `organizer.undo_last_run` |
| Exception handling (W3 S67)                                             | `organizer`, `cli.main`                       |
| Input validation with `input()` (W3 S26–27)                             | `cli.ask_yes_no`                              |
| `argparse` positionals, choices, options and flags (W3 S28–31)          | `cli.build_parser`                            |
| Helpers, `main()` and execution guard (W3 S40–43)                       | `cli.py`                                      |
| Disposable test files (W3 S68)                                          | `sample.py`                                   |

## Team

| Member             | Responsibility                                                                      | Branch                   |
| ------------------ | ----------------------------------------------------------------------------------- | ------------------------ |
| Ömer Ali Taylan    | Configuration system (`config.txt`, `config_loader.py`) and demo data (`sample.py`) | `feature/config`         |
| Zehra Nur Ak       | File scanner and type classification (`scanner.py`)                                 | `feature/scanner`        |
| Samet Öztürk       | Safe moving, preview plan and undo (`organizer.py`)                                 | `feature/organizer`      |
| Elif Aktaş         | Episode detection and statistics report (`episode.py`, `report.py`)                 | `feature/episode-report` |
| Yusuf Berke Zengin | Command-line interface, README, repository and merges (`cli.py`)                    | `feature/cli-docs`       |

Detailed contributions are available in the [`contributions/`](contributions/) folder.
