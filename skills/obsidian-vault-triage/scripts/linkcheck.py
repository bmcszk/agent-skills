import os, re, json, unicodedata
V = os.environ.get('VAULT') or os.environ.get('OBSIDIAN_VAULT') or '.'
assert os.path.isdir(V), f"vault dir not found: {V} (set VAULT=<vault path>)"
SKIP = ('.git', '.obsidian', '.smart-env', '.trash', '.beans', '_triage_rework')

md_names = set()
all_paths = set()   # vault-relative posix paths
for root, dirs, fs in os.walk(V):
    dirs[:] = [d for d in dirs if d not in SKIP]
    for f in fs:
        rel = os.path.relpath(os.path.join(root, f), V).replace('\\', '/')
        all_paths.add(rel)
        if f.endswith('.md'):
            md_names.add(f[:-3])

def norm(s):
    return unicodedata.normalize('NFKC', s.lower().replace('\u2013', '-').replace('\u2014', '-'))
md_n = {norm(n) for n in md_names}

def exists_as_file(p, note_rel):
    """resolve a path-ish wikilink/markdown target: try vault-root-relative and note-dir-relative."""
    cand = [p, os.path.normpath(os.path.join(os.path.dirname(note_rel), p))]
    for c in cand:
        c = c.replace('\\', '/')
        if c in all_paths: return True
        if c + '.md' in all_paths: return True
    return False

bad = []
for root, dirs, fs in os.walk(V):
    dirs[:] = [d for d in dirs if d not in SKIP]
    for f in fs:
        if not f.endswith('.md'): continue
        rel = os.path.relpath(os.path.join(root, f), V).replace('\\', '/')
        text = open(os.path.join(root, f), encoding='utf-8', errors='replace').read()
        # code-span strip: remove fenced blocks and inline backticks to avoid example false positives
        stripped = re.sub(r'```.*?```', '', text, flags=re.S)
        stripped = re.sub(r'`[^`\n]*`', '', stripped)
        # wikilinks
        for m in re.finditer(r'!?\[\[([^\]|#\n]+)', stripped):
            tgt = m.group(1).strip()
            if '/' in tgt or re.search(r'\.(png|jpg|jpeg|gif|webp|pdf|3gp|dat|bmp)$', tgt, re.I):
                if not exists_as_file(tgt, rel): bad.append((rel, 'wiki-path', tgt))
            else:
                base = tgt.split('#')[0]
                if norm(base) not in md_n: bad.append((rel, 'wiki-md', tgt))
        # markdown links (non-http)
        for m in re.finditer(r'\]\(([^)\s]+)\)', stripped):
            t = m.group(1)
            if t.startswith(('http', 'mailto:', 'tel:', '#', 'file://')): continue
            if not exists_as_file(t, rel): bad.append((rel, 'md-link', t))

from collections import Counter
print('total broken:', len(bad))
c = Counter(b[1] for b in bad)
print(c)
for b in bad: print(b[0], '|', b[1], '|', b[2][:100])
