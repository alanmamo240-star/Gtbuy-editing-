# Regeln für dieses Projekt

Der Nutzer ist kein Programmierer. Immer auf Deutsch antworten, jeden Schritt in einem einfachen Satz erklären und vor jeder Installation fragen.

## Videos: NUR POV-Geschichten

In diesem Ordner werden ausschließlich **POV-Geschichten** als Cartoon-Videos gemacht. Keine anderen Video-Arten, außer der Nutzer sagt ausdrücklich etwas anderes.

- **Ich-Perspektive:** Der Zuschauer ist die Hauptfigur. Man sieht die eigenen Hände und das eigene Handy, alles aus der Ich-Perspektive.
- **Stimmung:** Eine gruselige oder spannende Situation.
- **Ende:** Ein Cliffhanger und eine Frage an den Zuschauer, z. B. „Welcher ist echt? A oder B?“
- **Format:** Hochkant 1080x1920, 30 fps. Projekt liegt in `cartoon-videos/` (Remotion + three.js), siehe `cartoon-videos/ANLEITUNG.md`.

## Ablauf jeder POV-Geschichte (immer in dieser Reihenfolge)

1. **Widerspruch in Sekunde 0:** Was man hört, passt nicht zu dem, was man liest (z. B. Stimme ruft „Komm rein!“, Handy zeigt „Bin verreist“).
2. **Erst wirkt alles normal, dann der erste RISS.**
3. **Die andere Seite meldet sich** (Nachricht, Klopfen oder Anruf).
4. **Beide behaupten, der andere ist falsch.** Es gibt einen Test, den **beide** bestehen.
5. **Es wird schlimmer:** Licht geht aus, ein Gerät macht etwas von allein.
6. **Twist am Ende, beide Seiten bleiben möglich.** Schlussfrage: „A oder B?“

Bei jeder Geschichte dem Nutzer zeigen, welcher Teil welchen der 6 Schritte erfüllt.

## Länge, Schnitt und Orte (bei JEDEM Video)

- **Länge:** 60 bis 85 Sekunden. Kürzer wirkt billig, länger verliert Zuschauer.
- **Sprechtext:** 165 bis 190 gesprochene Wörter (für ca. 60 Sekunden). Wörter immer nachzählen und Summe angeben.
- **Schnitt:** Alle 2–3 Sekunden ein neues Bild. Bei jedem neuen Satz wechselt die Einstellung.
- **Keine Pausen:** Keine langen Pausen in der Stimme. Kurz und knackig.
- **Mindestens 3 Orte**, und man sieht, wie man von einem Ort zum nächsten geht.

## Arbeitsablauf

1. Skript schreiben: Idee + gewählter Hook, Format (POV / Serie / Story), Bauplan des Formats einhalten, 165–190 Wörter.
2. Neben jeden Satz schreiben, was man in der Szene sieht (mit ungefährer Zeit).
3. **Skript dem Nutzer zeigen und auf sein OK warten, bevor das Video gebaut wird.**

Alles, was der Nutzer an Regeln oder Vorgaben schickt, hier in CLAUDE.md eintragen.

## Die 5 Hook-Regeln (bei JEDEM Video einhalten)

1. **Konflikt in Sekunde 0.** Das Problem ist sofort da, ohne Einleitung. Kein „Hallo, heute zeige ich euch …“.
2. **Ein Satz, den jeder versteht.** „Kevins Mama hat seinen Kanal übernommen!“ versteht jeder. „Das Mod-Turnier geht weiter“ versteht nur, wer die Serie kennt.
3. **Nah dran.** Das erste Bild zeigt ein Gesicht oder die Action groß und nah, nicht von weit weg.
4. **Die Frage oben als Titel.** Groß oben im Bild, z. B. „WER FÄHRT DICH NACH HAUSE?“
5. **Keine Bitten am Anfang.** „Schreib in die Kommentare …“ kommt erst ganz am Ende. Am Anfang kostet es Zuschauer.

Vor dem Abgeben eines Videos jede der 5 Regeln prüfen und dem Nutzer kurz sagen, wie sie erfüllt ist.

## Technische Hinweise

- Rendern: im Ordner `cartoon-videos` `npm run render` (oder `npx remotion render src/index.ts <ID> out/<name>.mp4`).
- Kein Grafikchip vorhanden: `remotion.config.ts` nutzt `swangle` (Software-3D) und den vorinstallierten Chromium unter `/opt/pw-browsers/`.
- Fertige Videos (`out/`) werden nicht in Git gespeichert, nur der Code.
