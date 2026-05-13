# Technical Requirements Document (TRD)
## Project: J.A.R.V.I.S. Spatial 3D Holographic Interface

### 1. Technology Stack
- **Language:** Python 3.12+
- **Computer Vision:** OpenCV (`opencv-python`) - Core webcam capture and matrix flipping.
- **AI / Tracking:** MediaPipe (`mediapipe==0.10.14`) - Real-time Hand Landmark AI.
- **Graphics Engine:** PyOpenGL (`PyOpenGL`, `PyOpenGL_accelerate`) - Low-level GPU communication.
- **Windowing & Input:** Pygame (`pygame`) - Full-screen context creation and OS-level event management.
- **Mathematics:** NumPy (`numpy`) - High-performance matrix multiplications, quaternions, and geometry math.

### 2. Architecture & File Structure
To maintain scalability, the monolithic code is split into four explicit domains:

1. `main.py`
    - Main orchestrator loop.
    - Synchronizes the frame capture, gesture evaluation, and visual rendering loop.
2. `camera_renderer.py`
    - Binds Pygame and OpenGL.
    - Manages double-buffering.
    - Implements an Orthographic projection phase to render `cv2` pixels as a flat background GL Texture.
    - Implements a Perspective projection phase to render lighting, grid floors, and 3D meshes.
3. `gesture_engine.py`
    - Isolates MediaPipe initialization and processing.
    - Employs a State Machine returning high-level semantic states (e.g., `State.PINCHING`, `State.SCALING_TWO_HANDS`, `State.KARATE_CHOP`) via threshold logic based on relative landmark distances and temporal velocity mapping.
4. `physics_engine.py` (or `geometry.py`)
    - Handles Screen-to-World raycasting (using `gluUnProject`).
    - Handles model transforms (Translation, Rotation, Scaling).
    - Contains logic for modifying the `vertices` array dynamically to support "sculpting".

### 3. Critical Technical Challenges & Solutions

#### 3.1. The AR Render Loop
OpenGL struggles with mixing 2D backgrounds and 3D foregrounds if matrices are not strictly managed.
*Solution:* At every frame tick:
1. `glDisable(GL_DEPTH_TEST)`
2. Switch to `GL_PROJECTION` and `glLoadIdentity()`
3. Set Orthographic view matching screen dimensions.
4. Draw OpenCV frame as a 2D Texture quad.
5. `glEnable(GL_DEPTH_TEST)`
6. Switch to Perspective view (`gluPerspective`).
7. Draw 3D Models.

#### 3.2. Raycasting (Virtual Touch)
MediaPipe yields 2D normalized coordinates (0.0 to 1.0).
*Solution:* Multiply by screen dimensions to get pixel `(X, Y)`. OpenGL's `Y` axis is inverted compared to screen coordinates, so `glY = window_height - screenY`. Pass `(X, glY, Z)` into `gluUnProject` (where Z is both near and far clip planes) to create a parametric 3D line. Determine intersection with the model's bounding box to establish a "hit".

#### 3.3. Gesture Stability
Raw AI outputs are incredibly jittery. A naked "Pinch" trigger will fire off and on rapidly, causing massive glitching in 3D translations.
*Solution:* Implement a One-Euro Filter or simple Low-Pass Filter on the landmark coordinates. Implement internal hysteresis (e.g., Pinch starts at distance < 0.05, but doesn't "un-pinch" until distance > 0.08) to create stable state locking.

### 4. Hardware Requirements
- Multicore CPU (for MediaPipe processing).
- Web Camera (min 30 FPS, 720p).
- Any standard integrated or dedicated GPU supporting OpenGL 3.3+.
