# WordPress-Fassung der neuen Startseite

Stand 10.09.2026. Die Testseite läuft unter https://sommerhaus-fredersdorf.de/new/ (noindex).

- `page-new-content.html` – der Seiteninhalt, wie er per REST-API in WordPress angelegt wurde:
  ein Custom-HTML-Block mit Stil und Markup aus `../site/index.html`, dazwischen zwei
  Shortcode-Blöcke: `[wpbs id="1" ...]` (Belegungskalender von WP Booking System) und
  `[contact-form-7 id="…"]` (Anfrageformular).
- `media-map.json` – Zuordnung Dateiname → Mediathek-ID und URL der 58 hochgeladenen Fotos.
- `ids.json` – Seiten-ID, Formular-ID und Link.

Seitenvorlage: `elementor_canvas` (ohne Theme-Kopf und -Fuß). Das Formular ist Contact Form 7
mit Flamingo (jede Anfrage bleibt im Backend unter „Flamingo“ gespeichert) und Honeypot-Spamschutz.
E-Mail geht an die Admin-Adresse mit Kopie an mail@sommerhaus-fredersdorf.de, der Gast erhält
eine Eingangsbestätigung.

Um die neue Seite zur Startseite zu machen: Einstellungen → Lesen → Startseite auf diese Seite
setzen, Slug von `new` auf die Startseite ändern und das Noindex in AIOSEO entfernen. Die alte
Startseite (ID 252) bleibt als Seite erhalten und kann jederzeit zurückgeschaltet werden.
