#!/usr/bin/env python3
"""Title check: no note carries a bare section-word title.

The batch-5 failure mode: a splitter shredded dailies at every `##` heading,
so generic section words ('Summary', 'Key Points', 'Produkty') became orphan
notes with no parent context, then got misfiled. Sections live glued to their
parent note, never as standalone files.

Usage: python3 titlecheck.py <vault-root>
Exit 1 (printing offenders) if any note title normalizes to a section word.
"""
import os
import re
import sys
import unicodedata

SECTION_WORDS = {
    # EN
    'summary', 'key points', 'notes', 'note', 'tldr', 'tl;dr', 'overview',
    'details', 'example', 'context', 'introduction', 'conclusion',
    'description', 'statistics', 'key details', 'key products',
    'video description summary', 'core philosophy', 'main flow',
    'watch list', 'next actions', 'repository structure',
    # PL
    'podsumowanie', 'glowne punkty', 'glowne tezy', 'tresc', 'tresc posta',
    'kontekst', 'wstep', 'uwagi', 'produkty', 'produkt', 'warianty',
    'cechy', 'zakres uslug', 'dostawa', 'statystyki', 'cytaty', 'wazne',
}


def norm(s: str) -> str:
    s = unicodedata.normalize('NFKD', s)
    s = ''.join(c for c in s if not unicodedata.combining(c))
    s = s.lower().replace(':', ' ').replace('-', ' ').replace('\u2014', ' ')
    return re.sub(r'\s+', ' ', s).strip()


def main(vault: str) -> int:
    bad = []
    flagged = []
    for root, dirs, files in os.walk(vault):
        dirs[:] = [d for d in dirs if not d.startswith(('.', '_'))]
        if 'smart-templates' in root.replace(vault, '').lstrip('/\\'):
            continue  # plugin-owned templates, not user triage targets
        for f in files:
            if not f.endswith('.md'):
                continue
            stem = norm(f[:-3])
            if stem in SECTION_WORDS:
                bad.append(os.path.join(root, f))
            else:
                # also catch "<date> - Summary" shapes
                if re.search(r'(^|\s)(summary|podsumowanie|key points|tresc|notes)$', stem):
                    bad.append(os.path.join(root, f))
                p = os.path.join(root, f)
                # importers can wrap the BODY inside frontmatter (block scalar):
                # a naive split then reads the note as empty/tag-only, and it
                # gets filed as "empty stub" and lost to Archive. Flag for a
                # raw-file read before any verdict.
                try:
                    with open(p, encoding='utf-8', errors='replace') as fh:
                        head = fh.read(65536)
                except OSError:
                    continue
                parts = head.split('---')
                fm = parts[1] if len(parts) > 2 else ''
                if fm.count('\n') > 60 or re.search(r'^(frontmatter|tags):\s*[|>][-+0-9]*\s*$', fm, re.M):
                    flagged.append(p + '  (frontmatter block-scalar or >60 lines: read raw file before classifying)')
    if bad:
        print(f'titlecheck: {len(bad)} section-title note(s):')
        for b in bad:
            print(' ', b)
        return 1
    if flagged:
        print(f'titlecheck: titles OK, but {len(flagged)} note(s) need a raw read (wrapped body):')
        for fl in flagged:
            print(' ', fl)
        return 1
    print('titlecheck: OK (no orphan section-title notes)')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else '.'))
