#!/usr/bin/env python3
"""Baut aus site/index.html den WordPress-Seiteninhalt für /new und spielt ihn auf Wunsch ein.

Aufruf: python3 wordpress/build-page.py [--push]
Umgebung: WP_USER und WP_APP_PASSWORD (Anwendungspasswort), nur mit --push nötig.

Was das Skript ersetzt:
- Bildpfade assets/img/... -> URLs aus der Mediathek (media-map.json)
- Schriften: lokale @font-face-Regeln aus der WordPress-Schriftbibliothek (fonts.json)
- Buchungszettel (Marker BOOKING:START/END) -> WP-Booking-System-Kalender + Contact-Form-7-Formular
- Karte -> Google-Maps-iframe, das Complianz bis zur Zustimmung blockiert
- Footer-Links -> echte Seiten
- JavaScript für Beispielkalender, Karte und Vorschauformular wird entfernt
"""
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = 'https://sommerhaus-fredersdorf.de'

ids = json.load(open(f'{ROOT}/wordpress/ids.json'))
media = json.load(open(f'{ROOT}/wordpress/media-map.json'))
fonts = json.load(open(f'{ROOT}/wordpress/fonts.json'))

html = open(f'{ROOT}/site/index.html', encoding='utf-8').read()
html = re.sub(r'assets/img/([^"]+)', lambda m: media[m.group(1)]['url'] if m.group(1) in media else m.group(0), html)

body = re.search(r'<body>(.*?)</body>', html, re.S).group(1)
style = re.search(r'<style>.*?</style>', html, re.S).group(0)
ld = re.search(r'<script type="application/ld\+json">.*?</script>', html, re.S).group(0)

# Schriften lokal einbinden (kein Aufruf an Google)
font_faces = ''.join(
    '@font-face{font-family:"%s";font-style:%s;font-weight:%s;font-display:swap;src:url(%s) format("woff2")}'
    % (fam['family'], face['style'], face['weight'], face['src'])
    for fam in fonts.values() for face in fam['faces']
)
style = style.replace('<style>', '<style>' + font_faces, 1)

# Hinweisbanner
body = re.sub(r'<div class="preview-banner">.*?</div>',
              '<div class="preview-banner">Testseite der neuen Startseite. Noch nicht offiziell, Rückmeldungen willkommen.</div>',
              body, count=1)

# Buchungszettel: echter Kalender + Formular
booking = (
    '\n<!-- /wp:html -->\n'
    '<!-- wp:shortcode -->\n[wpbs id="1" title="no" legend="yes" legend_position="side" language="de"]\n<!-- /wp:shortcode -->\n'
    '<!-- wp:html -->\n'
    '<p class="note" style="margin-top:14px">Tipp: Klicken Sie im Kalender zuerst auf den Anreise- und dann auf den Abreisetag, '
    'die Daten werden unten übernommen.</p>\n'
    '<div class="form-wrap">\n'
    '<!-- /wp:html -->\n'
    '<!-- wp:shortcode -->\n[contact-form-7 id="%s" title="Buchungsanfrage"]\n<!-- /wp:shortcode -->\n'
    '<!-- wp:html -->\n'
    '</div>\n'
) % ids['form_id']
body, n1 = re.subn(r'<!--BOOKING:START-->.*?<!--BOOKING:END-->', lambda m: booking, body, count=1, flags=re.S)

# Karte
map_iframe = (
    '<div class="map live" id="map" style="margin-top:24px">'
    '<iframe src="https://www.google.com/maps?q=Amselstr.%203%2C%2015370%20Fredersdorf-Vogelsdorf&amp;output=embed" '
    'width="100%" height="100%" style="border:0;min-height:320px" loading="lazy" allowfullscreen '
    'referrerpolicy="no-referrer-when-downgrade" title="Karte: Sommerhaus Ella, Amselstr. 3, Fredersdorf-Vogelsdorf"></iframe>'
    '</div>\n      </div>'
)
body, n2 = re.subn(r'<div class="map" id="map" style="margin-top:24px">.*?</div>\s*</div>\s*</div>', lambda m: map_iframe, body, count=1, flags=re.S)

# Footer-Links
for old, new in [
    ('<li><a href="#">Impressum</a></li>', '<li><a href="/impressum/">Impressum</a></li>'),
    ('<li><a href="#">Datenschutzerklärung</a></li>', '<li><a href="/datenschutzerklaerung/">Datenschutzerklärung</a></li>'),
    ('<li><a href="#">Allgemeine Geschäftsbedingungen</a></li>', '<li><a href="/geschaeftsbedingungen/">Allgemeine Geschäftsbedingungen</a></li>'),
    ('<li><a href="#">Cookie-Einstellungen</a></li>', '<li><a href="/cookie-richtlinie-eu/">Cookie-Richtlinie</a></li>'),
]:
    body = body.replace(old, new)

# Vorschau-JavaScript entfernen (Beispielkalender, Kartenknopf, Vorschauformular)
body, n3 = re.subn(r'  // Beispielkalender: zwei Monate.*?\n  \}\n\n', '', body, count=1, flags=re.S)
body, n4 = re.subn(r"  el\('map-btn'\).*?\n", '', body, count=1)
body, n5 = re.subn(r"  el\('anfrage-form'\).*?\n", '', body, count=1)
assert (n1, n2, n3, n4, n5) == (1, 1, 1, 1, 1), (n1, n2, n3, n4, n5)

extra = (
    '<style>'
    '.wpcf7 .form-grid label{display:block}.wpcf7-form-control-wrap{display:block}'
    '.wpcf7-not-valid-tip{color:#B5452D;font-size:.85rem;margin-top:4px}'
    '.wpcf7-response-output{margin:16px 0 0;padding:12px 14px;border:1px solid #D6DACF!important;border-radius:6px}'
    '.wpcf7-acceptance .wpcf7-list-item{margin:0}.wpcf7-spinner{margin-left:10px}'
    '.paper .wpbs-container{margin:0 auto}'
    '.paper .wpbs-date[data-day]:not(.wpbs-legend-item-2){cursor:pointer}'
    '</style>'
)

# Inline-Skript gegen WordPress-Textfilter schützen (wptexturize wandelt sonst & < > um):
# das JavaScript wird Base64-kodiert und zur Laufzeit entpackt.
import base64
def _protect(m):
    code = m.group(1)
    b64 = base64.b64encode(code.encode('utf-8')).decode('ascii')
    return ('<script>(function(){var b=atob("%s");var a=new Uint8Array(b.length);'
            'for(var i=0;i<b.length;i++){a[i]=b.charCodeAt(i);}'
            'new Function(new TextDecoder().decode(a))();})();</script>') % b64
body, n6 = re.subn(r'<script>(?!\(function\(\)\{var b=atob)(.*?)</script>', _protect, body, count=1, flags=re.S)
assert n6 == 1, 'Inline-Skript nicht gefunden'

content = '<!-- wp:html -->\n' + ld + '\n' + style + '\n' + extra + '\n' + body + '\n<!-- /wp:html -->'
open(f'{ROOT}/wordpress/page-new-content.html', 'w', encoding='utf-8').write(content)
print('page-new-content.html gebaut,', round(len(content.encode()) / 1024), 'KB')

if '--push' in sys.argv:
    user = os.environ['WP_USER']
    pw = os.environ['WP_APP_PASSWORD']
    r = subprocess.run(
        ['curl', '-sS', '-m', '120', '-u', f'{user}:{pw}', '-X', 'POST',
         f"{BASE}/wp-json/wp/v2/pages/{ids['page_id']}", '-H', 'Content-Type: application/json',
         '-d', json.dumps({'content': content}, ensure_ascii=False)],
        capture_output=True, text=True)
    d = json.loads(r.stdout)
    print('WordPress:', d.get('id'), d.get('modified'), d.get('link')) if 'id' in d else print('FEHLER', r.stdout[:200])
    f = subprocess.run(
        ['curl', '-sS', '-m', '60', '-u', f'{user}:{pw}', '-X', 'DELETE',
         f'{BASE}/wp-json/ionos-performance/v1/flush', '-o', '/dev/null', '-w', '%{http_code}'],
        capture_output=True, text=True)
    print('Cache-Flush HTTP', f.stdout)
