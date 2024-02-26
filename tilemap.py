import pygame
from all_images import assets


class Block(pygame.sprite.Sprite):
    def __init__(self, pos, type, group):
        super().__init__(group)
        match type:
            case 0:
                self.image = pygame.transform.scale(
                    pygame.image.load("images/wall_up.png").convert_alpha(), (100, 25)
                )
            case 1:
                self.image = pygame.transform.scale(
                    pygame.image.load("images/wall_down.png").convert_alpha(), (100, 25)
                )
            case 2:
                self.image = pygame.transform.scale(
                    pygame.image.load("images/wall_left.png").convert_alpha(), (25, 100)
                )
            case 3:
                self.image = pygame.transform.scale(
                    pygame.image.load("images/wall_right.png").convert_alpha(),
                    (25, 100),
                )
        self.rect = self.image.get_rect(topleft=pos)


class Floor(pygame.sprite.Sprite):
    def __init__(self, path, pos, group):
        super().__init__(group)
        self.image = pygame.transform.scale(pygame.image.load(path).convert(), (50, 50))
        self.rect = self.image.get_rect(topleft=pos)


class Spikes(pygame.sprite.Sprite):
    def __init__(self, pos, group):
        super().__init__(group)
        self.animation = assets["spikes"].copy()
        self.image = self.animation.img()
        self.rect = self.image.get_rect(topleft=pos)
        self.col = self.rect.copy()
        self.id = 1

    def update(self, player):
        self.animation.update()
        self.image = self.animation.img()
        if self.rect.colliderect(player.rect) and self.animation.frame == 4:
            player.health -= 1
            print("Ouch!")
