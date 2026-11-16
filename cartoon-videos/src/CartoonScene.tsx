// Die 3D-Szene: Boden, Sonne und eine runde Cartoon-Figur, die hüpft und sich dreht.
import React from "react";
import { useCurrentFrame } from "remotion";

const Eye: React.FC<{ x: number }> = ({ x }) => (
  <group position={[x, 0.35, 0.95]}>
    <mesh>
      <sphereGeometry args={[0.28, 32, 32]} />
      <meshToonMaterial color="white" />
    </mesh>
    <mesh position={[0, 0, 0.22]}>
      <sphereGeometry args={[0.12, 32, 32]} />
      <meshToonMaterial color="#1a1a1a" />
    </mesh>
  </group>
);

export const CartoonScene: React.FC = () => {
  const frame = useCurrentFrame();
  const t = frame / 30; // Zeit in Sekunden

  // Hüpfen: Betrag einer Sinuskurve ergibt "Boing"-Sprünge.
  const jump = Math.abs(Math.sin(t * Math.PI * 1.2)) * 2;
  // Quetschen beim Aufkommen auf dem Boden (Cartoon-Effekt).
  const squash = jump < 0.3 ? 1 - (0.3 - jump) * 0.8 : 1;
  const spin = t * 1.2;

  return (
    <>
      <ambientLight intensity={0.8} />
      <directionalLight position={[5, 8, 5]} intensity={2} />

      {/* Boden */}
      <mesh position={[0, -2.2, 0]} rotation={[-Math.PI / 2, 0, 0]}>
        <circleGeometry args={[6, 64]} />
        <meshToonMaterial color="#6ad46a" />
      </mesh>

      {/* Sonne */}
      <mesh position={[2.6, 4.2, -4]} rotation={[0, 0, t]}>
        <icosahedronGeometry args={[0.9, 0]} />
        <meshToonMaterial color="#ffcc00" />
      </mesh>

      {/* Figur */}
      <group position={[0, -1.2 + jump, 0]} rotation={[0, Math.sin(spin) * 0.6, 0]} scale={[1 / squash, squash, 1 / squash]}>
        <mesh>
          <sphereGeometry args={[1, 48, 48]} />
          <meshToonMaterial color="#ff6b8a" />
        </mesh>
        <Eye x={-0.35} />
        <Eye x={0.35} />
        {/* Mund */}
        <mesh position={[0, -0.3, 0.92]} rotation={[0, 0, Math.PI]}>
          <torusGeometry args={[0.25, 0.06, 16, 32, Math.PI]} />
          <meshToonMaterial color="#5a1a2a" />
        </mesh>
      </group>
    </>
  );
};
