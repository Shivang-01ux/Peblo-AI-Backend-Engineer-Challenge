"use client"

import { useRef, useMemo } from "react"
import { useFrame } from "@react-three/fiber"
import * as THREE from "three"

export function ParticleWave() {
  const pointsRef = useRef<THREE.Points>(null!)
  
  const particleCount = 2000
  const positions = useMemo(() => {
    const arr = new Float32Array(particleCount * 3)
    for (let i = 0; i < particleCount; i++) {
      const x = (Math.random() - 0.5) * 20
      const z = (Math.random() - 0.5) * 20
      const y = (Math.random() - 0.5) * 2
      
      arr[i * 3] = x
      arr[i * 3 + 1] = y
      arr[i * 3 + 2] = z
    }
    return arr
  }, [])

  useFrame((state) => {
    const time = state.clock.getElapsedTime()
    if (pointsRef.current) {
      const positionsAttr = pointsRef.current.geometry.attributes.position
      for (let i = 0; i < particleCount; i++) {
        const x = positionsAttr.getX(i)
        const z = positionsAttr.getZ(i)
        
        // Creating a dynamic wave effect
        const y = Math.sin((x + time) * 0.5) * Math.cos((z + time) * 0.5) * 2
        positionsAttr.setY(i, y)
      }
      positionsAttr.needsUpdate = true
      
      // Slow rotation of entire system
      pointsRef.current.rotation.y = time * 0.05
    }
  })

  return (
    <points ref={pointsRef}>
      <bufferGeometry>
        <bufferAttribute 
          attach="attributes-position" 
          count={positions.length / 3} 
          array={positions} 
          itemSize={3} 
          args={[positions, 3]}
        />
      </bufferGeometry>
      <pointsMaterial 
        size={0.06} 
        color="#00f3ff" 
        transparent 
        opacity={0.6} 
        blending={THREE.AdditiveBlending}
        sizeAttenuation
      />
    </points>
  )
}
