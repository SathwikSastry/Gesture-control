import math
import copy
from OpenGL.GL import *
from OpenGL.GLU import *

class SceneMaster:
    """Controls the entire 3D universe, holding multiple objects and history."""
    def __init__(self):
        self.objects = [Hologram(pos_x=0.0, pos_y=0.0, pos_z=-5.0)]
        self.active_index = 0
        self.history_stack = []
        self.xray_mode = False

    def render_scene(self):
        for i, obj in enumerate(self.objects):
            obj.render(is_active=(i == self.active_index), xray=self.xray_mode)

    def save_history(self):
        """Saves a Deep Copy of the entire universe for the SHAKA Undo gesture."""
        if len(self.objects) > 0:
            self.history_stack.append(copy.deepcopy(self.objects[self.active_index].vertices))
            if len(self.history_stack) > 10:
                self.history_stack.pop(0)

    def undo(self):
        if self.history_stack and self.objects:
            self.objects[self.active_index].vertices = self.history_stack.pop()

    def spawn_object(self, x, y):
        # Spawn a new cube slightly offset
        new_cube = Hologram(pos_x=0.0, pos_y=0.0, pos_z=-5.0)
        self.objects.append(new_cube)
        self.active_index = len(self.objects) - 1
        
    def delete_active(self):
        if len(self.objects) > 0:
            self.objects.pop(self.active_index)
            self.active_index = max(0, len(self.objects) - 1)

class Hologram:
    def __init__(self, pos_x=0.0, pos_y=0.0, pos_z=-5.0):
        # A simple cube for our initial MVP
        self.vertices = [
            [1.0, -1.0, -1.0], [1.0, 1.0, -1.0], [-1.0, 1.0, -1.0], [-1.0, -1.0, -1.0],
            [1.0, -1.0, 1.0], [1.0, 1.0, 1.0], [-1.0, -1.0, 1.0], [-1.0, 1.0, 1.0]
        ]
        # Connecting the corners
        self.edges = [
            (0,1), (0,3), (0,4), (2,1), (2,3), (2,7),
            (6,3), (6,4), (6,7), (5,1), (5,4), (5,7)
        ]
        
        # Solid Faces (For the cyber-hologram look)
        self.faces = [
            (0,1,2,3), # Back
            (3,2,7,6), # Top
            (6,7,5,4), # Front
            (4,5,1,0), # Bottom
            (1,5,7,2), # Right
            (4,0,3,6)  # Left
        ]
        
        # Transform states
        self.pos_x, self.pos_y, self.pos_z = pos_x, pos_y, pos_z
        self.rot_x, self.rot_y = 0.0, 0.0
        self.scale = 1.0

        # Memory for Raycasting Matrix
        self.modelview = None
        self.projection = None
        self.viewport = None
        self.hovered_vertex = -1

    def render(self, is_active=True, xray=False):
        """Draws the 3D model applying all physics and math transformations."""
        glPushMatrix() 
        
        # 1. Translate (Move to position)
        glTranslatef(self.pos_x, self.pos_y, self.pos_z)
        
        # 2. Rotate (Spin the object)
        glRotatef(self.rot_x, 1, 0, 0)
        glRotatef(self.rot_y, 0, 1, 0)
        
        # 3. Scale (Resize the object)
        glScalef(self.scale, self.scale, self.scale)

        # CAPTURE MATRICES
        self.modelview = glGetDoublev(GL_MODELVIEW_MATRIX)
        self.projection = glGetDoublev(GL_PROJECTION_MATRIX)
        self.viewport = glGetIntegerv(GL_VIEWPORT)

        # Draw the solid faces (Translucent Cyberpunk Wiremesh)
        if not xray:
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            glBegin(GL_QUADS)
            if is_active:
                glColor4f(0.05, 0.15, 0.2, 0.6) # Active Translucent Cyber Blue
            else:
                glColor4f(0.3, 0.0, 0.0, 0.4)   # Inactive Dark Red
            for face in self.faces:
                for vertex in face:
                    glVertex3fv(self.vertices[vertex])
            glEnd()
            glDisable(GL_BLEND)

        # Draw the wireframe outline
        glLineWidth(2.0 if is_active else 1.0)
        glBegin(GL_LINES)
        if is_active:
            glColor3f(0.0, 0.8, 1.0) # Bright Cyan
        else:
            glColor3f(0.5, 0.0, 0.0) # Dim Red
        for edge in self.edges:
            for vertex in edge:
                glVertex3fv(self.vertices[vertex])
        glEnd()

        # Draw glowing vertex nodes only if active
        if is_active:
            glPointSize(10.0)
            glBegin(GL_POINTS)
            for i, vertex in enumerate(self.vertices):
                if i == self.hovered_vertex:
                    glColor3f(1.0, 0.0, 1.0) # Neon Magenta for hovered!
                else:
                    glColor3f(0.0, 1.0, 0.8) # Normal cyan nodes
                glVertex3fv(vertex)
            glEnd()
        
        glPopMatrix()

    def find_closest_vertex(self, screen_x, screen_y):
        """Phase 2 Spatial Math: Converts 3D points to 2D screen pixels to check if finger touches them."""
        if self.modelview is None or self.projection is None or self.viewport is None:
            return -1

        gl_y = self.viewport[3] - screen_y # Invert Y for OpenGL
        closest_idx = -1
        min_dist = float('inf')
        
        for i, v in enumerate(self.vertices):
            try:
                # Project 3D vertex to 2D screen coordinate
                px, py, pz = gluProject(v[0], v[1], v[2], self.modelview, self.projection, self.viewport)
                dist = math.hypot(px - screen_x, py - gl_y)
                if dist < 60: # 60 pixels radius for Virtual Touch
                    if dist < min_dist:
                        min_dist = dist
                        closest_idx = i
            except Exception:
                pass
        return closest_idx

    def apply_rotation(self, dx, dy):
        self.rot_y += dx 
        self.rot_x += dy 

    def apply_translation(self, dx, dy):
        self.pos_x += dx
        self.pos_y -= dy
        
    def deform_vertex(self, index, dx, dy):
        """Phase 2 Sculpting: Physically modifies a single coordinate of the geometry."""
        # Un-rotating the finger movement so the drag feels correct relative to the camera
        # For MVP, we apply a raw directional offset.
        self.vertices[index][0] += dx
        self.vertices[index][1] -= dy
