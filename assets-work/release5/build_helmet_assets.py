"""Encode original AI-assisted helmet sheets without pixel or layout editing.

Run after generated-sheets.json has all eight output paths. Original face
sheets and generated PNGs are retained. Only format encoding uses Pillow.
"""
from pathlib import Path
import hashlib
import json
import shutil
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
WORK = Path(__file__).resolve().parent
ART = ROOT / 'dist/assets/art'
PEOPLE = {
    'a': ['hamilton', 'norris', 'max_verstappen'],
    'b': ['russell', 'leclerc', 'alonso'],
    'c': ['antonelli', 'piastri', 'sainz'],
    'd': ['albon', 'gasly', 'ocon'],
    'e': ['bottas', 'perez', 'hulkenberg'],
    'f': ['hadjar', 'lawson', 'arvid_lindblad'],
    'g': ['colapinto', 'bearman', 'bortoleto'],
    'h': ['stroll', 'tsunoda'],
}
paths = json.loads((WORK / 'generated-sheets.json').read_text())
assert set(paths) == set(PEOPLE), 'All eight generated sheets are required.'
manifest = {
    'people': {},
    'format': '6 columns x 3 rows / 6 animation frames per person',
    'attribution': 'Original AI-assisted pixel artwork. Driver-inspired helmets are fan interpretations, not exact current-season designs.',
    'version': 5,
}
provenance = []
ART.mkdir(parents=True, exist_ok=True)
for sheet, people in PEOPLE.items():
    source = Path(paths[sheet])
    im = Image.open(source)
    assert im.width / im.height == 1.5, (sheet, im.size)
    archive = WORK / ('helmets-' + sheet + '.png')
    shutil.copy2(source, archive)
    target = ART / ('helmets-' + sheet + '.webp')
    im.save(target, 'WEBP', quality=95, method=6)
    for row, person in enumerate(people):
        manifest['people'][person] = {
            'src': 'assets/art/' + target.name, 'row': row,
            'frames': 6, 'width': im.width, 'height': im.height,
        }
    original = ART / ('drivers-' + sheet + '.webp')
    provenance.append({
        'sheet': sheet, 'driverIds': people,
        'originalAsset': str(original.relative_to(ROOT)),
        'originalSHA256': hashlib.sha256(original.read_bytes()).hexdigest(),
        'generatedSource': str(source),
        'retainedPNG': str(archive.relative_to(ROOT)),
        'output': str(target.relative_to(ROOT)),
        'dimensions': list(im.size), 'columns': 6, 'rows': 3,
        'encoding': 'WebP quality 95; no resizing, cropping or pixel editing.',
        'inspection': 'Visually inspected: six full-body helmeted poses per mapped driver; closed visors and distinctive colour palettes.',
        'designStatus': 'Original fan interpretation; not an exact 2026 helmet replica.',
    })
assert len(manifest['people']) == 23
(WORK / 'helmet-manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
(WORK / 'provenance.json').write_text(json.dumps(provenance, indent=2) + '\n')
(ROOT / 'dist/helmet-artwork.js').write_text(
    'window.PADDOCK_HELMET_ART=' + json.dumps(manifest, separators=(',', ':')) + ';\n'
    'if(window.PADDOCK_ASSET_URLS){Object.values(window.PADDOCK_HELMET_ART.people).forEach(p=>{p.src=window.PADDOCK_ASSET_URLS[p.src]||p.src;});}\n'
)
print(json.dumps({'drivers': len(manifest['people']), 'sheets': len(paths),
                  'encodedBytes': sum((ART / ('helmets-' + x + '.webp')).stat().st_size for x in paths)}))
