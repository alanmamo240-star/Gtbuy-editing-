# Regeln für dieses Projekt

Der Nutzer ist kein Programmierer. Immer auf Deutsch antworten, jeden Schritt in einem einfachen Satz erklären und vor jeder Installation fragen.

## Videos: NUR POV-Geschichten

In diesem Ordner werden ausschließlich **POV-Geschichten** als Cartoon-Videos gemacht. Keine anderen Video-Arten, außer der Nutzer sagt ausdrücklich etwas anderes.

- **Ich-Perspektive:** Der Zuschauer ist die Hauptfigur. Man sieht die eigenen Hände und das eigene Handy, alles aus der Ich-Perspektive.
- **Stimmung:** Eine gruselige oder spannende Situation.
- **Ende:** Ein Cliffhanger und eine Frage an den Zuschauer, z. B. „Welcher ist echt? A oder B?“
- **Format:** Hochkant 1080x1920, 30 fps. Projekt liegt in `cartoon-videos/` (Remotion + three.js), siehe `cartoon-videos/ANLEITUNG.md`.

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
