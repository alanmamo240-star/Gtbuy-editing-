// 5-Sekunden-Testvideo: eine hüpfende 3D-Cartoon-Figur mit Titel.
import React from "react";
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { ThreeCanvas } from "@remotion/three";
import { CartoonScene } from "./CartoonScene";

export const TestVideo: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();

  // Titel springt am Anfang ins Bild.
  const titleScale = spring({ frame, fps, config: { damping: 8 } });
  const fadeOut = interpolate(frame, [130, 150], [1, 0], { extrapolateLeft: "clamp" });

  return (
    <AbsoluteFill style={{ background: "linear-gradient(#7fd3ff, #c9f0ff)", opacity: fadeOut }}>
      <ThreeCanvas linear width={width} height={height} camera={{ position: [0, 1.5, 9], fov: 45 }}>
        <CartoonScene />
      </ThreeCanvas>
      <AbsoluteFill style={{ justifyContent: "flex-start", alignItems: "center", paddingTop: 220 }}>
        <div
          style={{
            transform: `scale(${titleScale})`,
            fontFamily: "Arial Black, Arial, sans-serif",
            fontSize: 110,
            color: "#ffde3b",
            WebkitTextStroke: "8px #2b2b2b",
            paintOrder: "stroke",
            textAlign: "center",
            lineHeight: 1.1,
          }}
        >
          ES
          <br />
          FUNKTIONIERT!
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
