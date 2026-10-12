"""Embed the original artwork, bitmap font, source snapshot and report in one HTML file."""
import base64
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / 'dist'


def export():
    page = (DIST / 'index.html').read_text()
    style = (DIST / 'style.css').read_text()
    font = base64.b64encode((DIST / 'assets/paddock-pixel.woff').read_bytes()).decode()
    style = style.replace('assets/paddock-pixel.woff', 'data:font/woff;base64,' + font)
    page = page.replace('<link rel="stylesheet" href="style.css">', '<style>' + style + '</style>')
    artwork = (DIST / 'pixel-art.js').read_text()
    page = page.replace('<script src="pixel-art.js"></script>', '<script>' + artwork.replace('</script', '<\\/script') + '</script>')
    assets = {str(p.relative_to(DIST)): 'data:image/webp;base64,' + base64.b64encode(p.read_bytes()).decode() for p in (DIST / 'assets/art').glob('*.webp')}
    asset_script = 'window.PADDOCK_ASSET_URLS=' + json.dumps(assets, separators=(',', ':')) + ';'
    manifest = (DIST / 'artwork.js').read_text()
    page = page.replace('<script src="artwork.js"></script>', '<script>' + asset_script + manifest + '</script>')
    script = (DIST / 'app.js').read_text()
    content = json.loads((DIST / 'data/content.json').read_text())
    embedded = json.dumps(content, ensure_ascii=False).replace('<', '\\u003c').replace('&', '\\u0026')
    report = json.dumps((DIST / 'progress.html').read_text().replace('href="index.html"', 'href="#" onclick="window.close();return false"'), ensure_ascii=False).replace('<', '\\u003c')
    report_script = '<script>const reportUrl=URL.createObjectURL(new Blob([' + report + '],{type:"text/html"}));document.querySelectorAll(\'a[href="progress.html"]\').forEach(a=>{a.href=reportUrl;a.target="_blank";a.rel="noopener";});</script>'
    page = page.replace('<script src="app.js"></script>', '<script>window.PIXEL_PADDOCK_BOOTSTRAP=' + embedded + ';</script><script>' + script.replace('</script', '<\\/script') + '</script>' + report_script)
    for name in ['pixel-paddock.html', 'pixel-paddock-v4.html']:
        (ROOT / name).write_text(page)
    print(json.dumps({'html': str(ROOT / 'pixel-paddock-v4.html'), 'bytes': len(page.encode()), 'embeddedSnapshot': True, 'embeddedArtworkAndFont': True}))


if __name__ == '__main__':
    export()
