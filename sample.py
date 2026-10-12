"""Create a disposable demo inbox so the tool can be tried safely (W3 S68).

The files are tiny text files with realistic podcast/YouTube names, in all
the naming styles the episode detector understands. The last episode has
no subtitle on purpose, so the "missing deliverables" report has something
to show.
"""

import os

MAX_SAMPLE_EPISODES = 20

EXTRA_FILES = [
    "S02E01_teaser.mp4",
    "guest_notes.txt",
    "invoice_october.pdf",
    "funny_meme.png",
    "README",
    "old_backup.zip",
]


def sample_names(episodes):
    """Return the list of demo file names for the given number of episodes."""
    names = []
    for number in range(1, episodes + 1):
        names.append(f"EP{number:02d}_raw_cam.mp4")
        names.append(f"ep{number}-final.MOV")
        names.append(f"Episode {number} voice.wav")
        names.append(f"ep_{number:03d}_thumbnail.JPEG")
        if number != episodes:  # the last episode has no subtitle
            names.append(f"EP{number}.srt")
    for name in EXTRA_FILES:
        names.append(name)
    return names


def create_sample(folder, episodes):
    """Create the demo files in a new or empty folder; return how many were made."""
    if episodes < 1 or episodes > MAX_SAMPLE_EPISODES:
        raise ValueError(f"--episodes must be between 1 and {MAX_SAMPLE_EPISODES}.")
    if folder.strip() == "":
        raise ValueError("Sample folder path is empty.")
    if os.path.exists(folder):
        if not os.path.isdir(folder) or len(os.listdir(folder)) > 0:
            raise ValueError(f"Sample folder must be new or empty: {folder}")

    os.makedirs(folder, exist_ok=True)
    names = sample_names(episodes)
    for name in names:
        with open(os.path.join(folder, name), "w", encoding="utf-8") as file:
            file.write(f"demo file: {name}\n")
    return len(names)
