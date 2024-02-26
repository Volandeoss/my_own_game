import pygame
from entities import PhysicsEntity
from tilemap import Block


class CameraGroup(pygame.sprite.Group):
    def __init__(self, entity_group, shooters, entitybullets, spikes):
        super().__init__()
        self.entity_group = entity_group
        self.entitybullets = entitybullets
        self.shooters = shooters
        self.spikes = spikes
        self.display_surface = pygame.display.get_surface()

        # camera offset
        self.offset = pygame.math.Vector2()
        self.half_w = self.display_surface.get_size()[0] // 2
        self.half_h = self.display_surface.get_size()[1] // 2

        # ground
        self.ground_surf = pygame.image.load("images/back_exp.png").convert_alpha()
        self.ground_rect = self.ground_surf.get_rect(center=(0, 0))

    def center_target_camera(self, target):
        self.offset.x = target.rect.centerx - self.half_w
        self.offset.y = target.rect.centery - self.half_h

    def custom_draw(self, player):
        self.center_target_camera(player)

        # ground
        ground_offset = self.ground_rect.topleft - self.offset
        self.display_surface.blit(self.ground_surf, ground_offset)

        # # Create a new surface to blit the ground and sprites onto
        # combined_surface = pygame.Surface(self.ground_surf.get_size(), pygame.SRCALPHA)
        # combined_surface.blit(self.ground_surf, (0, 0))

        # active elements

        for sprite in self.sprites():  # player and blocks
            offset_pos = sprite.rect.topleft - self.offset
            self.display_surface.blit(sprite.image, offset_pos)

        for sprite in self.spikes:
            offset_pos = sprite.rect.topleft - self.offset
            sprite.col.topleft = offset_pos
            self.display_surface.blit(sprite.image, offset_pos)

        for sprite in self.entity_group:  # entities
            offset_pos = sprite.rect.topleft - self.offset
            sprite.col.topleft = offset_pos
            self.display_surface.blit(sprite.image, offset_pos)
        for sprite in self.shooters:  # shooters and guns
            offset_pos = sprite.gun.rect.topleft - self.offset
            sprite.col.topleft = offset_pos
            self.display_surface.blit(sprite.image, offset_pos)
            self.display_surface.blit(
                sprite.gun.image, (offset_pos[0] + 10, offset_pos[1] + 20)
            )
