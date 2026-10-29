#!/usr/bin/env python3
"""skill-craft lint for agent-skills: mechanical gates per SKILL.md."""
import sys, re, pathlib

def norm(t):
    return re.sub(r'\s*—\s*', ' - ', t)

root = pathlib.Path(sys.argv[1])
issues = {}
for d in sorted(root.iterdir()):
    f = d / "SKILL.md"
    if not d.is_dir() or not f.exists():
        continue
    t = f.read_text()
    out = []
    # frontmatter + description routing
    m = re.match(r"^---\n(.*?)\n---\n", t, re.S)
    if not m:
        out.append("no frontmatter")
    else:
        fm = m.group(1)
        dm = re.search(r"description:\s*>?-?\s*(.*?)(?=\n\w+:|\Z)", fm, re.S)
        desc = re.sub(r"\s+", " ", dm.group(1)) if dm else ""
        if "use when" not in desc.lower() and "use for" not in desc.lower() and "load when" not in desc.lower() and "triggers" not in desc.lower():
            out.append("description lacks trigger (routing)")
        if len(desc) > 600:
            out.append(f"description very long ({len(desc)} ch)")
        if re.search(r"\bI \w+", desc) or "This skill" in desc:
            out.append("description first-person / 'This skill' (want third person)")
    body = t[m.end():] if m else t
    lines = body.splitlines()
    if len(lines) > 500:
        out.append(f"body {len(lines)} lines > 500")
    if "—" in body:
        out.append(f"em dash x{body.count('—')}")
    filler_body = "\n".join(l for l in body.splitlines() if "AI filler" not in l)
    for w in ["crucial", "delve", "additionally,", "comprehensive", "seamless", "leverage", "robust"]:
        n = len(re.findall(w, filler_body, re.I))
        if n: out.append(f"AI filler '{w}' x{n}")
    fp = re.findall(r"^\s*I (?:am|will|'m)\b.*$", body, re.M)
    if fp: out.append(f"first-person narrative x{len(fp)}")
    ids = re.findall(r"\b[a-zA-Z][a-zA-Z0-9]*-[a-z]{2,8}-[a-z0-9]{4}\b|\b(2026|2025)-\d{2}-\d{2}\b|PR #\d+", body)
    if ids: out.append(f"dates/ids/incident refs: {sorted(set(i for i in ids if i))[:4]}")
    # dangling references (quoted examples like "read references/x.md" excluded)
    body_unquoted = re.sub(r'"[^"\n]*"', '', body)
    for ref in re.findall(r"references/([A-Za-z0-9_./-]+\.md)", body_unquoted):
        if not (d / "references" / ref).exists():
            out.append(f"dangling reference references/{ref}")
    # scripts named must exist
    for sc in re.findall(r"scripts/([A-Za-z0-9_./-]+\.(?:py|sh|js))", body):
        if not (d / "scripts" / sc).exists():
            out.append(f"dangling script scripts/{sc}")
    # flags info
    flags = sorted(set(re.findall(r"--[a-z][a-z-]+", body)))
    if flags: out.append("flags used (verify argparse): " + ", ".join(flags))
    if out:
        issues[d.name] = out
for name in sorted(issues):
    print(f"== {name}")
    for i in issues[name]: print(f"   - {i}")
print(f"\n{len(issues)} skills with findings")
