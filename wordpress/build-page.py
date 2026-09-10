#!/usr/bin/env python3
"""Baut aus site/index.html den WordPress-Seiteninhalt für /new und spielt ihn auf Wunsch ein.
Aufruf: python3 wordpress/build-page.py [--push]  (WP_USER, WP_APP_PASSWORD aus der Umgebung)"""
import re,json,os,sys,subprocess
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE='https://sommerhaus-fredersdorf.de'
ids=json.load(open(f'{ROOT}/wordpress/ids.json')); mm=json.load(open(f'{ROOT}/wordpress/media-map.json'))
html=open(f'{ROOT}/site/index.html',encoding='utf-8').read()
html=re.sub(r'assets/img/([^"]+)',lambda m: mm[m.group(1)]['url'] if m.group(1) in mm else m.group(0),html)
body=re.search(r'<body>(.*?)</body>',html,re.S).group(1)
style=re.search(r'<style>.*?</style>',html,re.S).group(0)
# Schriften lokal aus der WordPress-Schriftbibliothek (kein Google-Aufruf)
fonts=json.load(open(f'{ROOT}/wordpress/fonts.json'))
ff=''.join(f'@font-face{{font-family:"{v["family"]}";font-style:{f["style"]};font-weight:{f["weight"]};font-display:swap;src:url({f["src"]}) format("woff2")}}' for v in fonts.values() for f in v['faces'])
style=style.replace('<style>','<style>'+ff,1)
ld=re.search(r'<script type="application/ld\+json">.*?</script>',html,re.S).group(0)
body=re.sub(r'<div class="preview-banner">.*?</div>','<div class="preview-banner">Testseite der neuen Startseite. Noch nicht offiziell, Rückmeldungen willkommen.</div>',body,count=1)
body,n1=re.subn(r'<div class="months" id="months"></div>\s*<div class="legend">.*?</div>\n','<!-- /wp:html -->\n<!-- wp:shortcode -->\n[wpbs id="1" title="no" legend="yes" language="de"]\n<!-- /wp:shortcode -->\n<!-- wp:html -->\n',body,count=1,flags=re.S)
body=body.replace('<p class="lede">Der Kalender zeigt später live unsere Buchungen. Die Belegung hier ist ein Beispiel.</p>','<p class="lede">Rot markierte Tage sind belegt. Für freie Termine senden Sie uns unten eine Anfrage.</p>')
body,n2=re.subn(r'<form class="form-wrap" id="anfrage-form".*?</form>','<div class="form-wrap">\n<!-- /wp:html -->\n<!-- wp:shortcode -->\n[contact-form-7 id="%s" title="Buchungsanfrage"]\n<!-- /wp:shortcode -->\n<!-- wp:html -->\n</div>'%ids['form_id'],body,count=1,flags=re.S)
body,n3=re.subn(r'<div class="map" id="map" style="margin-top:24px">.*?</div>\s*</div>\s*</div>','<div class="map" id="map" style="margin-top:24px;border:0;padding:0;background:var(--moss-soft)"><iframe src="https://www.google.com/maps?q=Amselstr.%203%2C%2015370%20Fredersdorf-Vogelsdorf&amp;output=embed" width="100%" height="100%" style="border:0;min-height:320px" loading="lazy" allowfullscreen referrerpolicy="no-referrer-when-downgrade" title="Karte: Sommerhaus Ella, Amselstr. 3, Fredersdorf-Vogelsdorf"></iframe></div>\n      </div>',body,count=1,flags=re.S)
for a,b in [('<li><a href="#">Impressum</a></li>','<li><a href="/impressum/">Impressum</a></li>'),('<li><a href="#">Datenschutzerklärung</a></li>','<li><a href="/datenschutzerklaerung/">Datenschutzerklärung</a></li>'),('<li><a href="#">Allgemeine Geschäftsbedingungen</a></li>','<li><a href="/geschaeftsbedingungen/">Allgemeine Geschäftsbedingungen</a></li>'),('<li><a href="#">Cookie-Einstellungen</a></li>','<li><a href="/cookie-richtlinie-eu/">Cookie-Richtlinie</a></li>')]: body=body.replace(a,b)
body,n4=re.subn(r'  // Beispielkalender: zwei Monate.*?\n  \}\n\n','',body,count=1,flags=re.S)
body,n5=re.subn(r"  el\('map-btn'\).*?\n",'',body,count=1)
body,n6=re.subn(r"  el\('anfrage-form'\).*?\n",'',body,count=1)
assert (n1,n2,n3,n4,n5,n6)==(1,1,1,1,1,1), (n1,n2,n3,n4,n5,n6)
extra='<style>.wpcf7 .form-grid label{display:block}.wpcf7-form-control-wrap{display:block}.wpcf7-not-valid-tip{color:var(--brick);font-size:.85rem;margin-top:4px}.wpcf7-response-output{margin:16px 0 0;padding:12px 14px;border:1px solid var(--line)!important;border-radius:6px}.wpcf7-acceptance .wpcf7-list-item{margin:0}.wpcf7-spinner{margin-left:10px}.wpbs-container{margin-inline:auto}</style>'
content='<!-- wp:html -->\n'+ld+'\n'+style+'\n'+extra+'\n'+body+'\n<!-- /wp:html -->'
open(f'{ROOT}/wordpress/page-new-content.html','w',encoding='utf-8').write(content)
print('page-new-content.html gebaut,',round(len(content.encode())/1024),'KB')
if '--push' in sys.argv:
    u=os.environ['WP_USER'];pw=os.environ['WP_APP_PASSWORD']
    r=subprocess.run(['curl','-sS','-m','120','-u',f'{u}:{pw}','-X','POST',f"{BASE}/wp-json/wp/v2/pages/{ids['page_id']}",'-H','Content-Type: application/json','-d',json.dumps({'content':content},ensure_ascii=False)],capture_output=True,text=True)
    d=json.loads(r.stdout); print('WordPress:',d.get('id'),d.get('modified'),d.get('link')) if 'id' in d else print('FEHLER',r.stdout[:200])
    f=subprocess.run(['curl','-sS','-m','60','-u',f'{u}:{pw}','-X','DELETE',f'{BASE}/wp-json/ionos-performance/v1/flush','-o','/dev/null','-w','%{http_code}'],capture_output=True,text=True); print('Cache-Flush HTTP',f.stdout)
