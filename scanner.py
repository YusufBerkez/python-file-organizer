"""Scan a source folder and describe every regular file inside it.

The scanner only reads names and sizes; it never changes the file system.
Each file becomes a small record (a dictionary) that the other modules
fill in step by step: category -> episode -> target path.
"""

import os

# Different spellings of the same format share one category (W3 S35-36).
EXTENSION_ALIASES = {"jpeg": "jpg", "tif": "tiff", "markdown": "md"}

# System files that editors never want to see in an episode folder.
IGNORED_NAMES = {"desktop.ini", "thumbs.db", ".ds_store"}

# Protects the tool from a folder with an absurd number of files.
MAX_FILES = 10000


def normalize_extension(extension):
    """Return extension in lower case, without the dot, with aliases merged.

    Example: " .JPEG " -> "jpg"
    """
    clean = extension.strip().lower()
    if clean.startswith("."):
        clean = clean[1:]
    return EXTENSION_ALIASES.get(clean, clean)


def get_extension(filename):
    """Return the normalized extension of filename, or "" if it has none (W3 S57)."""
    extension = os.path.splitext(filename)[1]
    return normalize_extension(extension)


def should_skip(filename):
    """Return True for hidden files, system junk and names the undo log cannot store."""
    if filename.startswith(".") or filename.lower() in IGNORED_NAMES:
        return True
    # The undo log uses tabs and new lines as separators.
    return "\t" in filename or "\n" in filename


def validate_directory(path):
    """Check that path is an existing folder and return its absolute path."""
    if path.strip() == "":
        raise ValueError("Folder path is empty.")
    if not os.path.isdir(path):
        raise NotADirectoryError(f"Not a folder: {path}")
    return os.path.abspath(path)
