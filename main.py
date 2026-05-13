import cv2
import pygame
import mediapipe.python.solutions.hands as mp_hands
import mediapipe.python.solutions.drawing_utils as mp_drawing
from camera_renderer import Renderer
from gesture_engine import GestureEngine, Gesture
from physics_engine import Hologram

def main():
    print("INITIALIZING J.A.R.V.I.S. INTERFACE...")
    
    # 1. Boot up our core systems
    cap = cv2.VideoCapture(0)
    renderer = Renderer(width=1280, height=720) # AR Video Engine
    gestures = GestureEngine()                  # AI State Machine
    holo = Hologram()                           # 3D Math Engine

    # Variables to track hand movement between frames (for deltas)
    prev_x, prev_y = None, None
    
    # Pygame clock to manage framerate
    clock = pygame.time.Clock()

    # Variable to lock onto a vertex during sculpting
    locked_vertex = -1

    print("SYSTEM ONLINE. Point to rotate, Pinch to move.")

    running = True
    while running:
        # 2. Check for exit commands
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
        
        # 3. Capture camera frame
        success, frame = cap.read()
        if not success:
            continue
        
        # Mirror image feels much more natural
        frame = cv2.flip(frame, 1)
        h, w = frame.shape[:2]

        # 4. Neural Tracking
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        hand_data = gestures.process_frame(img_rgb)
        
        # Cyberpunk HUD Processing
        h, w = frame.shape[:2]
        
        # Dim the webcam slightly for that "holographic blueprint" contrast
        frame = cv2.convertScaleAbs(frame, alpha=0.5, beta=0) 
        
        # Draw Cyberpunk Grid
        for i in range(0, w, 150):
            cv2.line(frame, (i, 0), (i, h), (0, 40, 20), 1)
        for i in range(0, h, 150):
            cv2.line(frame, (0, i), (w, i), (0, 40, 20), 1)
            
        # Draw Text UI
        cv2.putText(frame, "J.A.R.V.I.S. // SPATIAL OS v2.0", (30, 40), cv2.FONT_HERSHEY_PLAIN, 1.5, (0, 255, 255), 2)
        cv2.putText(frame, f"TRACKING NODES: {len(hand_data)}", (30, 70), cv2.FONT_HERSHEY_PLAIN, 1.2, (0, 200, 200), 1)
        
        # Display Current Mode
        mode_text = "[IDLE]"
        
        # Draw the physical hand wireframes onto the video frame
        if hand_data:
            for hand in hand_data:
                mp_drawing.draw_landmarks(
                    frame, 
                    hand['raw_hand'], 
                    mp_hands.HAND_CONNECTIONS,
                    mp_drawing.DrawingSpec(color=(255, 0, 255), thickness=2, circle_radius=4), # Neon Pink Nodes
                    mp_drawing.DrawingSpec(color=(0, 255, 255), thickness=2, circle_radius=2)  # Cyan connections
                )

        # 5. RENDER PHASE 1: Draw the flat 2D video background
        renderer.draw_background(frame)
        
        # 6. RENDER PHASE 2: Setup 3D math over the video
        renderer.setup_perspective()

        # 7. INTERACTION LOGIC
        holo.hovered_vertex = -1

        if hand_data:
            primary_hand = hand_data[0]
            current_state = primary_hand['gesture']
            landmarks = primary_hand['landmarks']
            
            index_x = landmarks[8].x * w
            index_y = landmarks[8].y * h
            
            # --- PHASE 2: RAYCASTING ---
            # Check if our finger is intersecting any 3D corners!
            closest_v = holo.find_closest_vertex(index_x, index_y)
            
            # Draw targeting reticle
            cv2.circle(frame, (int(index_x), int(index_y)), 10, (0, 255, 255), 2)

            if closest_v != -1 and current_state == Gesture.POINT:
                holo.hovered_vertex = closest_v
                cv2.putText(frame, f"TARGET LOCKED: v_{closest_v}", (int(index_x)+20, int(index_y)), cv2.FONT_HERSHEY_PLAIN, 1.2, (0, 255, 255), 2)
                mode_text = "[TARGETING]"

            if prev_x is not None and prev_y is not None:
                dx = index_x - prev_x
                dy = index_y - prev_y

                # --- PHASE 2: SCULPTING LOGIC ---
                if current_state == Gesture.PINCH:
                    if locked_vertex == -1 and closest_v != -1:
                        locked_vertex = closest_v # Grab the vertex!
                        
                    if locked_vertex != -1:
                        # We are pinching an exact point! Deform the mesh!
                        holo.hovered_vertex = locked_vertex
                        holo.deform_vertex(locked_vertex, dx * 0.005, dy * 0.005)
                        mode_text = "[SCULPTING PROTOCOL]"
                        cv2.putText(frame, "DEFORMING MESH", (int(index_x)+20, int(index_y)), cv2.FONT_HERSHEY_PLAIN, 1.2, (255, 0, 255), 2)
                    else:
                        # Not hovering anything, move the whole object
                        holo.apply_translation(dx * 0.01, dy * 0.01)
                        mode_text = "[TRANSLATE]"
                        
                elif current_state == Gesture.POINT:
                    # Release the vertex lock if we stop pinching
                    locked_vertex = -1 
                    if holo.hovered_vertex == -1:
                        holo.apply_rotation(dx * 0.4, dy * 0.4)
                        mode_text = "[ORBIT]"
                else:
                     locked_vertex = -1
            else:
                 locked_vertex = -1

            prev_x, prev_y = index_x, index_y
        else:
            prev_x, prev_y = None, None
            locked_vertex = -1

        # Render HUD Mode Text
        cv2.putText(frame, mode_text, (30, 100), cv2.FONT_HERSHEY_PLAIN, 1.5, (0, 0, 255) if "SCULPT" in mode_text else (0, 255, 0), 2)
        
        # WE MUST DRAW THE BACKGROUND *AFTER* ADDING OUR OpenCV HUD TEXT!
        renderer.draw_background(frame)
        
        # 8. RENDER PHASE 3: Draw the modified 3D model
        holo.render()

        # 9. Push to screen
        renderer.update_display()
        clock.tick(60) # Target a smooth 60 FPS

    # Clean shutdown
    print("SHUTTING DOWN SYSTEM...")
    cap.release()
    gestures.cleanup()
    renderer.cleanup()

if __name__ == "__main__":
    main()
