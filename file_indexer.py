import os
import json
import re
from pathlib import Path
from typing import List, Dict, Any
import requests
import typer

from codi.logic.utils import is_text_file
from codi.constants import SKIP_DIRS, SKIP_FILES


# ============================================================
# Exceptions
# ============================================================

class MissingAPIKeyError(Exception):
    """Raised when AI_API_KEY is not found."""
    pass


# ============================================================
# Main Indexer
# ============================================================

def index_project():
    """
    Index all project text files:
    - Extract semantic metadata (AI)
    - Extract functions/classes
    - Detect related files via keyword similarity
    """

    root = Path(".").resolve()
    codi_folder = root / ".codi"
    index_path = codi_folder / "index.json"

    codi_folder.mkdir(exist_ok=True)
    typer.echo("🔍 CODI: Indexing project...\n")

    files_data = collect_files_data(root)
    create_file_relationships(files_data)
    save_index(index_path, files_data)

    typer.echo("\n✅ CODI: Indexing completed!")
    typer.echo(f"📁 Saved: {index_path}")


# ============================================================
# Indexing Steps
# ============================================================

def collect_files_data(root: Path) -> List[Dict[str, Any]]:
    """Walk the directory and extract static + AI metadata."""
    
    files_data = []

    for path, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]

        for filename in files:
            if filename in SKIP_FILES:
                continue

            file_path = Path(path) / filename
            if not is_text_file(file_path):
                continue

            rel = file_path.relative_to(root)
            typer.echo(f"📄 Processing: {rel}")

            content = file_path.read_text(errors="ignore")

            metadata = extract_keywords_from_ai(content)

            files_data.append({
                "path": str(rel),
                "semantic": metadata,              # NEW FULL METADATA OBJECT
                "keywords": metadata.get("keywords", []),
                "functions": extract_functions(content),
                "related_files": []
            })

    return files_data


# ============================================================
# File Relationship Builder
# ============================================================

def create_file_relationships(files_data: List[Dict[str, Any]]):
    """Calculate file → related files using keyword similarity."""

    for file in files_data:
        for other in files_data:
            if file["path"] == other["path"]:
                continue

            shared = len(set(file["keywords"]) & set(other["keywords"]))
            if shared >= 2:
                file["related_files"].append(other["path"])


def save_index(path: Path, data: List[Dict[str, Any]]):
    """Save index.json cleanly."""
    with path.open("w") as f:
        json.dump(data, f, indent=2)


# ============================================================
# Function Extraction
# ============================================================

def extract_functions(content: str) -> List[str]:
    """Extract function, class, and method names for JS/Python/Java."""

    patterns = [
        r"\bfunction\s+([a-zA-Z_][a-zA-Z0-9_]*)",
        r"([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*\([^)]*\)\s*=>",
        r"\bexport function\s+([a-zA-Z_][a-zA-Z0-9_]*)",
        r"\bclass\s+([A-Za-z_][A-Za-z0-9_]*)",
        r"\bdef\s+([a-zA-Z_][a-zA-Z0-9_]*)",
        r"(?:public|private|protected)\s+[a-zA-Z<>]+\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\("
    ]

    extracted = set()

    for pattern in patterns:
        for match in re.findall(pattern, content):
            extracted.add(match if isinstance(match, str) else match[-1])

    return list(extracted)


# ============================================================
# AI Keyword / Metadata Extraction
# ============================================================

def extract_keywords_from_ai(content: str) -> Dict[str, Any]:
    """Query AI model and extract structured metadata."""
    
    api_key, model, url = validate_ai_env()
    prompt = build_keyword_prompt(content)
    response = call_ai_api(api_key, model, url, prompt)

    # Return structured object (not just keywords)
    return safe_json_extract_object(response)


def validate_ai_env():
    """Ensure required env vars exist."""
    api_key = os.getenv("AI_API_KEY")
    model = os.getenv("AI_MODEL")
    url = os.getenv("AI_URL")

    if not api_key:
        raise MissingAPIKeyError("❌ Missing AI_API_KEY")

    if not model:
        raise RuntimeError("❌ Missing AI_MODEL")

    if not url:
        raise RuntimeError("❌ Missing AI_URL")

    return api_key, model, url


# ============================================================
# New Deep Metadata Prompt
# ============================================================

def build_keyword_prompt(content: str) -> str:
    """Create an advanced prompt for extracting deep semantic code metadata."""
    return f"""
You are an expert software architect. Analyze the following code and extract **deep semantic metadata**.

🎯 GOAL  
Describe WHAT this code does — not the syntax or framework.

📌 OUTPUT (JSON ONLY)
Return EXACTLY this structure:

{{
  "keywords": [],
  "capabilities": [],
  "side_effects": [],
  "inputs": [],
  "outputs": [],
  "risks": [],
  "patterns": [],
  "data_entities": [],
  "external_dependencies": []
}}

⚠ RULES
- ❌ No library/framework names (React, Express, Django, etc)
- ❌ No trivial syntax terms (function, const, import, class, etc)
- ✔ Use meaningful business logic verbs
- ✔ Capture intent, behavior, purpose, domain actions
- ✔ Extract hidden workflows, data flow, and responsibilities

--------------------
CODE:
{content}
--------------------
"""


# ============================================================
# AI Call
# ============================================================

def call_ai_api(api_key: str, model: str, url: str, prompt: str) -> str:
    """Send request to LLM and retrieve content."""

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2
    }

    res = requests.post(url, headers=headers, json=payload, timeout=30)
    res.raise_for_status()

    return res.json()["choices"][0]["message"]["content"]


# ============================================================
# Robust JSON Extraction
# ============================================================

def safe_json_extract_object(text: str) -> Dict[str, Any]:
    """
    Extract a JSON object from LLM output.
    Supports objects spanning multiple lines.
    """

    match = re.search(r"\{[\s\S]*\}", text)
    if not match:
        return {"keywords": []}  # fallback

    try:
        return json.loads(match.group(0))
    except Exception:
        return {"keywords": []}  # fallback


# ============================================================
# End of file
# ============================================================
