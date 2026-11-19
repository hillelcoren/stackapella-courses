"""Switch to variant (b), Beimel's melody only: python3 -I parked/shema-yisrael/apply-makers-b.py, then rebuild.
Makers and licence are not music, so no version bump (SyncOfficialTemplates::musicHash covers guide and sections only)."""
import json, os
here = os.path.dirname(os.path.abspath(__file__))
b = json.load(open(os.path.join(here, 'makers-b.json'), encoding='utf-8'))
p = os.path.join(here, 'build', 'meta.json')
m = json.load(open(p, encoding='utf-8'))
m['makers'] = b['makers']
m['licence']['tune'] = b['licence.tune']
text = json.dumps(m, indent=1, ensure_ascii=False) + '\n'
open(p, 'w', encoding='utf-8').write(text)
print('meta.json: variant (b); now run python3 -I parked/shema-yisrael/build/build.py templates/library/shema-yisrael.json')
