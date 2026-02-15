import { Canvas } from "@react-three/fiber";
import { OrbitControls } from "@react-three/drei";
import { ReactNode } from "react";

interface ThreeScaffoldViewProps {
  bayLayout: number[];
  levels: number;
}

function ScaffoldMesh({ bayLayout, levels }: ThreeScaffoldViewProps) {
  const meshes: ReactNode[] = [];
  let xOffset = 0;
  bayLayout.forEach((bayWidth, bayIdx) => {
    for (let level = 0; level < levels; level += 1) {
      const y = level * 2;
      meshes.push(
        <mesh key={`${bayIdx}-${level}`} position={[xOffset + bayWidth / 2, y, 0]}>
          <boxGeometry args={[bayWidth, 0.12, 0.8]} />
          <meshStandardMaterial color="#3f4c5a" />
        </mesh>,
      );
    }
    xOffset += bayWidth;
  });
  return <>{meshes}</>;
}

export function ThreeScaffoldView({ bayLayout, levels }: ThreeScaffoldViewProps) {
  return (
    <div className="viewer-3d">
      <Canvas camera={{ position: [8, 6, 12], fov: 55 }}>
        <ambientLight intensity={0.8} />
        <directionalLight position={[8, 12, 4]} intensity={1.2} />
        <ScaffoldMesh bayLayout={bayLayout} levels={levels} />
        <gridHelper args={[30, 30, "#778899", "#d8dee4"]} />
        <OrbitControls />
      </Canvas>
    </div>
  );
}
