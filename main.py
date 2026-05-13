import cv2
import pygame
import mediapipe.python.solutions.hands as mp_hands
import mediapipe.python.solutions.drawing_utils as mp_drawing
from camera_renderer import Renderer
from gesture_engine import GestureEngine, Gesture
from physics_engine import SceneMaster

def main():
    print("INITIALIZING O.D.I.N. INTERFACE...")
    
    # 1. Boot up our core systems
    cap = cv2.VideoCapture(0)
    renderer = Renderer(width=1280, height=720) # AR Video Engine
    gestures = GestureEngine()                  # AI State Machine
    scene = SceneMaster()                       # Phase 3 Scene Manager

    # Variables to track hand movement between frames (for deltas)
    prev_x, prev_y = None, None
    
    # Pygame clock to manage framerate
    clock = pygame.time.Clock()

    # Variable to lock onto a vertex during sculpting
    locked_vertex = -1
    
    # Cooldown timer to prevent commands firing 60 times a second
    action_cooldown = 0

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
        cv2.putText(frame, "O.D.I.N. // SPATIAL OS v3.0", (30, 40), cv2.FONT_HERSHEY_PLAIN, 1.5, (0, 0, 255), 2)
        cv2.putText(frame, f"TRACKING NODES: {len(hand_data)}", (30, 70), cv2.FONT_HERSHEY_PLAIN, 1.2, (0, 0, 200), 1)
        cv2.putText(frame, f"ACTIVE OBJECTS: {len(scene.objects)}", (30, 100), cv2.FONT_HERSHEY_PLAIN, 1.2, (0, 0, 200), 1)
        
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
        if len(scene.objects) > 0:
            target_obj = scene.objects[scene.active_index]
        else:
            target_obj = None

        if target_obj:
            target_obj.hovered_vertex = -1
            
        if action_cooldown > 0:
            action_cooldown -= 1

        if hand_data:
            primary_hand = hand_data[0]
            current_state = primary_hand['gesture']
            landmarks = primary_hand['landmarks']
            
            index_x = landmarks[8].x * w
            index_y = landmarks[8].y * h
            
            # --- PHASE 3: MACRO COMMANDS (No Math Delta needed) ---
            if action_cooldown == 0:
                if current_state == Gesture.PEACE:
                    scene.spawn_object(0, 0)
                    mode_text = "[SPAWNING NEW GEOMETRY]"
                    action_cooldown = 30
                elif current_state == Gesture.MIDDLE:
                    scene.delete_active()
                    mode_text = "[DELETING TARGET]"
                    action_cooldown = 30
                elif current_state == Gesture.SHAKA:
                    scene.undo()
                    mode_text = "[UNDO TIME-SHIFT]"
                    action_cooldown = 30
                elif current_state == Gesture.SPIDERMAN:
                    scene.xray_mode = not scene.xray_mode
                    mode_text = "[TOGGLING X-RAY VISION]"
                    action_cooldown = 30

            # --- PHASE 3: MICRO COMMANDS (Need Math Delta) ---
            if target_obj:
                closest_v = target_obj.find_closest_vertex(index_x, index_y)
                cv2.circle(frame, (int(index_x), int(index_y)), 10, (0, 0, 255), 2) # Red reticle target

                if closest_v != -1 and current_state == Gesture.POINT:
                    target_obj.hovered_vertex = closest_v
                    cv2.putText(frame, f"TARGET LOCKED: v_{closest_v}", (int(index_x)+20, int(index_y)), cv2.FONT_HERSHEY_PLAIN, 1.2, (0, 0, 255), 2)
                    mode_text = "[TARGETING]"

                if prev_x is not None and prev_y is not None:
                    dx = index_x - prev_x
                    dy = index_y - prev_y

                    if current_state == Gesture.PINCH:
                        if locked_vertex == -1 and closest_v != -1:
                            locked_vertex = closest_v 
                            scene.save_history() # Save state before we start stretching it!
                            
                        if locked_vertex != -1: # Sculpting
                            target_obj.hovered_vertex = locked_vertex
                            target_obj.deform_vertex(locked_vertex, dx * 0.005, dy * 0.005)
                            mode_text = "[SCULPTING PROTOCOL]"
                        else: # Translate
                            target_obj.apply_translation(dx * 0.01, dy * 0.01)
                            mode_text = "[TRANSLATE]"
                            
                    elif current_state == Gesture.POINT:
                        locked_vertex = -1 
                        if target_obj.hovered_vertex == -1:
                            target_obj.apply_rotation(dx * 0.4, dy * 0.4)
                            mode_text = "[ORBIT]"
                            
                    elif current_state == Gesture.THUMBS_UP:
                        target_obj.apply_scale(0.05)
                        mode_text = "[GROWING]"
                    elif current_state == Gesture.THUMBS_DOWN:
                        target_obj.apply_scale(-0.05)
                        mode_text = "[SHRINKING]"
                    elif current_state == Gesture.OPEN_PALM:
                        mode_text = "[CALIBRATING]"
                    else:
                         locked_vertex = -1
                else:
                     locked_vertex = -1

            prev_x, prev_y = index_x, index_y
        else:
            prev_x, prev_y = None, None
            locked_vertex = -1

        # Render HUD Mode Text
        cv2.putText(frame, mode_text, (30, 130), cv2.FONT_HERSHEY_PLAIN, 1.5, (0, 0, 255), 2)
        
        # Draw background
        renderer.draw_background(frame)
        
        # 8. RENDER PHASE 3: Draw entire scene
        scene.render_scene()

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
