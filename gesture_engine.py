import math
from enum import Enum
import mediapipe.python.solutions.hands as mp_hands

# We use an Enum to strictly define states. This prevents spelling mistakes
# and makes it incredibly easy to add new gestures later.
class Gesture(Enum):
    NONE = "NONE"
    POINT = "POINT"           # Only index finger up (Laser pointer)
    PINCH = "PINCH"           # Thumb and index tips touching
    GRAB = "GRAB"             # All fingers closed (Fist)
    OPEN_PALM = "OPEN_PALM"   # All fingers spread open
    OPEN_WIDENED = "OPEN_WIDENED" # All fingers open and spread wide (For future use)   
    OPEN_CLOSED = "OPEN_CLOSED" # All fingers open but close together (For future use)

class GestureEngine:
    def __init__(self, min_detection_confidence=0.7, min_tracking_confidence=0.7):
        """Initializes the MediaPipe Hands AI."""
        self.mp_hands = mp_hands
        self.hands = self.mp_hands.Hands(
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence,
            max_num_hands=2 # Support up to 2 hands for advanced combos later
        )
        
        # Fingertip landmark IDs
        self.TIP_IDS = [4, 8, 12, 16, 20]

    def process_frame(self, img_rgb):
        """Processes an RGB frame and returns the detected gestures and landmark coordinates."""
        results = self.hands.process(img_rgb)
        
        hand_data = [] # Will store a dictionary for each hand detected

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                
                # Get the semantic gesture state (What is the hand doing?)
                current_gesture = self._detect_gesture(hand_landmarks.landmark)
                
                # We package the raw data and the semantic meaning together
                hand_data.append({
                    "gesture": current_gesture,
                    "landmarks": hand_landmarks.landmark, # The raw 21 points
                    "raw_hand": hand_landmarks            # Kept for drawing lines later
                })
                
        return hand_data

    def _get_distance(self, p1, p2):
        """Helper to calculate distance between two normalized landmarks."""
        return math.hypot(p2.x - p1.x, p2.y - p1.y)

    def _detect_gesture(self, landmarks):
        """
        The core State Machine. Analyzes distances and finger angles 
        to determine the current gesture.
        """
        # 1. Determine which fingers are "open" (pointing up)
        fingers_open = []
        
        # Thumb is special, we check X axis instead of Y axis
        if landmarks[self.TIP_IDS[0]].x > landmarks[self.TIP_IDS[0] - 1].x:
            fingers_open.append(1) # Right hand logic (simplified for MVP)
        else:
            fingers_open.append(0)

        # 4 Fingers (Index, Middle, Ring, Pinky)
        for i in range(1, 5):
            # If the TIP is higher (smaller Y) than the lower joint, it is open
            if landmarks[self.TIP_IDS[i]].y < landmarks[self.TIP_IDS[i] - 2].y:
                fingers_open.append(1)
            else:
                fingers_open.append(0)

        total_fingers = fingers_open.count(1)

        # 2. Check for Specific Overrides (like a PINCH)
        # We check distance between Thumb tip (4) and Index tip (8)
        pinch_distance = self._get_distance(landmarks[4], landmarks[8])
        if pinch_distance < 0.05: # Threshold for a tight pinch
            return Gesture.PINCH

        # 3. Match states based on open fingers
        if total_fingers == 0:
            return Gesture.GRAB # Fist
            
        elif total_fingers == 5:
            return Gesture.OPEN_PALM
            
        # If ONLY the index finger (position 1 in our list) is open
        elif fingers_open == [0, 1, 0, 0, 0] or fingers_open == [1, 1, 0, 0, 0]:
            return Gesture.POINT
            
        # Add new gestures here easily! Example:
        # elif fingers_open == [0, 1, 1, 0, 0]: 
        #     return Gesture.PEACE_SIGN

        return Gesture.NONE

    def cleanup(self):
        self.hands.close()
