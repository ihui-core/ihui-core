import os
import sys
import json
import re
from pathlib import Path
from datetime import datetime, timezone
import requests
import jsonschema

REPO_NAME = os.getenv("GITHUB_REPOSITORY", "ihui-core/ihui-core")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
BASE_DIR = Path(__file__).resolve().parent.parent
SESSIONS_DIR = BASE_DIR / ".sessions"
PROJECTBRAIN_DIR = BASE_DIR / "PROJECTBRAIN"
SCHEMA_PATH = BASE_DIR / "docengine" / "schema_session_v1.json"
OUTPUT_DIR = BASE_DIR / "docengine" / "dashboard" / "public" / "data"

HEADERS = {
    "Accept": "application/vnd.github.v3+json",
    "User-Agent": "ihui-Core-Doc-Engine"
}
if GITHUB_TOKEN:
    HEADERS["Authorization"] = f"token {GITHUB_TOKEN}"

def fetch_github_api(endpoint: str):
    url = f"https://api.github.com/repos/{REPO_NAME}/{endpoint}"
    try:
        res = requests.get(url, headers=HEADERS, timeout=15)
        if res.status_code == 200:
            return res.json()
        print(f"[WARN] GitHub API {endpoint} retornó HTTP {res.status_code}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"[ERROR] Error al conectar con GitHub API ({endpoint}): {e}", file=sys.stderr)
        return None

def load_schema():
    if not SCHEMA_PATH.exists():
        print(f"[ERROR] Esquema no encontrado en {SCHEMA_PATH}", file=sys.stderr)
        sys.exit(1)
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def process_sessions(schema, github_data):
    sessions = []
    invalid_sessions = []
    if not SESSIONS_DIR.exists():
        return [], []
    for file_path in SESSIONS_DIR.glob("*.json"):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = json.load(f)
            jsonschema.validate(instance=content, schema=schema)
            content["verification"] = verify_claims(content, github_data)
            sessions.append(content)
        except jsonschema.ValidationError as err:
            invalid_sessions.append({"file_name": file_path.name, "error": f"Error de Esquema: {err.message}", "raw_content": None})
        except Exception as err:
            invalid_sessions.append({"file_name": file_path.name, "error": f"Error: {str(err)}", "raw_content": None})
    sessions.sort(key=lambda x: x.get("started_at", ""), reverse=True)
    return sessions, invalid_sessions

def verify_claims(session, github_data):
    claims = session.get("claims", {})
    branch_name = session.get("branch", "")
    files_claimed = claims.get("files_modified", [])
    adrs_claimed = claims.get("adrs_touched", [])
    prs_claimed = claims.get("prs", [])

    branch_commits = github_data.get("branch_commits", {}).get(branch_name, [])
    branch_files = set()
    for c in branch_commits:
        branch_files.update(c.get("files", []))

    files_verification = []
    files_ok = True
    for f in files_claimed:
        found = f in branch_files
        files_verification.append({"file": f, "status": "VERIFICADO" if found else "NO_ENCONTRADO"})
        if not found: files_ok = False

    real_prs = {pr["number"]: pr for pr in github_data.get("prs", [])}
    prs_verification = []
    prs_ok = True
    for pr in prs_claimed:
        pr_num = pr.get("number")
        found = pr_num in real_prs
        prs_verification.append({"number": pr_num, "status": "VERIFICADO" if found else "NO_ENCONTRADO"})
        if not found: prs_ok = False

    commits_main = github_data.get("main_commits", [])
    adrs_verification = []
    adrs_ok = True
    for adr_id in adrs_claimed:
        adr_num_match = re.search(r'\d+', adr_id)
        found = False
        if adr_num_match:
            num = adr_num_match.group(0).zfill(3)
            pattern_trailer = f"ADR: {num}"
            pattern_literal = f"ADR-{num}"
            for commit in commits_main + branch_commits:
                msg = commit.get("message", "")
                if pattern_trailer in msg or pattern_literal in msg:
                    found = True
                    break
        adrs_verification.append({"adr": adr_id, "status": "VERIFICADO" if found else "NO_ENCONTRADO"})
        if not found: adrs_ok = False

    if files_ok and prs_ok and adrs_ok:
        status = "VERIFICADO"
    elif not files_ok or not prs_ok or not adrs_ok:
        status = "DISCREPANCIA"
    else:
        status = "NO_ENCONTRADO"

    return {
        "status": status,
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "details": {"files": files_verification, "adrs": adrs_verification, "prs": prs_verification}
    }

def process_adrs(commits_main):
    adrs = []
    adr_file = PROJECTBRAIN_DIR / "ADRS.md"
    if not adr_file.exists():
        found_adrs = list(PROJECTBRAIN_DIR.glob("**/*ADR*.md"))
        if found_adrs: adr_file = found_adrs[0]
    if not adr_file.exists(): return adrs

    content = adr_file.read_text(encoding="utf-8")
    adr_blocks = re.split(r'(?=^##\s+ADR-\d+)', content, flags=re.MULTILINE)

    for block in adr_blocks:
        match_title = re.search(r'^##\s+ADR-(\d+)\s+[\u2014\-–]\s+(.+)$', block, re.MULTILINE)
        if not match_title: continue
        num_str = match_title.group(1).zfill(3)
        title = match_title.group(2).strip()
        adr_id = f"ADR-{num_str}"
        status_match = re.search(r'^\*\*Estado\*\*:\s*(.+)$', block, re.MULTILINE | re.IGNORECASE)
        declared_status = status_match.group(1).strip() if status_match else "Desconocido"
        
        pattern_trailer = f"ADR: {num_str}"
        pattern_literal = f"ADR-{num_str}"
        linked_commits = []
        for commit in commits_main:
            msg = commit.get("message", "")
            if pattern_trailer in msg or pattern_literal in msg:
                linked_commits.append({"sha": commit.get("sha", "")[:7], "message": msg.split("\n")[0], "url": commit.get("url", "")})

        auto_status = declared_status
        warning = None
        if declared_status in ["Propuesto", "Aceptado"] and len(linked_commits) > 0:
            auto_status = "Implementado (auto-detectado)"
        elif declared_status == "Implementado" and len(linked_commits) == 0:
            warning = "DECLARADO IMPLEMENTADO SIN COMMITS VINCULADOS EN MAIN"

        adrs.append({"id": adr_id, "number": num_str, "title": title, "declared_status": declared_status, "auto_status": auto_status, "evidence_commits": linked_commits, "warning": warning})
    return adrs

def process_docs(commits_main):
    docs = []
    if not PROJECTBRAIN_DIR.exists(): return docs
    now = datetime.now(timezone.utc)
    for file_path in PROJECTBRAIN_DIR.glob("**/*.md"):
        rel_path = str(file_path.relative_to(BASE_DIR))
        last_commit_date = None
        for commit in commits_main:
            if rel_path in commit.get("files", []):
                last_commit_date = commit.get("date")
                break
        is_stale = False
        days_old = None
        if last_commit_date:
            try:
                dt = datetime.fromisoformat(last_commit_date.replace("Z", "+00:00"))
                days_old = (now - dt).days
                if days_old > 14: is_stale = True
            except Exception: pass
        docs.append({"path": rel_path, "title": file_path.stem.replace("_", " ").title(), "last_commit_date": last_commit_date or "[FALTA FECHA_COMMIT]", "days_old": days_old if days_old is not None else "[FALTA DIAS]", "is_stale": is_stale})
    return docs

def fetch_github_data():
    data = {"main_commits": [], "prs": [], "active_branches": [], "branch_commits": {}}
    raw_commits = fetch_github_api("commits?sha=main&per_page=50")
    if raw_commits and isinstance(raw_commits, list):
        for c in raw_commits:
            commit_detail = fetch_github_api(f"commits/{c['sha']}") or c
            files = [f["filename"] for f in commit_detail.get("files", [])]
            data["main_commits"].append({"sha": c["sha"], "message": c["commit"]["message"], "author": c["commit"]["author"]["name"], "date": c["commit"]["author"]["date"], "url": c.get("html_url", ""), "files": files})
    
    raw_prs = fetch_github_api("pulls?state=all&per_page=30")
    if raw_prs and isinstance(raw_prs, list):
        for pr in raw_prs:
            data["prs"].append({"number": pr["number"], "title": pr["title"], "state": pr["state"], "user": pr["user"]["login"], "created_at": pr["created_at"], "merged_at": pr.get("merged_at"), "url": pr["html_url"]})
            
    raw_branches = fetch_github_api("branches?per_page=30")
    if raw_branches and isinstance(raw_branches, list):
        for b in raw_branches:
            b_name = b["name"]
            data["active_branches"].append({"name": b_name, "sha": b["commit"]["sha"]})
            b_commits = fetch_github_api(f"commits?sha={b_name}&per_page=10")
            if b_commits and isinstance(b_commits, list):
                parsed_b_commits = []
                for bc in b_commits:
                    detail = fetch_github_api(f"commits/{bc['sha']}") or bc
                    parsed_b_commits.append({"sha": bc["sha"], "message": bc["commit"]["message"], "files": [f["filename"] for f in detail.get("files", [])]})
                data["branch_commits"][b_name] = parsed_b_commits
    return data

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    schema = load_schema()
    github_data = fetch_github_data()
    sessions, invalid_sessions = process_sessions(schema, github_data)
    adrs = process_adrs(github_data["main_commits"])
    docs = process_docs(github_data["main_commits"])

    with open(OUTPUT_DIR / "sessions.json", "w", encoding="utf-8") as f:
        json.dump({"sessions": sessions, "invalid_sessions": invalid_sessions}, f, indent=2)
    with open(OUTPUT_DIR / "adrs.json", "w", encoding="utf-8") as f:
        json.dump({"adrs": adrs}, f, indent=2)
    with open(OUTPUT_DIR / "git_activity.json", "w", encoding="utf-8") as f:
        json.dump({"main_commits": github_data["main_commits"], "prs": github_data["prs"], "active_branches": github_data["active_branches"]}, f, indent=2)
    with open(OUTPUT_DIR / "docs.json", "w", encoding="utf-8") as f:
        json.dump({"docs": docs}, f, indent=2)

if __name__ == "__main__":
    main()
