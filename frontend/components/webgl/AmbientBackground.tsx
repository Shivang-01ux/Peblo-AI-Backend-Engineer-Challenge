"use client"

import { Canvas } from "@react-three/fiber"
import { OrbitControls } from "@react-three/drei"
import { ParticleWave } from "./ParticleWave"

export function AmbientBackground() {
  return (
    <div className="fixed inset-0 z-[-1] pointer-events-none overflow-hidden bg-background">
      <Canvas camera={{ position: [0, 5, 10], fov: 45 }}>
        <fog attach="fog" args={['#0a0a0a', 5, 20]} />
        <ambientLight intensity={0.5} />
        <ParticleWave />
        <OrbitControls enableZoom={false} enablePan={false} enableRotate={false} autoRotate autoRotateSpeed={0.5} />
      </Canvas>
    </div>
  )
}
