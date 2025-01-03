import pygame
from camera import Camera
from settings import *

class Player(Camera):
    def __init__(self, app, position=PLAYER_POS, yaw=-90, pitch=0):
        self.app = app
        super().__init__(position=position, yaw=yaw, pitch=pitch)
        self.sprinting = False

    def update(self):
        self.keyboard_control()
        self.mouse_control()
        super().update()

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            voxel_handler = self.app.scene.world.voxel_handler
            if event.button == 1:
                voxel_handler.set_voxel()
            if event.button == 3:
                voxel_handler.switch_mode()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LCTRL:
                self.sprinting = not self.sprinting

    def mouse_control(self):
        mouse_dx, mouse_dy = pygame.mouse.get_rel()
        if mouse_dx:
            self.rotate_yaw(mouse_dx * MOUSE_SENSITIVITY)
        if mouse_dy:
            self.rotate_pitch(mouse_dy * MOUSE_SENSITIVITY)

    def keyboard_control(self):
        key_state = pygame.key.get_pressed()

        if self.sprinting:
            vel = PLAYER_SPRINT_SPEED * self.app.delta_time
        else:
            vel = PLAYER_SPEED * self.app.delta_time

        if key_state[pygame.K_w]:
            self.move_forward(vel)
        if key_state[pygame.K_s]:
            self.move_back(vel)
        if key_state[pygame.K_d]:
            self.move_right(vel)
        if key_state[pygame.K_a]:
            self.move_left(vel)
        if key_state[pygame.K_SPACE]:
            self.move_up(vel)
        if key_state[pygame.K_LSHIFT]:
            self.move_down(vel)