#!/usr/bin/env python3
"""Style gate for SKILL.md files. Structural checks (spec, fences, links,
budgets, adapters) are owned by skillscheck: uvx skillscheck <dir>.
This shim covers only what an external linter cannot know: the local
prose style law and project-content leakage."""
import sys, re
from pathlib import Path

def lint(d: Path):
    out = []
    p = d / "SKILL.md"
    t = p.read_text() if p.exists() else ""
    if not t:
        return ["SKILL.md missing or empty"]
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", t, re.S)
    if not m:
        return ["no frontmatter"]
    fm, body = m.groups()
    fm_lines = fm.splitlines()
    desc = None
    for i, l in enumerate(fm_lines):
        m2 = re.match(r"^description:\s*(.*)$", l)
        if m2:
            rest = m2.group(1)
            if rest in (">", ">-", "|", "|-"):
                cont = []
                for l2 in fm_lines[i+1:]:
                    if not l2.startswith(" ") and l2.strip():
                        break
                    cont.append(l2.strip())
                desc = " ".join(cont)
            else:
                desc = rest
            break
    if desc is None:
        out.append("no description")
    else:
        desc = desc.strip().strip('"')
        if not re.search(r"\b(when|use|for)\b", desc, re.I):
            out.append("description lacks trigger (routing)")
        if re.search(r"\bI\b|\bmy\b|this skill", desc, re.I):
            out.append("description first-person / 'This skill' (want third person)")
    if len(body.splitlines()) > 500:
        out.append(f"body {len(body.splitlines())} lines > 500")
    if body.count("—"):
        out.append(f"em dash x{body.count('—')}")
    filler_body = "\n".join(l for l in body.splitlines() if "AI filler" not in l)
    for w in ["crucial", "delve", "additionally,", "comprehensive", "seamless", "leverage", "robust"]:
        n = len(re.findall(w, filler_body, re.I))
        if n: out.append(f"AI filler '{w}' x{n}")
    fp = re.findall(r"^\s*I (?:am|will|'m)\b.*$", body, re.M)
    if fp: out.append(f"first-person narrative x{len(fp)}")
    ids = [m.group(0) for m in re.finditer(r"\b[a-z]{2,12}-[a-z]{2,12}-[a-z0-9]*[0-9][a-z0-9]{0,3}\b|\b(?:2026|2025)-\d{2}-\d{2}\b|PR #\d+", body)]
    if ids: out.append(f"dates/ids/incident refs: {sorted(set(ids))[:4]}")
    return out

def main():
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
    dirs = sorted(d for d in root.rglob("SKILL.md") if "[SKILL_PRUNED]" not in d.read_text()[:2000])
    bad = 0
    for f in dirs:
        finds = lint(f.parent)
        if finds:
            bad += 1
            print(f"== {f.parent.relative_to(root)}")
            for x in finds: print(f"   - {x}")
    print(f"\n{bad} skills with style findings")
    sys.exit(1 if bad else 0)

if __name__ == "__main__":
    main()
