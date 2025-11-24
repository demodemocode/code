import json
from pathlib import Path

TEXT_EXT = {
    ".py", ".js", ".ts", ".tsx", ".jsx",
    ".java", ".go", ".cpp", ".c", ".h",
    ".css", ".html", ".md", ".json",
    ".yml", ".yaml", ".txt"
}

def is_text_file(path: Path):
    return path.suffix.lower() in TEXT_EXT



def load_json(path: Path):
    if not path.exists():
        return {}
    try:
        return json.load(path.open())
    except:
        return {}


def save_json(path: Path, data):
    path.parent.mkdir(exist_ok=True)
    json.dump(data, path.open("w"), indent=2)
