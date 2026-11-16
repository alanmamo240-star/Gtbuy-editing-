// Liste aller Videos. Jedes Video ist hochkant 1080x1920 mit 30 Bildern pro Sekunde.
import React from "react";
import { Composition } from "remotion";
import { TestVideo } from "./TestVideo";

export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="TestVideo"
      component={TestVideo}
      durationInFrames={150} // 150 Bilder / 30 pro Sekunde = 5 Sekunden
      fps={30}
      width={1080}
      height={1920}
    />
  );
};
