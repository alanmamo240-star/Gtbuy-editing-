# Cartoon-Videos fürs Handy

Format: Hochkant 1080x1920, 30 Bilder pro Sekunde. Gebaut mit Remotion + three.js (3D).

## Die wichtigsten Befehle (im Ordner `cartoon-videos` ausführen)

| Befehl | Was passiert |
|---|---|
| `npm install` | Lädt alle Bausteine (nur einmal nötig, z. B. auf einem neuen Computer). |
| `npm run studio` | Öffnet eine Vorschau im Browser, in der man das Video abspielen kann. |
| `npm run render` | Macht aus dem Testvideo eine fertige Datei: `out/testvideo.mp4`. |

## Wo ist was?

- `src/Root.tsx` – Liste aller Videos (Länge, Größe, Bilder pro Sekunde).
- `src/TestVideo.tsx` – das Testvideo (Hintergrund + Titel).
- `src/CartoonScene.tsx` – die 3D-Figur, die hüpft.
- `remotion.config.ts` – Einstellungen fürs Rendern (Software-3D ohne Grafikkarte).

Länge ändern: In `src/Root.tsx` bei `durationInFrames` gilt **Sekunden × 30** (z. B. 10 Sekunden = 300).
