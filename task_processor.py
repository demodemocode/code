import os
import re
import json
import requests
from pathlib import Path
import typer
from rich.console import Console
from sentence_transformers import SentenceTransformer, util

# Local utilities
from codi.logic.utils import load_json, save_json


# ============================================================
# CONSTANTS / CONFIG
# ============================================================

console = Console()
TASKS = Path(".codi/tasks.json")
INDEX = Path(".codi/index.json")

# Load embedding model (global init)
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")


# ============================================================
# STORAGE UTILITIES
# ============================================================

def ensure_tasks_exists():
    """Return loaded tasks JSON or empty dict."""
    if not TASKS.exists():
        return {}
    return load_json(TASKS)


def load_index():
    """Load the code index, error if not found."""
    if not INDEX.exists():
        console.print("[bold red]❌ No index found. Run `codi init` first.[/bold red]")
        raise typer.Exit()
    return json.load(INDEX.open())


def semantic_fields(semantic):
    """Merge semantic metadata fields into one large list of strings."""
    return (
        semantic.get("keywords", []) +
        semantic.get("capabilities", []) +
        semantic.get("side_effects", []) +
        semantic.get("inputs", []) +
        semantic.get("outputs", []) +
        semantic.get("risks", []) +
        semantic.get("patterns", [])
    )


# ============================================================
# SCORING ENGINE
# ============================================================

def compute_score(task_keywords, file_meta):
    """
    Hybrid scoring: semantic similarity + keyword overlap + function matching.
    """

    if not task_keywords:
        return 0.0

    semantic = file_meta.get("semantic", {})
    functions = file_meta.get("functions", [])

    sem_block = semantic_fields(semantic) + functions
    file_keywords = semantic.get("keywords", [])

    if not sem_block:
        return 0.0

    # --- Keyword overlap ---
    task_set = {k.lower() for k in task_keywords}
    file_set = {k.lower() for k in file_keywords}
    keyword_score = len(task_set & file_set) / max(len(task_set), 1)

    # --- Function name matching ---
    fn_set = {fn.lower() for fn in functions}
    function_score = len(task_set & fn_set) / max(len(fn_set), 1)

    # --- Semantic embedding similarity ---
    emb_task = model.encode(" ".join(task_keywords), convert_to_tensor=True)
    emb_file = model.encode(" ".join(sem_block), convert_to_tensor=True)

    semantic_score = float(util.cos_sim(emb_task, emb_file))

    # --- Weighted hybrid score ---
    final_score = (
        0.50 * semantic_score +
        0.30 * keyword_score +
        0.20 * function_score
    )

    return round(final_score, 3)


# ============================================================
# TASK LISTING
# ============================================================

def list_tasks():
    console.print("\n[bold cyan]📋 Saved Tasks:[/bold cyan]\n")

    tasks = ensure_tasks_exists()
    if not tasks:
        console.print("[bold red]❌ No tasks created yet.[/bold red]")
        return

    for task_id, data in tasks.items():
        console.print(f"[bold yellow]ID:[/bold yellow] {task_id}")
        console.print(f"  📝 {data.get('description', '')}")

        best = (data.get("matches") or [{}])[0]
        if best:
            console.print(
                f"  📌 Best match: {best.get('file')} "
                f"({best.get('score')})"
            )
        console.print("")


# ============================================================
# TASK RE-RUN
# ============================================================

def run_existing_task(id: str):
    console.print("\n[bold cyan]🔁 Re-processing task...[/bold cyan]\n")

    tasks = ensure_tasks_exists()

    if id not in tasks:
        console.print(f"[bold red]❌ Task '{id}' does not exist.[/bold red]")
        console.print(f"👉 Run: [yellow]codi task --id {id} --desc \"your description\"[/yellow]")
        raise typer.Exit()

    process_task(id, tasks[id]["description"])
    console.print("\n[bold green]✓ Task reprocessed successfully![/bold green]\n")


# ============================================================
# CREATE OR UPDATE TASK
# ============================================================

def create_or_update_task(id: str, description: str):
    console.print(f"📝 Updating task: [bold]{id}[/bold]")
    process_task(id, description)
    console.print("\n[bold green]✓ Task saved & processed![/bold green]\n")


# ============================================================
# MAIN TASK PROCESSOR
# ============================================================

def process_task(id: str, description: str):
    console.print("🔑 Extracting keywords...")

    task_keywords = extract_keywords_from_ai(description)
    console.print(f"[green]✓ Keywords:[/green] {task_keywords}\n")

    index_data = load_index()
    matches = []

    # Score each index entry
    for entry in index_data:
        score = compute_score(task_keywords, entry)

        if score > 0:
            matches.append({
                "file": entry.get("path"),
                "score": score,
                "functions": entry.get("functions", []),
                "keywords": entry.get("keywords", []),
                "semantic": entry.get("semantic", {}),
                "related_files": entry.get("related_files", []),
            })

    # Sort best → worst
    matches.sort(key=lambda x: x["score"], reverse=True)

    # Store
    tasks = ensure_tasks_exists()
    tasks[id] = {
        "description": description,
        "keywords": task_keywords,
        "matches": matches,
    }
    save_json(TASKS, tasks)

    # Display
    console.print("\n📁 [cyan]Top matching files:[/cyan]")
    for m in matches[:5]:
        console.print(f"  → {m['file']} ({m['score']})")

    return matches


# ============================================================
# AI KEYWORD EXTRACTION (INLINE)
# ============================================================

class MissingAPIKeyError(Exception):
    pass


def extract_keywords_from_ai(content: str):
    """LLM-powered keyword extraction."""
    api_key, model, url = validate_ai_env()
    prompt = build_keyword_prompt(content)
    response = call_ai_api(api_key, model, url, prompt)
    data = safe_json_extract_object(response)
    return data.get("keywords", [])


def validate_ai_env():
    """Ensure required env values are set."""
    api_key = os.getenv("AI_API_KEY")
    model = os.getenv("AI_MODEL")
    url = os.getenv("AI_URL")

    if not api_key:
        raise MissingAPIKeyError("❌ Missing environment variable: AI_API_KEY")
    if not model:
        raise RuntimeError("❌ Missing AI_MODEL")
    if not url:
        raise RuntimeError("❌ Missing AI_URL")

    return api_key, model, url


def build_keyword_prompt(content: str):
    """Prompt strictly enforcing compact JSON output."""
    return f"""
You are an expert system. Extract semantic task-related keywords from the text.

Return ONLY strict JSON:
{{
  "keywords": []
}}

Rules:
- No code syntax terms
- No framework/library names
- Only conceptual task-related keywords
- Output must be valid JSON

---------------------
TEXT:
{content}
---------------------
"""


def call_ai_api(api_key, model, url, prompt):
    """Call OpenAI-compatible LLM API."""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.0
    }

    response = requests.post(url, headers=headers, json=payload, timeout=30)
    response.raise_for_status()

    return response.json()["choices"][0]["message"]["content"]


def safe_json_extract_object(text: str):
    """Extract and parse JSON from arbitrary AI output."""
    match = re.search(r"\{[\s\S]*?\}", text)
    if not match:
        return {"keywords": []}

    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return {"keywords": []}
