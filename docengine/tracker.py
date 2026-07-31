#!/usr/bin/env python3
"""Parser del tracker markdown + lector de verificaciones + historial de corridas.

Codificado por Claude · para el Core-Doc-Engine (ihui Systems) · 2026

Contrato que implementa (tablero congelado, 30-jul-2026):
- El tracker es un markdown commiteado en Git. Cada renglón es un checkbox:
      - [ ] **B-01** (🔴 P0) — descripción _(fuente)_
- `id` inmutable con prefijo que define el tipo: B (BUG), F (FEATURE), DE (MOTOR).
- `alcance` se DERIVA, jamás se teclea:  fecha_intake > linea_base  →  EXPANSION.
- `fecha_intake` la pone Git (primer commit que menciona el ID en el tracker).
  Excepción única de arranque: un renglón puede traer `[intake: AAAA-MM-DD]`
  tecleado a mano SOLO si nació en el commit inicial del tracker. Si el marcador
  aparece en un renglón agregado después, se denuncia como manipulación.
- `prioridad` capturada (P0–P3); si falta → [FALTA CLASIFICAR].
- `[x]` significa "verificado en vivo" según el humano; la evidencia canónica es
  `verificaciones/*.jsonl` — un tachado sin evidencia se denuncia, no se cuenta.

Diseñado para ser reutilizable en cualquier repo (opensource):
- CERO rutas o nombres hardcodeados de un proyecto específico.
- Toda configuración entra por variables de entorno con defaults sensatos.
- Si un dato falta, se marca ruidosamente ([FALTA ...]); nunca se inventa.

Configuración (env):
  DOCENGINE_TRACKER         ruta al tracker .md   (default: <repo>/tracker.md)
  DOCENGINE_LINEA_BASE      fecha ISO de la línea base del contrato (ej. 2026-05-04)
  DOCENGINE_VERIFICACIONES  dir de evidencias .jsonl (default: <repo>/verificaciones)
  DOCENGINE_HISTORIAL       ruta del historial append-only (default: <repo>/historial.jsonl)

Salidas:
  <out_dir>/tracker.json         renglones normalizados + resumen + avisos
  <out_dir>/verificaciones.json  evidencias leídas + errores de formato
  <historial>                    una línea JSON por corrida (append-only, reconstruible)
"""
import json
import os
import re
import subprocess
from datetime import datetime, timezone, date
from pathlib import Path

MOTOR_VERSION = "0.2.0"

TIPO_POR_PREFIJO = {"B": "BUG", "F": "FEATURE", "DE": "MOTOR"}

# - [ ] **B-01** ... | - [x] **F-02** ...
RE_RENGLON = re.compile(r"^\s*-\s*\[( |x|X)\]\s*\*\*([A-Za-z]{1,3}-\d+)\*\*\s*(.*)$")
RE_PRIORIDAD = re.compile(r"\(\s*[^\w\s]*\s*(P[0-3])\s*\)")
RE_INTAKE = re.compile(r"\[intake:\s*(\d{4}-\d{2}-\d{2})\s*\]")
RE_ORIGEN = re.compile(r"\[origen:\s*(F-\d+)\s*\]")


def _git(args, cwd):
    """Corre git y devuelve stdout limpio, o None si falla (el caller decide el aviso)."""
    res = subprocess.run(["git"] + args, cwd=cwd, capture_output=True, text=True)
    return res.stdout.strip() if res.returncode == 0 else None


def _fecha_primer_commit(repo_root, tracker_rel, needle=None):
    """Fecha (date) del commit MÁS ANTIGUO que tocó el tracker.

    Con `needle` (ej. '**B-05**') busca el primer commit que introdujo ese texto
    (git log -S): así Git pone la fecha de intake, no el humano.
    """
    args = ["log", "--reverse", "--format=%aI", "--"]
    if needle is not None:
        args = ["log", "--reverse", "--format=%aI", "-S", needle, "--"]
    out = _git(args + [tracker_rel], repo_root)
    if not out:
        return None
    primera = out.splitlines()[0].strip()
    try:
        return datetime.fromisoformat(primera).date()
    except ValueError:
        return None


def parse_tracker(repo_root, tracker_path, linea_base):
    """Lee el tracker markdown y devuelve (dict | None, avisos). No escribe nada."""
    avisos = []
    tracker_path = Path(tracker_path)
    if not tracker_path.exists():
        return None, [f"[FALTA TRACKER] No existe {tracker_path}. Define DOCENGINE_TRACKER."]

    # Ruta relativa al repo, necesaria para preguntarle a Git por el archivo.
    try:
        tracker_rel = str(tracker_path.resolve().relative_to(Path(repo_root).resolve()))
    except ValueError:
        tracker_rel = None
        avisos.append(f"[TRACKER FUERA DEL REPO] {tracker_path} no vive dentro de "
                      f"{repo_root}: Git no puede derivar fechas de intake.")

    commit_inicial = (_fecha_primer_commit(repo_root, tracker_rel)
                      if tracker_rel else None)
    if tracker_rel and commit_inicial is None:
        avisos.append("[TRACKER SIN HISTORIA] El tracker no está commiteado en Git: "
                      "las fechas de intake sin marcador quedarán [SIN FECHA_INTAKE].")

    renglones = []
    ids_vistos = set()
    for num, linea in enumerate(tracker_path.read_text(encoding="utf-8").splitlines(), 1):
        m = RE_RENGLON.match(linea)
        if not m:
            continue
        tachado = m.group(1).lower() == "x"
        rid = m.group(2).upper()
        resto = m.group(3)

        if rid in ids_vistos:
            avisos.append(f"[ID DUPLICADO] {rid} aparece más de una vez (línea {num}).")
            continue
        ids_vistos.add(rid)

        prefijo = rid.split("-")[0]
        tipo = TIPO_POR_PREFIJO.get(prefijo)
        if tipo is None:
            avisos.append(f"[ID FUERA DE CONTRATO] {rid} (línea {num}): los prefijos "
                          f"válidos son {', '.join(TIPO_POR_PREFIJO)}. Se lista pero "
                          "no cuenta en el universo.")

        m_prio = RE_PRIORIDAD.search(resto)
        prioridad = m_prio.group(1) if m_prio else "[FALTA CLASIFICAR]"

        # --- fecha_intake: Git manda; el marcador manual solo vale en el arranque ---
        m_intake = RE_INTAKE.search(resto)
        fecha_git = (_fecha_primer_commit(repo_root, tracker_rel, needle=f"**{rid}**")
                     if tracker_rel and commit_inicial else None)
        if m_intake:
            fecha_intake = date.fromisoformat(m_intake.group(1))
            if fecha_git and fecha_git != commit_inicial:
                # Git manda: el marcador manual fuera del arranque se ignora
                # y se usa la fecha real del commit que agregó el renglón.
                avisos.append(f"[INTAKE MANUAL SOSPECHOSO] {rid}: trae marcador "
                              f"[intake: {fecha_intake}] pero NO nació en el commit "
                              f"inicial del tracker (nació {fecha_git}). Se usa la "
                              "fecha de Git; el marcador solo vale en el arranque.")
                fecha_intake = fecha_git
        else:
            fecha_intake = fecha_git

        if linea_base is None:
            alcance = "[FALTA LINEA_BASE]"
        elif fecha_intake is None:
            alcance = "[SIN FECHA_INTAKE]"
        else:
            alcance = "EXPANSION" if fecha_intake > linea_base else "BASE"

        m_origen = RE_ORIGEN.search(resto)
        origen = None
        if tipo == "BUG":
            origen = m_origen.group(1) if m_origen else "CORE"
        elif m_origen:
            avisos.append(f"[ORIGEN IGNORADO] {rid}: [origen:] solo aplica a bugs.")

        # Descripción limpia: sin prioridad, sin marcadores, sin fuente final _(...)_.
        descripcion = RE_PRIORIDAD.sub("", resto)
        descripcion = RE_INTAKE.sub("", descripcion)
        descripcion = RE_ORIGEN.sub("", descripcion)
        descripcion = re.sub(r"_\([^)]*\)_\s*$", "", descripcion)
        descripcion = descripcion.replace("**", "").replace("`", "")
        descripcion = descripcion.strip(" —–-·\t")

        renglones.append({
            "id": rid,
            "tipo": tipo or "[FUERA DE CONTRATO]",
            "descripcion": descripcion,
            "prioridad": prioridad,
            "origen": origen,
            "fecha_intake": fecha_intake.isoformat() if fecha_intake else None,
            "alcance": alcance,
            "tachado": tachado,
            "linea": num,
        })

    # El motor exige que el origen F-nn de un bug exista en el tracker.
    for r in renglones:
        if r["origen"] and r["origen"] != "CORE" and r["origen"] not in ids_vistos:
            avisos.append(f"[ORIGEN INEXISTENTE] {r['id']} declara origen "
                          f"{r['origen']} y ese renglón no existe en el tracker.")

    return {"renglones": renglones,
            "commit_inicial": commit_inicial.isoformat() if commit_inicial else None}, avisos


def leer_verificaciones(verif_dir):
    """Lee verificaciones/*.jsonl (append-only). Devuelve (evidencias, avisos)."""
    avisos, evidencias = [], []
    verif_dir = Path(verif_dir)
    if not verif_dir.exists():
        avisos.append(f"[SIN VERIFICACIONES] No existe {verif_dir}: "
                      "cobertura verificada = 0 hasta que exista la primera evidencia.")
        return evidencias, avisos

    campos_obligatorios = {"id", "verifico", "fecha", "resultado"}
    for archivo in sorted(verif_dir.glob("*.jsonl")):
        for n, linea in enumerate(archivo.read_text(encoding="utf-8").splitlines(), 1):
            if not linea.strip():
                continue
            try:
                ev = json.loads(linea)
            except json.JSONDecodeError:
                avisos.append(f"[EVIDENCIA ILEGIBLE] {archivo.name}:{n}")
                continue
            faltan = campos_obligatorios - set(ev)
            if faltan:
                avisos.append(f"[EVIDENCIA INCOMPLETA] {archivo.name}:{n} "
                              f"faltan: {', '.join(sorted(faltan))}")
                continue
            ev["_archivo"] = archivo.name
            evidencias.append(ev)
    return evidencias, avisos


def _resumen(renglones, evidencias):
    """Todos los números del tablero salen de aquí — derivados, jamás tecleados."""
    ids_con_evidencia_ok = {e["id"] for e in evidencias if e.get("resultado") == "ok"}
    for r in renglones:
        r["cubierto"] = r["id"] in ids_con_evidencia_ok
    universo = [r for r in renglones if r["tipo"] in TIPO_POR_PREFIJO.values()]
    cubiertos = [r for r in universo if r["cubierto"]]
    bugs = [r for r in universo if r["tipo"] == "BUG"]
    bugs_abiertos = [r for r in bugs if not r["cubierto"]]
    return {
        "universo": len(universo),
        "base": len([r for r in universo if r["alcance"] == "BASE"]),
        "expansion": len([r for r in universo if r["alcance"] == "EXPANSION"]),
        "sin_alcance_determinable": len([r for r in universo
                                         if r["alcance"] not in ("BASE", "EXPANSION")]),
        "bugs_abiertos": len(bugs_abiertos),
        "bugs_core": len([r for r in bugs_abiertos if r["origen"] == "CORE"]),
        "bugs_expansion": len([r for r in bugs_abiertos if r["alcance"] == "EXPANSION"]),
        "verificados_en_vivo": len(cubiertos),
        "cobertura_pct": round(100 * len(cubiertos) / len(universo), 1) if universo else 0.0,
    }


def _avisos_cruce(renglones, evidencias):
    """Cruza el tachado humano contra la evidencia canónica. La evidencia manda."""
    avisos = []
    ids_ok = {e["id"] for e in evidencias if e.get("resultado") == "ok"}
    ids_tracker = {r["id"] for r in renglones}
    for r in renglones:
        if r["tachado"] and r["id"] not in ids_ok:
            avisos.append(f"[TACHADO SIN EVIDENCIA] {r['id']} está [x] en el tracker "
                          "pero no tiene resultado ok en verificaciones/. No cuenta.")
    for e in evidencias:
        if e["id"] not in ids_tracker:
            avisos.append(f"[EVIDENCIA HUÉRFANA] {e['id']} ({e['_archivo']}) "
                          "no existe en el tracker.")
    return avisos


def _commit_actual(repo_root):
    return _git(["rev-parse", "--short", "HEAD"], repo_root) or "[SIN GIT]"


def run(repo_root, out_dir):
    """Punto de entrada. Escribe tracker.json, verificaciones.json y appendea historial."""
    repo_root = Path(repo_root)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    avisos_globales = []
    linea_base = None
    linea_base_env = os.environ.get("DOCENGINE_LINEA_BASE")
    if linea_base_env:
        try:
            linea_base = date.fromisoformat(linea_base_env)
        except ValueError:
            avisos_globales.append(
                f"[LINEA_BASE ILEGIBLE] {linea_base_env!r}: usa formato AAAA-MM-DD. "
                "Todo el alcance saldrá como [FALTA LINEA_BASE].")
    else:
        avisos_globales.append(
            "[FALTA LINEA_BASE] Define DOCENGINE_LINEA_BASE (AAAA-MM-DD): "
            "sin ella BASE/EXPANSION no es determinable.")

    tracker_path = os.environ.get("DOCENGINE_TRACKER", repo_root / "tracker.md")
    verif_dir = os.environ.get("DOCENGINE_VERIFICACIONES", repo_root / "verificaciones")
    historial_path = Path(os.environ.get("DOCENGINE_HISTORIAL",
                                         repo_root / "historial.jsonl"))

    tracker, avisos_t = parse_tracker(repo_root, tracker_path, linea_base)
    evidencias, avisos_v = leer_verificaciones(verif_dir)
    avisos = avisos_globales + avisos_t + avisos_v
    if tracker is not None:
        avisos += _avisos_cruce(tracker["renglones"], evidencias)

    for a in avisos:
        print(a)

    if tracker is None:
        with open(out_dir / "tracker.json", "w", encoding="utf-8") as f:
            json.dump({"error": avisos_t, "renglones": [], "resumen": None},
                      f, indent=2, ensure_ascii=False)
        return False

    resumen = _resumen(tracker["renglones"], evidencias)

    with open(out_dir / "tracker.json", "w", encoding="utf-8") as f:
        json.dump({
            "generado": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ"),
            "motor": MOTOR_VERSION,
            "commit_datos": _commit_actual(repo_root),
            "linea_base": linea_base.isoformat() if linea_base else None,
            "commit_inicial_tracker": tracker["commit_inicial"],
            "resumen": resumen,
            "avisos": avisos,
            "renglones": tracker["renglones"],
        }, f, indent=2, ensure_ascii=False)

    with open(out_dir / "verificaciones.json", "w", encoding="utf-8") as f:
        json.dump({"evidencias": evidencias, "avisos": avisos_v},
                  f, indent=2, ensure_ascii=False)

    # historial.jsonl: caché de derivados, append-only, reconstruible desde Git.
    linea = {
        "build": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M"),
        "motor": MOTOR_VERSION,
        "commit": _commit_actual(repo_root),
        "universo": resumen["universo"],
        "base": resumen["base"],
        "expansion": resumen["expansion"],
        "bugs_core": resumen["bugs_core"],
        "bugs_exp": resumen["bugs_expansion"],
        "cubierto": resumen["verificados_en_vivo"],
    }
    with open(historial_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(linea, ensure_ascii=False) + "\n")

    # Copia derivada del historial para la vista Versiones del tablero
    # (el .jsonl de la raíz sigue siendo el registro canónico).
    try:
        lineas = []
        for n, raw in enumerate(historial_path.read_text(encoding="utf-8").splitlines(), 1):
            if not raw.strip():
                continue
            try:
                lineas.append(json.loads(raw))
            except json.JSONDecodeError:
                print(f"[HISTORIAL ILEGIBLE] línea {n} de {historial_path.name}: se omite.")
        with open(out_dir / "historial.json", "w", encoding="utf-8") as f:
            json.dump(lineas, f, indent=2, ensure_ascii=False)
    except OSError as err:
        print(f"[HISTORIAL NO PUBLICADO] {err}")

    print(f"TRACKER: universo={resumen['universo']} base={resumen['base']} "
          f"expansion={resumen['expansion']} bugs={resumen['bugs_abiertos']} "
          f"cubierto={resumen['verificados_en_vivo']} ({resumen['cobertura_pct']}%)")
    return True


if __name__ == "__main__":
    raiz = Path(__file__).resolve().parent.parent
    run(raiz, raiz / "docengine" / "dashboard" / "public" / "data")
