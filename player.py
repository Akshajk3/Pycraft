import pygame
from camera import Camera
from settings import *

class Player(Camera):
    def __init__(self, app, position=PLAYER_POS, yaw=-90, pitch=0):
        self.app = app
        super().__init__(position=position, yaw=yaw, pitch=pitch)
        self.sprinting = False
        self.flying = True
        self.move_speed = 0
        self.vertical_vel = 0.0

    def update(self):
        self.keyboard_control()
        self.mouse_control()
        # self.handle_collision()
        super().update()
        self.position += glm.vec3(self.vel.x, 0, self.vel.z) * self.app.delta_time
        self.position.y += self.vertical_vel * self.app.delta_time

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            voxel_handler = self.app.scene.world.voxel_handler
            if event.button == 1:
                voxel_handler.remove_voxel()
            if event.button == 3:
                voxel_handler.add_voxel()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LCTRL:
                self.sprinting = not self.sprinting
            if event.key == pygame.K_f:
                self.flying = not self.flying
    
    def handle_collision(self):
        vh = self.app.scene.world.voxel_handler
        delta = self.vel * self.app.delta_time

        for axis in range(3):
            offset = glm.vec3(0)
            offset[axis] = delta[axis]
            new_pos = self.position + offset

            aabb_min, aabb_max = self.get_player_aabb(new_pos)
            if not self.is_colliding(vh, aabb_min, aabb_max):
                self.position = new_pos
            else:
                self.vel[axis] = 0

    def get_player_aabb(self, position):
        hw = PLAYER_HEIGHT / 2
        return (
            glm.vec3(position.x - hw, position.y, position.z - hw), # min
            glm.vec3(position.x + hw, position.y + PLAYER_HEIGHT, position.z + hw) # max
        )
    
    def is_colliding(self, voxel_handler, aabb_min, aabb_max):
        min_x = math.floor(aabb_min.x)
        max_x = math.ceil(aabb_max.x)
        min_y = math.floor(aabb_min.y)
        max_y = math.ceil(aabb_max.y)
        min_z = math.floor(aabb_min.z)
        max_z = math.ceil(aabb_max.z)

        for x in range(min_x, max_x):
            for y in range(min_y, max_y):
                for z in range(min_z, max_z):
                    voxel_id, *_ = voxel_handler.get_voxel_id(glm.ivec3(x, y, z))
                    if voxel_id != 0:
                        return True
        return False

    def is_grounded(self):
        ground_check = self.position.y - PLAYER_HEIGHT
        aabb_min, aabb_max = self.get_player_aabb(self.position)

        check_min_y = math.floor(ground_check)
        min_x = math.floor(aabb_min.x)
        max_x = math.ceil(aabb_max.x)
        min_z = math.floor(aabb_min.z)
        max_z = math.ceil(aabb_max.z)

        vh = self.app.scene.world.voxel_handler
        for x in range(min_x, max_x):
            for z in range(min_z, max_z):
                voxel_id, *_ = vh.get_voxel_id(glm.ivec3(x, check_min_y, z))
                if voxel_id != 0:
                    voxel_top_y = check_min_y + 1
                    if self.position.y >= voxel_top_y - 0.01:
                        return True
        return False

    def mouse_control(self):
        mouse_dx, mouse_dy = pygame.mouse.get_rel()
        if mouse_dx:
            self.rotate_yaw(mouse_dx * MOUSE_SENSITIVITY)
        if mouse_dy:
            self.rotate_pitch(mouse_dy * MOUSE_SENSITIVITY)

    def keyboard_control(self):
        self.vel.x = 0
        self.vel.z = 0

        is_grounded = self.is_grounded()

        key_state = pygame.key.get_pressed()

        if self.sprinting:
            speed = PLAYER_SPRINT_SPEED
        else:
            speed = PLAYER_SPEED

        if not self.flying:
            if not is_grounded:
                self.vertical_vel -= GRAVITY * self.app.delta_time
                self.vertical_vel = max(self.vertical_vel, TERMINAL_VEL)
            else:
                if key_state[pygame.K_SPACE]:
                    self.vertical_vel = PLAYER_JUMP
                else:
                    self.vertical_vel = 0.0
        else:
            if key_state[pygame.K_SPACE]:
                self.vertical_vel = self.move_speed
            elif key_state[pygame.K_LSHIFT]:
                self.vertical_vel = -self.move_speed
            else:
                self.vertical_vel = 0

        self.move_speed = speed

        if key_state[pygame.K_w]:
            self.move_forward(self.move_speed)
        if key_state[pygame.K_s]:
            self.move_back(self.move_speed)
        if key_state[pygame.K_d]:
            self.move_right(self.move_speed)
        if key_state[pygame.K_a]:
            self.move_left(self.move_speed)

        horizontal = glm.vec3(self.vel.x, 0, self.vel.z)
        if glm.length(horizontal) > 0:
            horizontal = glm.normalize(horizontal) * self.move_speed
            self.vel.x = horizontal.x
            self.vel.z = horizontal.z