from pathlib import Path

HOME = Path.home()
DATA_DIR = HOME / ".octavius"
DATA_DIR.mkdir(parents=True, exist_ok=True)

JOURNAL_PATH = DATA_DIR / "journal.jsonl"
PENDING_PATH = DATA_DIR / "pending.jsonl"
CONFIG_PATH = DATA_DIR / "config.json"

HOST = "127.0.0.1"
PORT = 7777

UE5_SEARCH_ROOTS = [
    HOME / "Documents" / "Unreal Projects",
    HOME / "Unreal Projects",
    Path("/Applications"),
    Path("/Users/Shared/Epic Games"),
]

APPROVAL_TIMEOUT_SECONDS = 300
