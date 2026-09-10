# Sommerhaus Ella – Website-Neubau und Buchungsautomatik

Projekt für https://sommerhaus-fredersdorf.de. Dieses Repository enthält die neue Website
(`site/`) und den Plan. Sicherungen der alten Seite, Zugangsdaten und Analyseberichte mit
internen Details gehören in das private Repository `Sommerhaus_priv`, nicht hierher.

## Ziel

1. Neue, schnelle und schöne Startseite mit sichtbaren Nachtpreisen, Verfügbarkeitskalender und
   funktionierender Anfrage.
2. Bessere Sichtbarkeit bei Google und Bing, inklusive Google-Unternehmensprofil (Maps).
3. Anfragen kommen zuverlässig per E-Mail an, nichts muss täglich im Backend geprüft werden.
4. Home Assistant setzt die Gästeregelung automatisch aus dem Buchungskalender.

## Phasen

### Phase 0 – Sicherung und Vorschau (erledigt am 10.09.2026)
- Komplette Sicherung der alten Seite: Seiteninhalte inklusive Elementor-Daten, Einstellungen,
  Plugin- und Theme-Liste, alle 147 Medien im Original (60 MB) und in Web-Größe.
- HTML-Vorschau der neuen Startseite in `site/index.html`, Fotos in `site/assets/img/`.
- Nichts an der Live-Seite geändert.

### Phase 1 – Sofortmaßnahmen an der bestehenden Seite (vor dem Neubau, je 10–30 Minuten)
- Unbekannte Administrator-Konten auf „Abonnent“ setzen oder löschen, Passwörter der echten
  Admin-Konten erneuern, Zwei-Faktor-Anmeldung einrichten.
- PHP-Version bei IONOS auf 8.2 oder 8.3 umstellen, vorher Backup.
- Elementor Beta deaktivieren und Elementor auf die stabile Version zurücksetzen.
- Impressum anlegen, Footer mit Impressum, Datenschutz und AGB.
- AdSense entfernen.

### Phase 2 – Neue Startseite in WordPress umsetzen (Testseite seit 10.09.2026 unter /new live)
Entscheidung: WordPress bleibt (Complianz, AIOSEO, Site Kit, Buchungslogik), aber ohne Elementor.
Die neue Seite wird als Block-Theme-Seite über die REST-API angelegt, damit alles per API
pflegbar bleibt und die Seite deutlich schneller lädt (heute 109 Requests, 1,7 MB, LCP mobil 8,9 s).
- Vorschau freigeben und Inhalte bestätigen: Preise, Saisonzeiten, Stornoregeln, Check-in-Zeiten,
  Hunde ja/nein, vollständige Namen fürs Impressum.
- Seite als Entwurf in WordPress anlegen, mit Fotos in Web-Größe und Alt-Texten.
- Neue Seite auf einer Vorschau-URL prüfen, dann als Startseite setzen. Alte Seite bleibt als
  Entwurf erhalten, Rückweg jederzeit möglich.
- Title, Meta-Description, Schema.org `VacationRental`, Sitemap, Bing- und Google-Einreichung.

### Phase 3 – Anfrageformular und E-Mail-Zustellung
Stand 10.09.2026, Abend: Auf /new läuft jetzt das Formular von WP Booking System auf dem
Buchungszettel unter dem Kalender, im Look des zuvor gebauten Formulars. Damit landen Anfragen als
Buchung im Kalender und in der Buchungsliste (Testbuchung 14.–17.09. erfolgreich abgesendet).
Contact Form 7, Flamingo und Honeypot bleiben installiert, werden aber nicht mehr auf der Seite
verwendet und können entfernt werden.

Ursache der fehlenden Kalender-Mails (aus den Formulareinstellungen abgelesen): Unter
„Admin Benachrichtigung“ steht als E-Mail-Adresse des Absenders `{1:E-Mail}`, also die Adresse des
Gastes. Der IONOS-Server versendet dann im Namen fremder Domains, was Outlook, Gmail und andere
abweisen. Lösung: Absender auf `wordpress@sommerhaus-fredersdorf.de` setzen, „Antwort an“ bleibt
`{1:E-Mail}`. Gleiches im Reiter „Benutzer Benachrichtigung“. WordPress selbst stellt Mails zu,
das ist mit dem Contact-Form-7-Test bestätigt.

Noch zu ergänzen im WP-Booking-System-Formular (Formulare → Formular Ersteller): Felder „Name“,
„Anreise mit E-Auto?“ und „Hund dabei?“. Check & Log Email bleibt aktiv, um Mails nachzuvollziehen.
- Optional: Push-Benachrichtigung über Home Assistant bei neuer Anfrage.

### Phase 4 – Belegungskalender als gemeinsame Wahrheit
Empfehlung: ein Google-Kalender „Sommerhaus Ella Buchungen“ als einzige Quelle.
- Bestätigte Buchungen werden als Termin eingetragen (Anreise bis Abreise, Titel „Buchung Name,
  2 Erw. + 1 Kind, E-Auto“).
- FeWo-direkt-Buchungen per iCal-Import automatisch in denselben Kalender.
- Die Website liest den Kalender (öffentlicher iCal-Link, nur belegt/frei) und zeigt Verfügbarkeit.
- Alternative, falls WP Booking System bleiben soll: Premium-Version mit iCal-Export.

### Phase 5 – Home Assistant
Vorhandene Logik: `input_select.gaste` mit „Keine Gäste da“, „Gäste ohne E-Auto“, „Gäste mit
E-Auto“, dazu `sensor.gastelage` (Keine Gäste, Erwartet, Aktiv, Ruhen), `sensor.gaste_im_sommerhaus`
(Geräte am Sommerhaus-AP) und die Nachtruhe-Automationen.
- Google-Kalender-Integration in Home Assistant, Kalender-Entität `calendar.sommerhaus_buchungen`.
- Automation „Gäste aus Kalender“: bei Terminbeginn (Anreisetag, z. B. 14 Uhr) `input_select.gaste`
  auf „Gäste mit E-Auto“ oder „Gäste ohne E-Auto“ setzen, je nach Stichwort im Termin; bei
  Terminende (Abreisetag 11 Uhr) auf „Keine Gäste da“.
- Sicherung: manuelle Änderung am `input_select` gewinnt bis zum nächsten Termin; Push an Dirk und
  Kathrin bei jedem automatischen Wechsel.
- Erst bauen, wenn der Kalender in Phase 4 steht.

## Entscheidungen der Gastgeber (Stand 10.09.2026)
- Keine Preise auf der Seite. Im Preisbereich steht wieder der Satz „Fragen Sie Ihren Preis für einen
  individuellen Buchungswunsch an.“ mit dem Oscar-Wilde-Zitat. Kein Preisrechner.
- Der Einstiegspreis „ab 116 € pro Nacht“ steht nur in den strukturierten Daten (`priceRange`),
  nicht im sichtbaren Text. Hinweis: Google übernimmt Ferienhaus-Preise nicht aus Schema.org,
  sondern aus Partner-Feeds und dem Unternehmensprofil; der Eintrag schadet nicht, bringt aber
  keine Preisanzeige in der Suche.
- Kein Tischtennis mehr. Grill und Waschmaschine sind inklusive.
- Bad und WC sind zwei getrennte Räume und werden getrennt gezeigt.
- Hunde sind willkommen, wenn sie die Hühner in Ruhe lassen.
- Mehr Fotos: jede Zimmerkarte hat eine Slideshow, dazu ein großer Rundgang (58 Fotos gesamt).

## SEO-Konzept der neuen Startseite
- Hauptbegriffe: „Ferienhaus Fredersdorf“, „Ferienhaus bei Berlin“, „Fachwerkhaus Garten“.
  Nebenbegriffe: „Fredersdorf-Vogelsdorf“, „S5 Ostkreuz“, „Bötzsee“, „Unterkunft Berlin Umland“.
- Platzierung statt Dichte: Hauptbegriff im Title, in der Meta-Description, im Eyebrow über der H1,
  in der H1 („Fachwerkhaus bei Berlin“), in der ersten H2 („Ferienhaus mit Garten“), im ersten
  Absatz und im Footer. Danach nur noch dort, wo es natürlich klingt. Ziel sind rund 1 bis 2 Prozent
  Keyword-Anteil im Fließtext, geprüft mit dem Lesefluss, nicht mit dem Zähler.
- Jedes Foto hat einen sprechenden Dateinamen (`ferienhaus-fredersdorf-<raum>-<motiv>.jpg`),
  einen beschreibenden Alt-Text und feste Breite und Höhe. Der Ortsname steht nur in einem Teil
  der Alt-Texte, damit es nicht wie Stuffing wirkt.
- Strukturierte Daten als `VacationRental` mit Adresse, Belegung, Betten, Bad und WC,
  Ausstattung, Haustiere und `priceRange`.
- Ein Thema pro Abschnitt mit eigener H2, damit Google Sprungmarken anbieten kann (Rundgang,
  Zimmer, Ausstattung, Preise, Verfügbarkeit, Anfrage, Lage, Fragen).
- Bilder laden verzögert, nur das Hero-Bild sofort. Keine externen Skripte außer Google Fonts.

## Offene Fragen an die Gastgeber
- Check-in und Check-out-Zeiten, Rauchen.
- Vollständige Namen und Umsatzsteuer-Status fürs Impressum.
- Google-Konto für das Unternehmensprofil und den Buchungskalender.
- Zugriff für die Claude-GitHub-App auf `Sommerhaus_priv` (für Sicherung und Berichte).

## Struktur
```
site/            neue Website (statische Vorschau, später Quelle für die WordPress-Blöcke)
site/assets/img  Fotos in Web-Größe
```
