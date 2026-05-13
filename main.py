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
        
        # Draw the physical hand wireframes onto the video frame
        if hand_data:
            for hand in hand_data:
                mp_drawing.draw_landmarks(
                    frame, 
                    hand['raw_hand'], 
                    mp_hands.HAND_CONNECTIONS,
                    mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=4), # Green glowing effect
                    mp_drawing.DrawingSpec(color=(255, 255, 255), thickness=2, circle_radius=2)
                )

        # 5. RENDER PHASE 1: Draw the flat 2D video background
        renderer.draw_background(frame)
        
        # 6. RENDER PHASE 2: Setup 3D math over the video
        renderer.setup_perspective()

        # 7. INTERACTION LOGIC
        if hand_data:
            # For the MVP, we just track the first active hand
            primary_hand = hand_data[0]
            current_state = primary_hand['gesture']
            landmarks = primary_hand['landmarks']
            
            # Extract Index Finger coordinate (Point 8 in MediaPipe)
            index_x = landmarks[8].x * w
            index_y = landmarks[8].y * h

            # We need historical data to know how *fast* and what *direction* you moved
            if prev_x is not None and prev_y is not None:
                dx = index_x - prev_x
                dy = index_y - prev_y

                # --- THE BRAIN OF THE APP ---
                if current_state == Gesture.POINT:
                    # Laser-pointer mode -> Spins the object
                    holo.apply_rotation(dx * 0.4, dy * 0.4)
                
                elif current_state == Gesture.PINCH:
                    # Pinch mode -> Translates (drags) the object in 3D space
                    # We multiply by 0.01 because OpenGL uses tiny measurement units
                    holo.apply_translation(dx * 0.01, dy * 0.01)

            # Store the current position for the next loop
            prev_x, prev_y = index_x, index_y
        else:
            # If the hand leaves the screen, wipe the history so it doesn't teleport
            # when the hand enters the screen again.
            prev_x, prev_y = None, None

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
