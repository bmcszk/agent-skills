#!/usr/bin/env python3
"""Coverage audit: prove a split lost nothing.

Run BEFORE removing the source of a split. Compares whitespace-normalized
content lines of source note(s) against the corpus of destination notes:
every non-trivial source line must appear exactly in the corpus, and every
source must map to a destination via an explicit mapping file (JSON:
{"<source-relpath>": ["<dest-relpath>", ...]}).

Usage: python3 coverage_audit.py <vault-root> <mapping.json>
Exit 0 = full coverage; exit 1 = lost lines / unmapped / double-mapped.
"""
import json
import os
import re
import subprocess
import sys
import unicodedata

SKIP_DIRS = ('.git', '.obsidian', '.smart-env', '.trash', '.beans')
MIN_LINE = 8  # ignore shorter lines (headers, URLs fragments, whitespace)


def norm(s: str) -> str:
    return re.sub(r'\s+', ' ', unicodedata.normalize('NFKC', s)).strip().lower()


def corpus_lines(vault: str) -> set:
    lines = set()
    for root, dirs, files in os.walk(vault):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith('_')]
        for f in files:
            if not f.endswith('.md'):
                continue
            p = os.path.join(root, f)
            with open(p, encoding='utf-8', errors='replace') as fh:
                for ln in fh:
                    n = norm(ln)
                    if len(n) >= MIN_LINE:
                        lines.add(n)
    return lines


def source_lines(vault: str, relpath: str):
    """Read a mapping source. On disk if present; after a move, from git
    HEAD's pre-move version (the documented post-move mode)."""
    sp = os.path.join(vault, relpath)
    if os.path.exists(sp):
        with open(sp, encoding='utf-8', errors='replace') as fh:
            return fh.read()
    if os.path.isdir(os.path.join(vault, '.git')):
        blob = subprocess.run(['git', '-C', vault, 'show', f'HEAD:{relpath}'],
                              capture_output=True, text=True)
        if blob.returncode == 0:
            return blob.stdout
        problems_src.append(f'{relpath}: source missing (not on disk, not in HEAD)')
    else:
        problems_src.append(f'{relpath}: source missing (no .git for post-move lookup)')
    return None


problems_src: list = []


def main(vault: str, mapping_path: str) -> int:
    mapping = json.load(open(mapping_path, encoding='utf-8'))
    corpus = corpus_lines(vault)
    problems = list(problems_src)
    for src, dests in mapping.items():
        if not dests:
            problems.append(f'{src}: mapped to nothing')
            continue
        if len(dests) > 1 and len(set(dests)) != len(dests):
            problems.append(f'{src}: duplicate destinations {dests}')
        text = source_lines(vault, src)
        if text is not None:
            for ln in text.splitlines():
                n = norm(ln)
                if len(n) < MIN_LINE:
                    continue
                if n not in corpus:
                    problems.append(f'{src}: LOST LINE: {ln.strip()[:90]}')
        for d in dests:
            if not os.path.exists(os.path.join(vault, d)):
                problems.append(f'{src}: destination missing: {d}')
    if problems:
        print(f'coverage_audit: {len(problems)} problem(s)')
        for p in problems:
            print(' ', p)
        return 1
    print(f'coverage_audit: OK ({len(mapping)} sources fully covered)')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1], sys.argv[2]))
