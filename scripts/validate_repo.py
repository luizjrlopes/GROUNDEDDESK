from pathlib import Path
import ast, json, sys, tomllib

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED_DIRS = {
    ".git",
    ".context-integrity",
    ".next",
    "node_modules",
    "__pycache__",
    ".venv",
    "dist",
    "build",
    "coverage",
}

required = [
    "README.md",
    "docker-compose.yml",
    "apps/api/app/main.py",
    "apps/api/app/models.py",
    "apps/api/app/rag.py",
    "apps/api/app/worker.py",
    "apps/web/package.json",
    "apps/web/src/app/(app)/tickets/[id]/page.tsx",
    "apps/web/src/app/(app)/knowledge/page.tsx",
    "apps/web/src/app/(app)/search/page.tsx",
]
errors = []


def excluded(path: Path) -> bool:
    relative = path.relative_to(ROOT)
    return any(part in EXCLUDED_DIRS for part in relative.parts)


for item in required:
    if not (ROOT / item).exists():
        errors.append(f"missing {item}")

for path in ROOT.rglob("*.py"):
    if excluded(path):
        continue
    try:
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except SyntaxError as exc:
        errors.append(f"python syntax {path.relative_to(ROOT)}: {exc}")

for path in ROOT.rglob("*.json"):
    if excluded(path):
        continue
    try:
        json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"json {path.relative_to(ROOT)}: {exc}")

with open(ROOT / "apps/api/pyproject.toml", "rb") as file:
    tomllib.load(file)

files = [
    path
    for path in ROOT.rglob("*")
    if path.is_file() and not excluded(path) and path.resolve() != Path(__file__).resolve()
]
text = "\n".join(path.read_text(encoding="utf-8", errors="ignore") for path in files)

for token in [
    "GD-1842",
    "AI_DRAFT_GENERATED",
    "DOCUMENT_REPROCESS",
    "reciprocal_rank_fusion",
    "TICKET_TRANSITIONS",
    "requester",
    "kbadmin",
    "pgvector",
]:
    if token not in text:
        errors.append(f"coverage token missing: {token}")

if "TODO" in text or "FIXME" in text:
    errors.append("TODO/FIXME marker found")

print(f"files={len(files) + 1}")
if errors:
    print("VALIDATION: FAIL")
    for error in errors:
        print("-", error)
    sys.exit(1)

print("VALIDATION: PASS")
