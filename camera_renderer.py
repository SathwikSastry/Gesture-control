import cv2
import pygame
from pygame.locals import DOUBLEBUF, OPENGL
from OpenGL.GL import *
from OpenGL.GLU import *

class Renderer:
    def __init__(self, width=1280, height=720):
        pygame.init()
        self.width = width
        self.height = height
        
        # Setup Pygame window with OpenGL capabilities
        self.display = pygame.display.set_mode((self.width, self.height), DOUBLEBUF | OPENGL)
        pygame.display.set_caption("J.A.R.V.I.S. AR Interface")
        
        # Generate a pointer/ID for our webcam background texture
        self.bg_texture = glGenTextures(1)

    def draw_background(self, frame):
        """Renders the live OpenCV frame as a flat 2D background."""
        h, w = frame.shape[:2]
        
        # Convert BGR to RGB and flip vertically (OpenGL origin is bottom-left, not top-left)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_rgb = cv2.flip(frame_rgb, 0)
        img_data = frame_rgb.tobytes()

        # Disable 3D depth limits so this texture paints the absolute background
        glDisable(GL_DEPTH_TEST)
        
        # Switch to 2D Orthographic mode (Flat screen coords)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(0, self.width, 0, self.height)
        
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        # Update the OpenGL texture with the new webcam frame
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.bg_texture)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, w, h, 0, GL_RGB, GL_UNSIGNED_BYTE, img_data)

        # Draw a screen-sized rectangle and stick the texture onto it
        glColor3f(1.0, 1.0, 1.0)
        glBegin(GL_QUADS)
        glTexCoord2f(0.0, 0.0); glVertex2f(0, 0)
        glTexCoord2f(1.0, 0.0); glVertex2f(self.width, 0)
        glTexCoord2f(1.0, 1.0); glVertex2f(self.width, self.height)
        glTexCoord2f(0.0, 1.0); glVertex2f(0, self.height)
        glEnd()
        
        glDisable(GL_TEXTURE_2D)

    def setup_perspective(self):
        """Prepares the scene to render 3D objects over the 2D background."""
        # Turn depth tracking back on for 3D
        glEnable(GL_DEPTH_TEST)
        # VERY IMPORTANT: Clear the depth buffer, but NOT the color buffer, keeping our video visible!
        glClear(GL_DEPTH_BUFFER_BIT) 

        # Switch to 3D Perspective mode
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, (self.width / self.height), 0.1, 100.0)
        
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glTranslatef(0.0, 0.0, -5) # Pull camera back 5 units

    def update_display(self):
        pygame.display.flip()

    def cleanup(self):
        pygame.quit()
