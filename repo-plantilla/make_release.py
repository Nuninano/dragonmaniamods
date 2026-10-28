#!/usr/bin/env python3
"""Genera mods/<id>.zip y updates.json a partir de las carpetas de mods_src/.
Uso (desde la raiz del repo):   python3 make_release.py
- Cada carpeta mods_src/<id>/ debe tener mod.json con "id" igual al nombre de la carpeta.
- La version de actualizacion (entero) sube sola cuando cambia el contenido del mod.
- Para eliminar un mod ya instalado en los telefonos, apunta su id en remove.txt (una linea por id).
"""
import hashlib, json, os, sys, zipfile

SRC, OUT = "mods_src", "mods"

def build_zip(folder, dest):
    files = []
    for root, _, names in os.walk(folder):
        for n in names:
            full = os.path.join(root, n)
            files.append((os.path.relpath(full, folder).replace(os.sep, "/"), full))
    files.sort()
    with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as z:
        for rel, full in files:   # orden y fecha fijos => el hash solo cambia si cambia el contenido
            info = zipfile.ZipInfo(rel, (2020, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, open(full, "rb").read())
    return [rel for rel, _ in files]

def main():
    os.makedirs(OUT, exist_ok=True)
    prev = {}
    if os.path.exists("updates.json"):
        prev = {m["id"]: m for m in json.load(open("updates.json", encoding="utf-8")).get("mods", [])}
    mods, needs_sig = [], False
    for mid in sorted(os.listdir(SRC)):
        folder = os.path.join(SRC, mid)
        mj = os.path.join(folder, "mod.json")
        if not os.path.isfile(mj):
            continue
        meta = json.load(open(mj, encoding="utf-8"))
        if meta.get("id") != mid:
            sys.exit(f"ERROR: mods_src/{mid}/mod.json tiene id={meta.get('id')!r}; debe ser {mid!r}")
        dest = os.path.join(OUT, mid + ".zip")
        names = build_zip(folder, dest)
        sha = hashlib.sha256(open(dest, "rb").read()).hexdigest()
        code = bool(meta.get("entrypoint")) or any(n.lower().endswith((".dex", ".jar", ".apk", ".so")) for n in names)
        old = prev.get(mid)
        version = 1 if not old else (old["version"] if old["sha256"] == sha else old["version"] + 1)
        mods.append({"id": mid, "version": version, "url": f"{OUT}/{mid}.zip", "sha256": sha, "code": code})
        needs_sig |= code
        print(f"  {mid}: v{version} {'(CON CODIGO)' if code else ''} sha256={sha[:12]}...")
    remove = []
    if os.path.exists("remove.txt"):
        remove = [l.strip() for l in open("remove.txt", encoding="utf-8") if l.strip()]
    manifest = {"format": 1, "mods": mods}
    if remove:
        manifest["remove"] = remove
    json.dump(manifest, open("updates.json", "w", encoding="utf-8"), indent=2)
    print("updates.json escrito.")
    if needs_sig:
        print("AVISO: hay mods con CODIGO. Firma el manifiesto:  java SignTool.java sign updates.json  (y sube updates.json.sig)")

main()
