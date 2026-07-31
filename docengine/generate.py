#!/usr/bin/env python3
import os
import json
import re
import subprocess
from datetime import datetime
from pathlib import Path
import jsonschema
import markdown

ROOT = Path(__file__).resolve().parent.parent
SESSIONS_DIR = ROOT / ".sessions"
SCHEMA_PATH = ROOT / "docengine" / "schema_session_v1.json"
OUT_DIR = ROOT / "docengine" / "dashboard" / "public" / "data"
PROJECTBRAIN_DIR = Path(os.environ.get("DOCENGINE_PROJECTBRAIN", str(ROOT / "PROJECTBRAIN")))
# Separadores ASCII para trocear la salida de git log: no aparecen en mensajes de commit.
RECORD_SEP = "\x1e"
FIELD_SEP = "\x1f"
# Un trailer (ADR: NNN) vive en el body, no en el subject: por eso se pide %B (mensaje completo).
GIT_LOG_FORMAT = f"--pretty=format:%H{FIELD_SEP}%s{FIELD_SEP}%B{RECORD_SEP}"
ADRS_MASTER_PATH = PROJECTBRAIN_DIR / os.environ.get("DOCENGINE_ADRS_FILE", "02_maestrodecisionesarquitectonicas.md")

def get_git_commits_in_range(branch, started_at, ended_at):
    cmd = ["git", "log", branch, "--name-only", "--pretty=format:COMMIT:%H|%an|%ae|%at|%s"]
    if branch != "main":
        res_diff = subprocess.run(["git", "rev-parse", "--verify", "origin/main"], cwd=ROOT, capture_output=True, text=True)
        if res_diff.returncode == 0:
            cmd = ["git", "log", f"origin/main..{branch}", "--name-only", "--pretty=format:COMMIT:%H|%an|%ae|%at|%s"]
        else:
            print("[FALTA origin/main] No se pudo verificar origin/main localmente para acotar el rango.")
            return [], set(), "NO_VERIFICABLE"

    res = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"[FALTA origin/main] Error ejecutando git log para la rama {branch}.")
        return [], set(), "NO_VERIFICABLE"

    try:
        start_dt = datetime.fromisoformat(started_at.replace("Z", "+00:00"))
        end_dt = datetime.fromisoformat(ended_at.replace("Z", "+00:00"))
    except Exception:
        return [], set(), "VERIFICADO"

    commits_data = []
    touched_files = set()
    current_commit = None

    for line in res.stdout.splitlines():
        if line.startswith("COMMIT:"):
            parts = line.replace("COMMIT:", "").split("|")
            if len(parts) == 5:
                commit_hash, author, email, timestamp, subject = parts
                commit_dt = datetime.fromtimestamp(int(timestamp), tz=start_dt.tzinfo)
                if start_dt <= commit_dt <= end_dt:
                    current_commit = {
                        "hash": commit_hash,
                        "author": author,
                        "email": email,
                        "subject": subject
                    }
                    commits_data.append(current_commit)
                else:
                    current_commit = None
        elif current_commit and line.strip():
            touched_files.add(line.strip())

    return commits_data, touched_files, "VERIFICADO"

def evaluate_status_priority(statuses):
    if "DISCREPANCIA" in statuses:
        return "DISCREPANCIA"
    if "NO_ENCONTRADO" in statuses:
        return "NO_ENCONTRADO"
    if "NO_VERIFICABLE" in statuses:
        return "NO_VERIFICABLE"
    return "VERIFICADO"

def parse_git_log_records(stdout):
    """Trocea la salida de git log con GIT_LOG_FORMAT.

    El body puede contener saltos de linea, asi que se parte por RECORD_SEP y no por lineas.
    Devuelve dicts con hash, subject y message (mensaje completo: subject + body).
    """
    commits = []
    for record in stdout.split(RECORD_SEP):
        record = record.strip("\n")
        if not record.strip():
            continue
        parts = record.split(FIELD_SEP)
        if len(parts) != 3:
            print(f"[FALTA MENSAJE COMMIT] Registro ilegible, se omite: {record[:60]!r}")
            continue
        commit_hash, subject, message = parts
        commits.append({"hash": commit_hash, "subject": subject, "message": message})
    return commits

def parse_adrs_master():
    adrs = []
    if not ADRS_MASTER_PATH.exists():
        return adrs
    
    content = ADRS_MASTER_PATH.read_text(encoding="utf-8")
    sections = re.split(r'(?m)^##\s+', content)
    
    for sec in sections:
        if not sec.strip():
            continue
        lines = sec.splitlines()
        header = lines[0]
        match = re.search(r'(ADR-\d+)\s*[—–-]\s*(.+)', header)
        if match:
            adr_id = match.group(1)
            title = match.group(2).strip()
            body = "\n".join(lines[1:])
            
            status_match = re.search(r'(?i)estado:\s*([^\n]+)', body)
            declared_status = status_match.group(1).strip() if status_match else "DESCONOCIDO"
            
            adrs.append({
                "id": adr_id,
                "title": title,
                "declared_status": declared_status,
                "body": body
            })
    return adrs

if not PROJECTBRAIN_DIR.exists():
    print(f"[FALTA PROJECTBRAIN] No existe {PROJECTBRAIN_DIR}. Define DOCENGINE_PROJECTBRAIN para apuntar a la carpeta real.")

def safe_rel(path):
    """Ruta relativa al repo; si el archivo vive fuera, devuelve la ruta absoluta."""
    try:
        return str(Path(path).relative_to(ROOT))
    except ValueError:
        return str(path)

def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    
    if not SCHEMA_PATH.exists():
        print(f"[ERROR] No se encontró el esquema en {SCHEMA_PATH}")
        exit(1)
        
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema = json.load(f)

    sessions = []
    invalid_count = 0
    c_verificado = 0
    c_no_encontrado = 0
    c_discrepancia = 0
    c_no_verificable = 0
    
    git_all_log = subprocess.run(
        ["git", "log", "--all", GIT_LOG_FORMAT],
        cwd=ROOT, capture_output=True, text=True,
    )
    if git_all_log.returncode != 0:
        print("[FALTA HISTORIAL GIT] git log --all falló: ningún ADR podrá respaldarse con commits.")
        all_git_commits = []
    else:
        all_git_commits = parse_git_log_records(git_all_log.stdout)

    if SESSIONS_DIR.exists():
        for session_file in sorted(SESSIONS_DIR.glob("*.json")):
            try:
                with open(session_file, "r", encoding="utf-8") as sf:
                    data = json.load(sf)
                
                data.pop("verification", None)
                jsonschema.validate(instance=data, schema=schema)
                
                branch = data.get("branch", "main")
                started_at = data.get("started_at")
                ended_at = data.get("ended_at")
                claims = data.get("claims", {})
                claimed_files = set(claims.get("files_modified", []))
                claimed_adrs = claims.get("adrs_touched", [])
                claimed_prs = claims.get("prs", [])

                commits_data, scope_touched_files, range_status = get_git_commits_in_range(branch, started_at, ended_at)

                file_details = []
                file_statuses = []

                if range_status == "NO_VERIFICABLE":
                    for f in claimed_files:
                        file_details.append({"file": f, "status": "NO_VERIFICABLE"})
                        file_statuses.append("NO_VERIFICABLE")
                elif not commits_data and not scope_touched_files:
                    for f in claimed_files:
                        file_details.append({"file": f, "status": "NO_ENCONTRADO"})
                        file_statuses.append("NO_ENCONTRADO")
                else:
                    session_emails = {c["email"] for c in commits_data}
                    
                    for f in claimed_files:
                        touched = False
                        for c in commits_data:
                            c_files = subprocess.run(["git", "show", "--name-only", "--pretty=", c["hash"]], cwd=ROOT, capture_output=True, text=True).stdout.splitlines()
                            if f in [cf.strip() for cf in c_files if cf.strip()]:
                                touched = True
                                break
                        if touched:
                            file_details.append({"file": f, "status": "VERIFICADO"})
                            file_statuses.append("VERIFICADO")
                        else:
                            file_details.append({"file": f, "status": "NO_ENCONTRADO"})
                            file_statuses.append("NO_ENCONTRADO")

                    author_scoped_touched = set()
                    for c in commits_data:
                        c_files = subprocess.run(["git", "show", "--name-only", "--pretty=", c["hash"]], cwd=ROOT, capture_output=True, text=True).stdout.splitlines()
                        for cf in c_files:
                            if cf.strip():
                                author_scoped_touched.add(cf.strip())

                    undeclared_files = author_scoped_touched - claimed_files
                    if len(session_emails) == 1:
                        for uf in undeclared_files:
                            file_details.append({"file": uf, "status": "DISCREPANCIA"})
                            file_statuses.append("DISCREPANCIA")
                    else:
                        for uf in undeclared_files:
                            file_details.append({"file": uf, "status": "NO_VERIFICABLE"})
                            file_statuses.append("NO_VERIFICABLE")

                adr_details = []
                adr_statuses = []

                for adr_str in claimed_adrs:
                    adr_num = re.search(r'\d+', adr_str)
                    if not adr_num:
                        adr_details.append({"adr": adr_str, "status": "NO_ENCONTRADO"})
                        adr_statuses.append("NO_ENCONTRADO")
                        continue
                    
                    num_clean = adr_num.group(0).zfill(3)
                    trailer_pattern = f"ADR: {num_clean}"
                    literal_pattern = f"ADR-{num_clean}"

                    found_hashes = []
                    for gc in all_git_commits:
                        if trailer_pattern in gc["message"] or literal_pattern in gc["message"]:
                            found_hashes.append(gc["hash"])

                    if found_hashes:
                        adr_details.append({"adr": adr_str, "status": "VERIFICADO"})
                        adr_statuses.append("VERIFICADO")
                    else:
                        adr_details.append({"adr": adr_str, "status": "NO_ENCONTRADO"})
                        adr_statuses.append("NO_ENCONTRADO")

                pr_details = []
                pr_statuses = []
                for pr in claimed_prs:
                    pr_number = pr.get("number")
                    pr_details.append({"number": pr_number, "status": "NO_VERIFICABLE"})
                    pr_statuses.append("NO_VERIFICABLE")

                all_statuses = file_statuses + adr_statuses + pr_statuses
                aggregate_status = evaluate_status_priority(all_statuses) if all_statuses else "NO_ENCONTRADO"

                if aggregate_status == "VERIFICADO":
                    c_verificado += 1
                elif aggregate_status == "NO_ENCONTRADO":
                    c_no_encontrado += 1
                elif aggregate_status == "DISCREPANCIA":
                    c_discrepancia += 1
                elif aggregate_status == "NO_VERIFICABLE":
                    c_no_verificable += 1

                data["verification"] = {
                    "status": aggregate_status,
                    "checked_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "details": {
                        "files": file_details,
                        "adrs": adr_details,
                        "prs": pr_details
                    }
                }

                sessions.append(data)
            except Exception as err:
                invalid_count += 1
                print(f"[FALTA VALIDACIÓN ESQUEMA] Inválido: {session_file.name} -> {err}")

    with open(OUT_DIR / "sessions.json", "w", encoding="utf-8") as f:
        json.dump(sessions, f, indent=2, ensure_ascii=False)

    adrs_master_list = parse_adrs_master()
    adrs_output = []
    for item in adrs_master_list:
        adr_id = item["id"]
        num_clean = re.search(r'\d+', adr_id).group(0).zfill(3)
        trailer_pattern = f"ADR: {num_clean}"
        literal_pattern = f"ADR-{num_clean}"

        evidence_hashes = []
        for gc in all_git_commits:
            if trailer_pattern in gc["message"] or literal_pattern in gc["message"]:
                evidence_hashes.append(gc["hash"])

        auto_status = "VERIFICADO" if evidence_hashes else "NO_ENCONTRADO"

        adrs_output.append({
            "numero": adr_id,
            "titulo": item["title"],
            "estado_declarado": item["declared_status"],
            "estado_autodetectado": auto_status,
            "commits_vinculados": evidence_hashes
        })

    with open(OUT_DIR / "adrs.json", "w", encoding="utf-8") as f:
        json.dump(adrs_output, f, indent=2, ensure_ascii=False)

    docs_output = []
    if PROJECTBRAIN_DIR.exists():
        for md_file in sorted(PROJECTBRAIN_DIR.glob("**/*.md")):
            try:
                content = md_file.read_text(encoding="utf-8")
                html_content = markdown.markdown(content, extensions=['fenced_code', 'tables'])
                docs_output.append({
                    "path": safe_rel(md_file),
                    "title": md_file.stem,
                    "html": html_content
                })
            except Exception as e:
                print(f"[WARN] No se pudo procesar {md_file.name}: {e}")

    with open(OUT_DIR / "docs.json", "w", encoding="utf-8") as f:
        json.dump(docs_output, f, indent=2, ensure_ascii=False)

    git_log = subprocess.run(["git", "log", "-n", "10", "--pretty=format:%h|%an|%s|%ad"], cwd=ROOT, capture_output=True, text=True)
    git_activity = []
    if git_log.returncode == 0:
        for line in git_log.stdout.splitlines():
            parts = line.split("|")
            if len(parts) == 4:
                git_activity.append({"hash": parts[0], "author": parts[1], "subject": parts[2], "date": parts[3]})

    with open(OUT_DIR / "git_activity.json", "w", encoding="utf-8") as f:
        json.dump(git_activity, f, indent=2, ensure_ascii=False)

    # Tracker + verificaciones + historial (módulo aparte, configurable por env).
    # Si falla, se avisa ruidosamente pero NO tumba el resto de las salidas.
    try:
        import tracker as tracker_mod
        tracker_mod.run(ROOT, OUT_DIR)
    except Exception as err:
        print(f"[FALLA TRACKER] El módulo tracker no corrió: {err}")

    print(f"VERIFICADO: {c_verificado} | NO_ENCONTRADO: {c_no_encontrado} | DISCREPANCIA: {c_discrepancia} | NO_VERIFICABLE: {c_no_verificable} | Invalidos Esquema: {invalid_count}")

if __name__ == "__main__":
    main()
