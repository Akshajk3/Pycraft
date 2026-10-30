# Pycraft

**A voxel engine and Minecraft-style sandbox written in Python, rendered with ModernGL and GLSL shaders.**

<img width="800" height="469" alt="download (1)" src="https://github.com/user-attachments/assets/fd3b5b29-be96-43b6-8962-a0925413e183" />

Pycraft generates a procedurally built island of roughly **88 million blocks** (960 × 96 × 960) complete with mountains, caves, trees, water, and drifting clouds, and lets you fly around it, break blocks, and place new ones in real time.

Python isn't usually the language you'd pick for a voxel engine, so performance is the central problem. Pycraft handles it by moving the heavy work out of the Python interpreter: terrain generation and mesh building are JIT-compiled to machine code with **Numba**, and vertex data is bit-packed so that the GPU does as much of the rendering work as possible.

---

## Features

**World generation**
- Seed-based procedural terrain built from four octaves of OpenSimplex noise (fractal Brownian motion)
- A radial falloff mask that shapes the world into an island surrounded by water
- 3D noise carving that produces underground caves
- Height-based biome layers: sand beaches, grassland, dirt, gravel slopes, and snow-capped peaks, with per-block jitter so the boundaries look natural
- Deterministic tree placement with layered leaf canopies

**Rendering**
- Chunked world (48³ blocks per chunk, 20 × 2 × 20 chunks) with hidden-face culling, so only block faces exposed to air are meshed
- Per-vertex **ambient occlusion**, with quad-diagonal flipping to avoid AO interpolation artifacts
- **View-frustum culling** using bounding spheres, so chunks outside the camera's view are never drawn
- Texture arrays with separate top, side, and bottom textures per block type
- Gamma-correct lighting, directional face shading, and distance fog
- Translucent water plane with underwater tinting of terrain
- Animated cloud layer generated from noise and merged into larger quads to cut down vertex count

**Interaction**
- First-person free-fly camera with mouse look and sprint
- Block breaking and placing via **voxel ray casting** (the Amanatides–Woo DDA traversal algorithm)
- A highlighted marker on the targeted block, color-coded by mode
- Only the affected chunk (and neighbors, when editing on a chunk border) is re-meshed after an edit

---

## How it works

### Bit-packed vertices

Each vertex in a chunk mesh is stored as a **single 32-bit unsigned integer** instead of a set of floats:

| Field     | Bits | Purpose                              |
|-----------|------|--------------------------------------|
| x, y, z   | 6 each | Position within the chunk          |
| voxel_id  | 8    | Block type (selects texture layer)   |
| face_id   | 3    | Which of the 6 faces                 |
| ao_id     | 2    | Ambient occlusion level              |
| flip_id   | 1    | Whether the quad's diagonal is flipped |

The vertex shader (`shaders/chunk.vert`) unpacks these fields with bit shifts and masks, then derives texture coordinates, shading, and world position on the GPU. This keeps chunk meshes small in memory and fast to upload whenever a block changes.

### Ambient occlusion

For every exposed face, the mesh builder samples the eight neighboring blocks in the plane in front of that face and counts how many corners are enclosed. Each vertex gets one of four brightness levels, which produces soft contact shadows in corners and under overhangs without any real-time lighting. When the AO values across a quad are uneven, the quad is split along its other diagonal so the shading interpolates correctly.

### Frustum culling

Each chunk is approximated by a bounding sphere. Every frame, the camera tests each sphere against the near/far, top/bottom, and left/right planes of its view frustum, and chunks that fail are skipped entirely. Looking at the ground or at the ocean means most of the world isn't drawn at all.

### Ray casting for block selection

To figure out which block the player is looking at, a ray is cast from the camera along its forward vector and stepped through the voxel grid one cell boundary at a time. The first solid block hit becomes the target, and the axis the ray crossed last gives the face normal, which is what determines where a newly placed block goes.

### Terrain

Height at each (x, z) column is the sum of four noise octaves at doubling frequencies and halving amplitudes, then multiplied by an island mask based on distance from the world center. Below the surface, 3D noise decides where caves are carved out. Surface blocks are chosen by height band, with a small pseudo-random offset per block so biome edges aren't perfectly flat lines.

---

## Project structure

```
Pycraft/
├── host.py                 # Entry point
├── engine.py               # Window, OpenGL context, main loop, crosshair
├── settings.py             # All world, camera, and generation constants
├── scene.py                # Owns the world, water, clouds, and block marker
├── world.py                # Builds and stores all chunks
├── terrain_gen.py          # Height map, biomes, caves, trees (Numba)
├── noise.py                # Numba-compiled OpenSimplex wrappers
├── player.py               # Input handling and movement
├── camera.py               # View/projection matrices
├── frustum.py              # View-frustum culling
├── voxel_handler.py        # Ray casting, block placing/breaking
├── textures.py             # Texture and texture-array loading
├── shader_program.py       # Compiles shaders and sets uniforms
├── world_objects/          # Chunk, water, clouds, block marker
├── meshes/                 # Mesh classes and the Numba chunk mesh builder
├── shaders/                # GLSL vertex and fragment shaders
└── assets/                 # Block, water, and marker textures
```

---

## Getting started

### Requirements
- Python 3.12 or 3.13
- A GPU supporting OpenGL 3.3

### Install

```bash
git clone https://github.com/Akshajk3/Pycraft.git
cd Pycraft
pip install pygame moderngl PyGLM numpy numba opensimplex
```

### Run

```bash
python host.py
```

The first launch takes a little longer while Numba compiles the terrain and meshing functions; later launches use the cache.

### Controls

| Input            | Action                                  |
|------------------|-----------------------------------------|
| Mouse            | Look around                             |
| W / A / S / D    | Move                                    |
| Space            | Fly up                                  |
| Left Shift       | Fly down                                |
| Left Ctrl        | Toggle sprint                           |
| Left click       | Break or place a block (depends on mode) |
| Right click      | Switch between break and place mode     |
| Esc              | Quit                                    |

### Configuration

Most of the world can be tweaked in `settings.py`: world size, chunk size, biome height thresholds, tree density, water level, cloud height, field of view, and movement speed.

---

## Roadmap

- [ ] **Multiplayer:** host/client networking over sockets (`host.py` and `client.py` are scaffolded)
- [ ] Gravity and collision so the player walks instead of flies
- [ ] Block selection hotbar
- [ ] Infinite world with chunks streamed in around the player
- [ ] Saving and loading worlds

---

## Built with

[Python](https://www.python.org/) · [ModernGL](https://github.com/moderngl/moderngl) · [Pygame](https://www.pygame.org/) · [PyGLM](https://github.com/Zuzu-Typ/PyGLM) · [NumPy](https://numpy.org/) · [Numba](https://numba.pydata.org/) · [OpenSimplex](https://github.com/lmas/opensimplex) · GLSL

## Acknowledgments

Pycraft started from Coder Space's tutorial [**Creating a Voxel Engine (like Minecraft) from Scratch in Python**](https://www.youtube.com/watch?v=Ab8TOSFfNp4). The core engine (chunk meshing, packed vertex data, ambient occlusion, voxel ray casting, frustum culling, texture arrays, and terrain generation) follows the approach taught in that video.

On top of that foundation, I added:
- Seed-based terrain generation
- An on-screen crosshair
- A mouse-capture fix for macOS
- Sprint toggle
- The start of a host/client multiplayer system

The voxel ray casting is based on *A Fast Voxel Traversal Algorithm for Ray Tracing* by John Amanatides and Andrew Woo (1987).
