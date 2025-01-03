import pygame
import moderngl as mgl

class Textures:
    def __init__(self, app):
        self.app = app
        self.ctx : mgl.Context = app.ctx

        self.texture_0 = self.load('frame.png')
        self.texture_array_0 = self.load('tex_array_0.png', is_tex_array=True)

        self.texture_0.use(location=0)
        self.texture_array_0.use(location=1)
    
    def load(self, file_name, is_tex_array=False):
        texture = pygame.image.load(f'assets/{file_name}')
        texture = pygame.transform.flip(texture, flip_x=True, flip_y=False)

        if is_tex_array:
            num_layers = 3 * texture.get_height() // texture.get_width()
            texture = self.ctx.texture_array(
                size=(texture.get_width(), texture.get_height() // num_layers, num_layers),
                components=4,
                data=pygame.image.tostring(texture, 'RGBA', False)
            )
        else:
            texture = self.ctx.texture(
                size=texture.get_size(),
                components=4,
                data=pygame.image.tostring(texture, 'RGBA', False)
            )
        texture.anisotropy = 32.0
        texture.build_mipmaps()
        texture.filter = (mgl.LINEAR_MIPMAP_LINEAR, mgl.NEAREST)
        return texture