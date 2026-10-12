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


def main(vault: str, mapping_path: str) -> int:
    mapping = json.load(open(mapping_path, encoding='utf-8'))
    corpus = corpus_lines(vault)
    problems = []
    for src, dests in mapping.items():
        if not dests:
            problems.append(f'{src}: mapped to nothing')
            continue
        if len(dests) > 1 and len(set(dests)) != len(dests):
            problems.append(f'{src}: duplicate destinations {dests}')
        sp = os.path.join(vault, src)
        if not os.path.exists(sp):
            problems.append(f'{src}: source missing')
            continue
        with open(sp, encoding='utf-8', errors='replace') as fh:
            for ln in fh:
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
