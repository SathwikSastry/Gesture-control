# Project Requirements Document (PRD)
## Project: J.A.R.V.I.S. Spatial 3D Holographic Interface

### 1. Vision & Purpose
To build a "Tony Stark-level", full-screen, augmented reality (AR) workspace using standard webcam hardware. The application will render live camera feeds as a semi-transparent background within an OpenGL context, superimposing 3D models. Users will interact with these models using highly advanced, multi-state hand gestures—allowing for real-time architectural editing, geometric deformation, and spatial manipulation without hardware controllers.

### 2. Target Audience
- UI/UX Innovators exploring Spatial Computing.
- 3D Artists and Sculptors looking for intuitive modeling interfaces.
- Developers looking for advanced MediaPipe + OpenGL integration examples.

### 3. Core Features
- **Holographic AR Rendering:** Live webcam feed mapped as an Orthographic background texture beneath Perspective 3D models.
- **Complex Gesture State Machine:** Continuous tracking of finger positions, relative angles, and velocities to infer intent (not just raw coordinates).
- **Spatial Raycasting (Virtual Touch):** 2D screen-pixel-to-3D-world unprojection. Allowing fingers to physically "touch" specific vertices of a floating model.
- **Dynamic Mesh Deformation:** The ability to edit geometry in real-time.

### 4. The Gesture Lexicon
#### 4.1. MVP Gestures (To be implemented first)
- **Index Finger Point:** "Laser pointer" raycast. Highlights hovered vertex/edge.
- **Index + Thumb Pinch (One Hand):** Grab, free-move (translate), or vertex-pull.
- **Two-Hand Pinch & Stretch:** Scale/Zoom the object dynamically.
- **Open Palm Drag:** Orbit/Rotate the entire 3D camera view.
- **Fist (Closed Hand):** "Heavy Grab" / Lock object to hand.

#### 4.2. Advanced / V2 Gestures (Post-MVP Brainstorm)
- **Index "Karate Chop" (Fast Flat Hand):** Slice/split a polygon or model in two.
- **Thumb + Pinky Pinch (Shaka Sign):** Undo the last action/transformation.
- **Peace Sign (V):** Spawn a new 3D Primitive (Cube/Sphere) at the finger location.
- **Thumbs Down:** Delete the currently tracked object.
- **"Spiderman Web" (Index + Middle Pinch):** Snap object rotation to rigid 90-degree mathematical grids.
- **"Thanos Snap" (Middle Finger + Thumb snap):** Clear the entire scene / Reset workspace.
- **"Time Dial" (Turn invisible knob in air):** Scrub through the timeline (Undo/Redo history slider).
- **Clapping Hands Together:** Merge two separate 3D objects into one single mesh.
- **"Jazz Hands" (Spread all fingers wide explosively):** Disassemble or explode a 3D object into its primitive vertex points.
- **"Gun" Hand Shape:** Target and delete specific objects that are far away in the Z-axis.

### 5. Roadmap
- **Phase 1: Architecture & Rendering Pipeline:** Build the AR OpenGL context.
- **Phase 2: Raycasting & Math Engine:** Screen-to-world geometry intersections.
- **Phase 3: Gesture Engine Validation:** Ensure the state machine recognizes MVP gestures smoothly.
- **Phase 4: Transformation Integration:** Tie gestures to the math engine to move/scale/rotate.
- **Phase 5: V2 Gestures & Sculpting:** Add vertex pulling, slicing, spawning.
