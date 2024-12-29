import pygame
import math

# from pygame.sprite import _Group
from all_images import assets
import random


class Bullet(pygame.sprite.Sprite):
    def __init__(self, start_pos, end_pos):
        super().__init__()
        self.image = pygame.transform.scale(
            pygame.image.load("images/bullet.png"), (10, 10)
        ).convert_alpha()
        self.image.set_colorkey((78, 255, 186))
        self.rect = self.image.get_rect(center=start_pos)
        self.vector = (end_pos[0] - start_pos[0], end_pos[1] - start_pos[1])
        self.speed = 7

    def update(self, center):
        distance = math.sqrt(self.vector[0] ** 2 + self.vector[1] ** 2)
        if distance != 0:
            self.rect.x += (self.speed * self.vector[0] / distance) - (
                center.direction.x * center.speed * 2
            )
            self.rect.y += (self.speed * self.vector[1] / distance) - (
                center.direction.y * center.speed * 2
            )

    def render(self, display):
        display.blit(self.image, self.rect.topleft)


class EntityBullet(pygame.sprite.Sprite):
    def __init__(self, start_pos, end_pos, size=(10, 10)):
        super().__init__()
        self.image = pygame.transform.scale(
            pygame.image.load("images/entity_bullet.png"), size
        ).convert_alpha()
        self.image.set_colorkey((78, 255, 186))
        self.rect = self.image.get_rect(center=start_pos)
        self.vector = (end_pos[0] - start_pos[0], end_pos[1] - start_pos[1])
        self.speed = 7
        self.time_shot = 0

    def update(self, center):
        distance = math.sqrt(self.vector[0] ** 2 + self.vector[1] ** 2)
        if distance != 0:
            self.rect.x += (self.speed * self.vector[0] / distance) - (
                center.direction.x * center.speed * 2
            )
            self.rect.y += (self.speed * self.vector[1] / distance) - (
                center.direction.y * center.speed * 2
            )


class Gun(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.original_image = pygame.transform.scale(
            pygame.image.load("images/gun.png").convert(), (20, 53)  # (10, 48),
        )
        self.images = {}  # Dictionary to store pre-rendered rotated images
        self.pos = pos
        self.rect = self.original_image.get_rect(topleft=pos)
        self.original_image.set_colorkey((78, 255, 186))
        self.angle = 0
        self.reload = 0.1

    def shoot(self, cursor_pos, bullets):
        bullets.add(
            Bullet(
                (
                    self.rect.x + 10,
                    self.rect.y + 18,
                ),
                (
                    cursor_pos[0] + 30,
                    cursor_pos[1] + 40,
                ),
            ),
        )

    def update(self, target_pos, player_pos):

        dx = target_pos[0] - self.rect.centerx
        dy = target_pos[1] - self.rect.centery
        angle = math.degrees(
            math.atan2(-dy, dx) - 89.5
        )  # Adjusting angle due to image correction
        if player_pos[0] > target_pos[0]:
            angle = -angle + 5

        # Check if the rotated image for the current angle already exists in the cache
        if angle not in self.images:
            # If not, rotate the original image and store it in the cache
            self.images[angle] = pygame.transform.rotate(self.original_image, angle)
        self.image = self.images[angle]

        # Update the rect with the new image position
        self.rect = self.image.get_rect(topleft=(player_pos[0], player_pos[1] + 20))


class ShotgunEnemy(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.transform.scale(assets["shotgun"], (10, 48)).convert_alpha()
        self.images = {}  # Dictionary to store pre-rendered rotated images
        self.pos = pos
        self.rect = self.image.get_rect(topleft=pos)
        self.angle = 0
        self.reload = 0.8

        # Pre-render rotated images
        self.pre_render_images()

    def pre_render_images(self):
        for angle in range(0, 360):
            # Rotate the original image and store it in the cache
            self.images[angle] = pygame.transform.rotate(self.image, angle - 89.5)

    def shoot(self, selfcol, player, bullets):
        bullets.add(
            EntityBullet(
                (
                    selfcol.x + 20,
                    selfcol.y + 40,
                ),
                (
                    player.col.x + 30,
                    player.col.y + 40,
                ),
            ),
            EntityBullet(
                (
                    selfcol.x + 20,
                    selfcol.y + 40,
                ),
                (
                    player.col.x + random.randint(-30, 30),
                    player.col.y + random.randint(-40, 40),
                ),
            ),
            EntityBullet(
                (
                    selfcol.x + 20,
                    selfcol.y + 40,
                ),
                (
                    player.col.x + random.randint(-30, 30),
                    player.col.y + random.randint(-40, 40),
                ),
                size=(8, 8),
            ),
        )

    def update(self, target_pos, player_pos):
        dx = target_pos[0] - player_pos[0]
        dy = target_pos[1] - player_pos[1]
        angle = math.degrees(math.atan2(-dy, dx))  # Calculate angle

        # Adjust angle based on player orientation
        if player_pos[0] > target_pos[0]:
            angle = -angle

        # Use pre-rendered rotated image from the cache
        if player_pos[0] > target_pos[0]:  # Check if player is facing left
            self.image = pygame.transform.flip(
                self.images[int(angle) % 360], False, True
            )
        else:
            self.image = self.images[int(angle) % 360]

        # Update the rect with the new image position
        self.rect = self.image.get_rect(center=player_pos)

    # def update(self, target_pos, player_pos):

    #     dx = target_pos[0] - self.rect.centerx
    #     dy = target_pos[1] - self.rect.centery
    #     angle = math.degrees(
    #         math.atan2(-dy, dx) - 89.5
    #     )  # Adjusting angle due to image correction
    #     if player_pos[0] > target_pos[0]:
    #         angle = -angle + 5

    #     # Check if the rotated image for the current angle already exists in the cache
    #     if angle not in self.images:
    #         # If not, rotate the original image and store it in the cache
    #         self.images[angle] = pygame.transform.rotate(self.image, angle)
    #     self.image = self.images[angle]

    #     # Update the rect with the new image position
    #     self.rect = self.image.get_rect(topleft=(player_pos[0], player_pos[1] + 20))


class Shotgun(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.original_image = pygame.transform.scale(
            pygame.image.load("images/shotgun.png").convert_alpha(),
            (10, 48),  # (10, 48),
        )
        self.images = {}  # Dictionary to store pre-rendered rotated images
        self.pos = pos
        self.rect = self.original_image.get_rect(topleft=pos)
        self.angle = 0
        self.reload = 0.5

    def shoot(self, cursor_pos, bullets):
        bullets.add(
            Bullet(
                (
                    self.rect.x + 10,
                    self.rect.y + 18,
                ),
                (
                    cursor_pos[0] + 30,
                    cursor_pos[1],
                ),
            ),
            Bullet(
                (
                    self.rect.x + 10,
                    self.rect.y + 18,
                ),
                (
                    cursor_pos[0] + random.randint(-30, 30),
                    cursor_pos[1] + random.randint(-40, 40),
                ),
            ),
            Bullet(
                (
                    self.rect.x + 10,
                    self.rect.y + 18,
                ),
                (
                    cursor_pos[0] + random.randint(-30, 30),
                    cursor_pos[1] + random.randint(-40, 40),
                ),
            ),
        )

    def update(self, target_pos, player_pos):

        dx = target_pos[0] - self.rect.centerx
        dy = target_pos[1] - self.rect.centery
        angle = math.degrees(
            math.atan2(-dy, dx) - 89.5
        )  # Adjusting angle due to image correction
        if player_pos[0] > target_pos[0]:
            angle = -angle + 5

        # Check if the rotated image for the current angle already exists in the cache
        if angle not in self.images:
            # If not, rotate the original image and store it in the cache
            self.images[angle] = pygame.transform.rotate(self.original_image, angle)
        self.image = self.images[angle]

        # Update the rect with the new image position
        self.rect = self.image.get_rect(topleft=(player_pos[0], player_pos[1] + 20))


class RifleEnemy(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.transform.scale(assets["rifle"], (15, 48)).convert()
        self.images = {}  # Dictionary to store pre-rendered rotated images
        self.pos = pos
        self.rect = self.image.get_rect(topleft=pos)
        self.image.set_colorkey((78, 255, 186))
        self.angle = 0
        self.reload = 0.1

        # Pre-render rotated images
        self.pre_render_images()

    def pre_render_images(self):
        for angle in range(0, 360):
            # Rotate the original image and store it in the cache
            self.images[angle] = pygame.transform.rotate(self.image, angle - 89.5)

    def shoot(self, selfcol, player, bullets):
        bullets.add(
            EntityBullet(
                (
                    selfcol.x + 20,
                    selfcol.y + 40,
                ),
                (
                    player.col.x + random.randint(-30, 30),
                    player.col.y + random.randint(-30, 30),
                ),
            )
        )

    def update(self, target_pos, player_pos):
        dx = target_pos[0] - player_pos[0]
        dy = target_pos[1] - player_pos[1]
        angle = math.degrees(math.atan2(-dy, dx))  # Calculate angle

        # Adjust angle based on player orientation
        if player_pos[0] > target_pos[0]:
            angle = -angle

        # Use pre-rendered rotated image from the cache
        if player_pos[0] > target_pos[0]:  # Check if player is facing left
            self.image = pygame.transform.flip(
                self.images[int(angle) % 360], False, True
            )
        else:
            self.image = self.images[int(angle) % 360]

        # Update the rect with the new image position
        self.rect = self.image.get_rect(center=player_pos)


class Pistol(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.original_image = pygame.transform.scale(
            assets["pistol"].convert_alpha(), (20, 30)  # (10, 48),
        )
        self.images = {}  # Dictionary to store pre-rendered rotated images
        self.pos = pos
        self.rect = self.original_image.get_rect(topleft=pos)
        self.angle = 0
        self.reload = 0.3

    def shoot(self, cursor_pos, bullets):
        bullets.add(
            Bullet(
                (
                    self.rect.x + 10,
                    self.rect.y + 10,
                ),
                (
                    cursor_pos[0] + 30,
                    cursor_pos[1],
                ),
            ),
        )

    def update(self, target_pos, player_pos):

        dx = target_pos[0] - self.rect.centerx
        dy = target_pos[1] - self.rect.centery
        angle = math.degrees(
            math.atan2(-dy, dx) - 89.5
        )  # Adjusting angle due to image correction
        if player_pos[0] > target_pos[0]:
            angle = -angle + 5

        # Check if the rotated image for the current angle already exists in the cache
        if angle not in self.images:
            # If not, rotate the original image and store it in the cache
            self.images[angle] = pygame.transform.rotate(self.original_image, angle)
        self.image = self.images[angle]

        # Update the rect with the new image position
        self.rect = self.image.get_rect(topleft=(player_pos[0], player_pos[1] + 20))
