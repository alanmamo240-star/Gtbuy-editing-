// Einstellungen für das Rendern. "swangle" sorgt dafür, dass 3D (WebGL) auch ohne Grafikkarte läuft (Software-3D).
import { Config } from "@remotion/cli/config";

Config.setChromiumOpenGlRenderer("swangle");
Config.setVideoImageFormat("jpeg");

// Benutzt den Browser, der auf diesem Rechner schon installiert ist (statt einen herunterzuladen).
// Falls du das Projekt auf einem anderen Computer benutzt, kannst du diese Zeile löschen.
import { existsSync } from "node:fs";
const localChrome = "/opt/pw-browsers/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell";
if (existsSync(localChrome)) {
  Config.setBrowserExecutable(localChrome);
}
