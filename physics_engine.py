from OpenGL.GL import *
from OpenGL.GLU import *

class Hologram:
    def __init__(self):
        # A simple cube for our initial MVP
        self.vertices = [
            [1, -1, -1], [1, 1, -1], [-1, 1, -1], [-1, -1, -1],
            [1, -1, 1], [1, 1, 1], [-1, -1, 1], [-1, 1, 1]
        ]
        # Connecting the corners
        self.edges = [
            (0,1), (0,3), (0,4), (2,1), (2,3), (2,7),
            (6,3), (6,4), (6,7), (5,1), (5,4), (5,7)
        ]
        
        # Solid Faces (For the Blender Grey look)
        self.faces = [
            (0,1,2,3), # Back
            (3,2,7,6), # Top
            (6,7,5,4), # Front
            (4,5,1,0), # Bottom
            (1,5,7,2), # Right
            (4,0,3,6)  # Left
        ]
        
        # Transform states (Where is the cube? How is it rotated? How big is it?)
        self.pos_x, self.pos_y, self.pos_z = 0.0, 0.0, -5.0
        self.rot_x, self.rot_y = 0.0, 0.0
        self.scale = 1.0

    def render(self):
        """Draws the 3D model applying all physics and math transformations."""
        glPushMatrix() # Save the current empty math matrix
        
        # 1. Translate (Move to position)
        glTranslatef(self.pos_x, self.pos_y, self.pos_z)
        
        # 2. Rotate (Spin the object)
        glRotatef(self.rot_x, 1, 0, 0)
        glRotatef(self.rot_y, 0, 1, 0)
        
        # 3. Scale (Resize the object)
        glScalef(self.scale, self.scale, self.scale)

        # Draw the solid faces (Blender Grey)
        glBegin(GL_QUADS)
        glColor3f(0.5, 0.5, 0.5) # Grey color
        for face in self.faces:
            for vertex in face:
                glVertex3fv(self.vertices[vertex])
        glEnd()

        # Draw the wireframe outline over the solid faces
        glLineWidth(2.0)
        glBegin(GL_LINES)
        glColor3f(0.1, 0.1, 0.1) # Dark grey/black outline
        for edge in self.edges:
            for vertex in edge:
                glVertex3fv(self.vertices[vertex])
        glEnd()
        
        glPopMatrix() # Restore the matrix so we don't mess up other drawings

    def apply_rotation(self, dx, dy):
        """Spins the object based on Delta (change in) hand movement."""
        self.rot_y += dx # Moving hand left/right rotates around the Y axis
        self.rot_x += dy # Moving hand up/down rotates around the X axis

    def apply_translation(self, dx, dy):
        """Moves the object strictly in X/Y 3D space."""
        self.pos_x += dx
        self.pos_y -= dy # Screen Y goes down, OpenGL Y goes up, so we invert it!
        
    def apply_scale(self, delta):
        """Resizes the object, clamping it so it doesn't invert or get too massive."""
        self.scale += delta
        self.scale = max(0.1, min(self.scale, 5.0))
