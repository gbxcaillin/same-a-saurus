"""Builds the single-file game: inlines everything under assets/ into index.html.
Usage: python3 tools/build.py"""
import base64, json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MIME = {'.webp': 'image/webp', '.png': 'image/png', '.mp4': 'video/mp4', '.jpg': 'image/jpeg'}
SKIP = {'icon-512.png', 'icon-180.png'}


def data_uri(path):
    ext = os.path.splitext(path)[1]
    with open(path, 'rb') as f:
        return f'data:{MIME[ext]};base64,' + base64.b64encode(f.read()).decode()


def main():
    assets = {}
    adir = os.path.join(ROOT, 'assets')
    for base, _, files in os.walk(adir):
        for fn in sorted(files):
            rel = os.path.relpath(os.path.join(base, fn), adir).replace(os.sep, '/')
            if rel in SKIP or os.path.splitext(fn)[1] not in MIME:
                continue
            assets[rel] = data_uri(os.path.join(base, fn))
    frames = json.load(open(os.path.join(ROOT, 'tools', 'dance_frames.json')))
    dance = {k: len(v) for k, v in frames.items() if f'dance/{k}.webp' in assets}
    html = open(os.path.join(ROOT, 'src', 'game.html'), encoding='utf-8').read()
    html = html.replace('/*__ASSETS__*/{}', json.dumps(assets, separators=(',', ':')))
    html = html.replace('/*__DANCE__*/{}', json.dumps(dance, separators=(',', ':')))
    html = html.replace('/*__ICON__*/', data_uri(os.path.join(adir, 'icon-180.png')))
    assert '/*__' not in html, 'unreplaced placeholder'
    out = os.path.join(ROOT, 'index.html')
    open(out, 'w', encoding='utf-8').write(html)
    print(f'index.html  {os.path.getsize(out)/1024:.0f} KB  ({len(assets)} assets, dance: {sorted(dance)})')


if __name__ == '__main__':
    main()
