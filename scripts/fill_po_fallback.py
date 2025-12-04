import polib
import glob
from pathlib import Path

root = Path(__file__).resolve().parents[1]
po_paths = glob.glob(str(root / 'locale' / '*' / 'LC_MESSAGES' / 'django.po'))
summary = {}
for p in po_paths:
    po = polib.pofile(p)
    changed = 0
    for entry in po:
        if not entry.obsolete and (entry.msgstr is None or entry.msgstr.strip() == ''):
            # Fill fallback
            entry.msgstr = entry.msgid
            changed += 1
    if changed:
        po.save()
    summary[p] = changed

for p, c in summary.items():
    print(f"{p}: filled {c} entries")
