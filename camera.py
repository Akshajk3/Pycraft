from settings import *
from frustum import Frustum

class Camera:
    def __init__(self, position, yaw, pitch):
        self.position = glm.vec3(position)
        self.yaw = glm.radians(yaw)
        self.pitch = glm.radians(pitch)

        self.up = glm.vec3(0, 1, 0)
        self.right = glm.vec3(1, 0, 0)
        self.forward = glm.vec3(0, 0, -1)

        self.m_proj = glm.perspective(V_FOV, ASPECT_RATIO, NEAR, FAR)
        self.m_view = glm.mat4()

        self.frustum = Frustum(self)

        self.vel = glm.vec3(0, 0, 0)

    def update(self):
        self.update_vectors()
        self.update_view_matrix()

    def update_view_matrix(self):
        self.m_view = glm.lookAt(self.position, self.position + self.forward, self.up)

    def update_vectors(self):
        self.forward.x = glm.cos(self.yaw) * glm.cos(self.pitch)
        self.forward.y = glm.sin(self.pitch)
        self.forward.z = glm.sin(self.yaw) * glm.cos(self.pitch)
        
        self.forward = glm.normalize(self.forward)
        self.right = glm.normalize(glm.cross(self.forward, glm.vec3(0, 1, 0)))
        self.up = glm.normalize(glm.cross(self.right, self.forward))

    def rotate_pitch(self, delta_y):
        self.pitch -= delta_y
        self.pitch = glm.clamp(self.pitch, -PITCH_MAX, PITCH_MAX)

    def rotate_yaw(self, delta_x):
        self.yaw += delta_x

    def move_left(self, speed):
        self.vel -= self.right * speed
    
    def move_right(self, speed):
        self.vel += self.right * speed

    def move_forward(self, speed):
        flat_forward = glm.normalize(glm.vec3(self.forward.x, 0, self.forward.z))
        self.vel += flat_forward * speed
    
    def move_back(self, speed):
        flat_forward = glm.normalize(glm.vec3(self.forward.x, 0, self.forward.z))
        self.vel -= flat_forward * speed
    
    def move_up(self, speed):
        self.position.y += speed
    
    def move_down(self, speed):
        self.position.y -= speed