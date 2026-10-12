"""Load and validate the category configuration (config.txt).

The configuration is a plain text file that anyone can edit in Notepad:

    [categories]
    Video = mp4, mov
    [settings]
    required = Video
    other_folder = Other
    unsorted_folder = _Unsorted

Everything read from disk is treated as untrusted input: a broken or
malicious config must give a clear error message, never a crash or a
folder outside the destination.
"""

import os

from scanner import normalize_extension

DEFAULT_CONFIG_PATH = "config.txt"
MAX_CONFIG_BYTES = 64 * 1024
SETTING_NAMES = {"required", "other_folder", "unsorted_folder"}

# Only these characters may appear in folder names, so a category such as
# "../../Windows" or "C:\Temp" can never be built (whitelist, not blacklist).
SAFE_NAME_CHARACTERS = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 _-")
SAFE_EXTENSION_CHARACTERS = set("abcdefghijklmnopqrstuvwxyz0123456789")
MAX_NAME_LENGTH = 40

# Windows refuses to create folders with these names.
RESERVED_NAMES = {"con", "prn", "aux", "nul"}
for number in range(1, 10):
    RESERVED_NAMES.add(f"com{number}")
    RESERVED_NAMES.add(f"lpt{number}")


def read_config_lines(path):
    """Return the lines of the config file, or raise ValueError with the reason."""
    if not os.path.isfile(path):
        raise ValueError(f"Config file not found: {path} (run the tool from the project folder or use --config)")
    if os.path.getsize(path) > MAX_CONFIG_BYTES:
        raise ValueError(f"Config file is larger than {MAX_CONFIG_BYTES // 1024} KiB: {path}")
    lines = []
    try:
        with open(path, encoding="utf-8") as file:
            for line in file:
                lines.append(line)
    except UnicodeDecodeError:
        raise ValueError(f"Config file is not UTF-8 text: {path}")
    except OSError as error:
        raise ValueError(f"Could not read config file: {error}")
    return lines


def split_values(text):
    """Turn "mp4, MOV ,mkv" into ["mp4", "MOV", "mkv"] and drop empty items."""
    values = []
    for part in text.split(","):
        part = part.strip()
        if part != "":
            values.append(part)
    return values


def validate_folder_name(name, line_number):
    """Return name if it is safe to use as a folder name, else raise ValueError."""
    if name == "" or len(name) > MAX_NAME_LENGTH:
        raise ValueError(f"Config line {line_number}: folder names must be 1-{MAX_NAME_LENGTH} characters.")
    for character in name:
        if character not in SAFE_NAME_CHARACTERS:
            raise ValueError(f"Config line {line_number}: '{name}' may only use letters, digits, spaces, '-' and '_'.")
    if name.lower() in RESERVED_NAMES:
        raise ValueError(f"Config line {line_number}: '{name}' is a name reserved by Windows.")
    return name


def add_category(extension_map, category, text, line_number):
    """Add every extension of one "Category = ext, ext" line to extension_map.

    The map is inverted ({"mp4": "Video"}) so the scanner can find a
    category with a single .get() call instead of an if/elif chain (W3 S17).
    """
    extensions = split_values(text)
    if len(extensions) == 0:
        raise ValueError(f"Config line {line_number}: category '{category}' has no extensions.")
    for raw_extension in extensions:
        extension = normalize_extension(raw_extension)
        if extension == "" or len(extension) > 10:
            raise ValueError(f"Config line {line_number}: invalid extension '{raw_extension}'.")
        for character in extension:
            if character not in SAFE_EXTENSION_CHARACTERS:
                raise ValueError(f"Config line {line_number}: invalid extension '{raw_extension}'.")
        owner = extension_map.get(extension)
        if owner is not None and owner != category:
            raise ValueError(f"Config line {line_number}: '.{extension}' is already listed under '{owner}'.")
        extension_map[extension] = category


def parse_config(lines):
    """Read the [categories] and [settings] sections.

    Returns a tuple: (extension_map, category_names, settings) where
    settings maps a setting name to a (value, line_number) tuple.
    """
    extension_map = {}
    category_names = set()
    settings = {}
    section = ""
    line_number = 0
    for line in lines:
        line_number += 1
        text = line.strip()
        if text == "" or text.startswith("#"):
            continue
        if text.startswith("[") and text.endswith("]"):
            section = text[1:-1].strip().lower()
            if section != "categories" and section != "settings":
                raise ValueError(f"Config line {line_number}: unknown section [{section}].")
            continue

        parts = text.split("=")
        if len(parts) != 2:
            raise ValueError(f"Config line {line_number}: expected 'name = value'.")
        name = parts[0].strip()
        value = parts[1].strip()

        if section == "categories":
            validate_folder_name(name, line_number)
            if name in category_names:
                raise ValueError(f"Config line {line_number}: category '{name}' is defined twice.")
            category_names.add(name)
            add_category(extension_map, name, value, line_number)
        elif section == "settings":
            if name not in SETTING_NAMES:
                raise ValueError(f"Config line {line_number}: unknown setting '{name}'.")
            settings[name] = (value, line_number)
        else:
            raise ValueError(f"Config line {line_number}: '{name}' must be inside [categories] or [settings].")
    return extension_map, category_names, settings


def load_config(path=DEFAULT_CONFIG_PATH):
    """Load, validate and return the configuration as a dictionary.

    The result has the keys: extension_map, categories, required,
    unsorted_folder and other_folder.
    """
    lines = read_config_lines(path)
    extension_map, category_names, settings = parse_config(lines)
    if len(category_names) == 0:
        raise ValueError("Config needs at least one category in [categories].")

    other_value, other_line = settings.get("other_folder", ("Other", 0))
    unsorted_value, unsorted_line = settings.get("unsorted_folder", ("_Unsorted", 0))
    required_value, required_line = settings.get("required", ("", 0))

    required = split_values(required_value)
    for category in required:
        if category not in category_names:
            raise ValueError(f"Config line {required_line}: required category '{category}' is not in [categories].")

    return {
        "extension_map": extension_map,
        "categories": sorted(category_names),
        "required": required,
        "other_folder": validate_folder_name(other_value, other_line),
        "unsorted_folder": validate_folder_name(unsorted_value, unsorted_line),
    }
