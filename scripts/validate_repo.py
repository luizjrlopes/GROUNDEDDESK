from pathlib import Path
import ast, json, sys, tomllib
ROOT=Path(__file__).resolve().parents[1]
required=["README.md","docker-compose.yml","apps/api/app/main.py","apps/api/app/models.py","apps/api/app/rag.py","apps/api/app/worker.py","apps/web/package.json","apps/web/src/app/(app)/tickets/[id]/page.tsx","apps/web/src/app/(app)/knowledge/page.tsx","apps/web/src/app/(app)/search/page.tsx"]
errors=[]
for p in required:
    if not (ROOT/p).exists(): errors.append(f"missing {p}")
for p in ROOT.rglob("*.py"):
    if ".context-integrity" in p.parts: continue
    try: ast.parse(p.read_text(encoding="utf-8"),filename=str(p))
    except SyntaxError as e: errors.append(f"python syntax {p.relative_to(ROOT)}: {e}")
for p in ROOT.rglob("*.json"):
    if ".context-integrity" in p.parts: continue
    try: json.loads(p.read_text(encoding="utf-8"))
    except Exception as e: errors.append(f"json {p.relative_to(ROOT)}: {e}")
with open(ROOT/'apps/api/pyproject.toml','rb') as f: tomllib.load(f)
text='\n'.join(p.read_text(encoding='utf-8',errors='ignore') for p in ROOT.rglob('*') if p.is_file() and '.context-integrity' not in p.parts and p.resolve()!=Path(__file__).resolve())
for token in ["GD-1842","AI_DRAFT_GENERATED","DOCUMENT_REPROCESS","reciprocal_rank_fusion","TICKET_TRANSITIONS","requester","kbadmin","pgvector"]:
    if token not in text: errors.append(f"coverage token missing: {token}")
if "TODO" in text or "FIXME" in text: errors.append("TODO/FIXME marker found")
print(f"files={sum(1 for p in ROOT.rglob('*') if p.is_file() and '.context-integrity' not in p.parts)}")
if errors:
    print("VALIDATION: FAIL"); [print("-",e) for e in errors]; sys.exit(1)
print("VALIDATION: PASS")
