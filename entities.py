import pygame
import math
import random
import time
from tilemap import Block
from all_images import assets
from guns import *


class Entity(pygame.sprite.Sprite):
    def __init__(self, x, y, speed):
        super().__init__()
        self.dx = x
        self.dy = y
        self.size = (50, 43)
        self.action = ""
        self.set_action("walk")
        self.image = self.animation.img()
        self.rect = self.image.get_rect(topleft=(x, y))
        self.col = self.image.get_rect(topleft=(x, y))
        self.health = 3
        self.speed = speed

    def is_colliding_player(self, player):
        return self.rect.colliderect(player.rect)

    def set_action(self, action):
        if action != self.action:
            self.action = action
            self.animation = assets[f"entity/{self.action}"].copy()

    def stand_still(self, player):
        self.dx = 0  # -= player.direction.x * player.speed * 2
        self.dy = 0  # -= player.direction.y * player.speed * 2

    def move_towards_center(self, center):
        angle = math.atan2(
            center.rect.y - self.rect.centery, center.rect.x - self.rect.centerx
        )
        self.dx = self.speed * math.cos(angle)
        self.dy = self.speed * math.sin(angle)

        if self.is_colliding_player(center):
            self.set_action("attack")
            self.dx = 0
            self.dy = 0

            if self.animation.frame == 4:
                center.health -= 1
        else:
            self.set_action("walk")

    def update(self, player):
        self.move_towards_center(player)
        self.rect.x += self.dx
        self.rect.y += self.dy
        self.animation.update()
        if player.rect.x < self.rect.x:
            self.image = pygame.transform.flip(self.animation.img(), True, False)
        else:
            self.image = self.animation.img()


class Shooter(pygame.sprite.Sprite):
    def __init__(self, x, y, speed):
        super().__init__()
        self.dx = x
        self.dy = y
        self.size = (40, 55)
        self.action = ""
        self.set_action("walk")
        self.image = self.animation.img()
        self.rect = self.image.get_rect(topleft=(x, y))
        self.col = self.image.get_rect(topleft=(x, y))
        if random.randint(0, 1) == 0:
            self.gun = ShotgunEnemy(
                (self.col.topleft[0] + 20, self.col.topleft[1] + 20)
            )
        else:
            self.gun = RifleEnemy(
                (self.col.topleft[0] + 20, self.col.topleft[1] + 20)
            )  
        self.health = 1
        self.speed = speed

        self.reload_time = 10
        self.last_shot_time = 0

    def set_action(self, action):
        if action != self.action:
            self.action = action
            self.animation = assets[f"shooter/{self.action}"].copy()
    
    def get_dist(self, player):
        return math.sqrt(
            (player.rect.x - self.rect.x) ** 2 + (player.rect.y - self.rect.y) ** 2
        )

    def move_towards_center(self, player, bullets):
        angle = math.atan2(
            player.rect.y - self.rect.centery, player.rect.x - self.rect.centerx
        )
        if hasattr(self, 'speed') and self.speed is not None:
            self.dx = self.speed * math.cos(angle)
            self.dy = self.speed * math.sin(angle)

            if self.get_dist(player) < 200:
                self.set_action("idle")
                current_time = time.time()
                if current_time - self.last_shot_time > self.gun.reload:
                    self.gun.shoot(self.col, player, bullets)
                    self.last_shot_time = current_time
                self.dx = 0
                self.dy = 0

            else:
                self.set_action("walk")

    def die(self, kill_count, health_pots):
        self.gun.kill()
        self.kill()
        if (kill_count % 30) == 0:
            health_pots.add(
                HealthPotion(
                    (self.col.x, self.col.y),
                    (50, 50),
                )
            )



    def update(self, player, bullets, display_surface):
        if hasattr(self, 'gun') and self.gun is not None:  # Check if gun exists
            self.gun.update((player.rect.x, player.rect.y), (self.rect.x, self.rect.y))

        # self.gun.update((player.rect.x, player.rect.y), (self.rect.x, self.rect.y))
        self.move_towards_center(player, bullets)
        self.rect.x += self.dx
        self.rect.y += self.dy
        # self.gun.update((player.rect.x, player.rect.y), (self.rect.x, self.rect.y))
        self.animation.update()
        if player.rect.x < self.rect.x:
            self.image = pygame.transform.flip(self.animation.img(), True, False)
        else:
            self.image = self.animation.img()



class PhysicsEntity(pygame.sprite.Sprite):
    def __init__(self, game, pos, size, group):
        super().__init__(group)
        self.game = game
        self.pos = list(pos)
        self.size = size
        self.health = 1000
        self.max_health = 1000
        self.old_x = 0
        self.old_y = 0
        self.action = ""
        self.set_action("idle")
        self.image = self.animation.img()
        self.rect = self.image.get_rect(center=pos)
        # self.col = self.image.get_rect(topleft=(pos[0] - 20, pos[1] - 22))
        self.col = pygame.Rect(pos[0] - 15, pos[1] - 22, size[0] - 10, size[1])
        self.direction = pygame.math.Vector2()
        self.speed = 3



    def is_colliding(self, block):
        if self.rect.colliderect(block.rect):
            left_overlap = self.rect.right - block.rect.left
            right_overlap = block.rect.right - self.rect.left
            top_overlap = self.rect.bottom - block.rect.top
            bottom_overlap = block.rect.bottom - self.rect.top

            # Determine side of collision
            min_overlap = min(left_overlap, right_overlap, top_overlap, bottom_overlap)
            if min_overlap == left_overlap:
                self.direction.x = 0
                self.rect.x = self.rect.x - self.speed
                print("Player collided with the left side of the wall!")
            elif min_overlap == right_overlap:
                self.direction.x = 0
                self.rect.x = self.rect.x + self.speed
                print("Player collided with the rightside of the wall!")
            elif min_overlap == top_overlap:
                self.direction.y = 0
                self.rect.y = self.rect.y - self.speed
                print("Player collided with the top side of the wall!")
            elif min_overlap == bottom_overlap:
                self.direction.y = 0
                self.rect.y = self.rect.y + self.speed
                print("Player collided with the bottom side of the wall!")
                return True

        return False

    def input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w] or keys[pygame.K_s] or keys[pygame.K_a] or keys[pygame.K_d]:
            self.set_action("walk")
        else:
            self.set_action("idle")
        if keys[pygame.K_w]:
            self.direction.y = -1
        elif keys[pygame.K_s]:
            
            self.direction.y = 1
        else:
            self.direction.y = 0

        if keys[pygame.K_d]:
            self.direction.x = 1
        elif keys[pygame.K_a]:
            self.direction.x = -1
        else:
            self.direction.x = 0

    def set_action(self, action):
        if action != self.action:
            self.action = action
            self.animation = assets[f"player/{self.action}"].copy()

    def update(self, mouse_pos, blocks):
        self.input()
        for block in blocks:

            self.is_colliding(block)

        self.rect.center += self.direction * self.speed
        self.animation.update()
        if mouse_pos[0] < self.pos[0]:

            self.image = pygame.transform.flip(self.animation.img(), True, False)
        else:
            self.image = self.animation.img()


class HealthPotion(pygame.sprite.Sprite):
    def __init__(self, pos, size):
        super().__init__()
        self.images = []
        for i in range(4, 23):
            self.images.append(
                pygame.transform.scale(
                    pygame.image.load(f"images/Sprite-{i}.png").convert_alpha(), size
                )
            )
        self.pos = list(pos)
        self.size = size
        self.rect = pygame.Rect(self.pos, self.size)
        self.image_index = 0  # Index of the current image in the animation
        self.animation_delay = 5  # Delay between animation frames
        self.animation_timer = 0  # Timer for animation

    def update(self, player):
        if self.rect.colliderect(player.col) and player.health < player.max_health:
            player.health += 1
            # print("HELL YEAH!")
            self.kill()
        elif self.rect.colliderect(player.col):
            # print("I'm full, I don't need this")
            self.kill()

    def move_towards_player(self, center):
        self.angle = math.atan2(
            center.pos[1] - self.rect.centery, center.pos[0] - self.rect.centerx
        )
        self.pos[0] = 6 * math.cos(self.angle)
        self.pos[1] = 6 * math.sin(self.angle)
        self.rect.move_ip(
            self.pos[0] - (center.direction.x * center.speed * 2),
            self.pos[1] - (center.direction.y * center.speed * 2),
        )

    def stand_still(self, player):
        self.pos[0] = 0
        self.pos[1] = 0
        self.rect.move_ip(
            self.pos[0] - (player.direction.x * player.speed * 2),
            self.pos[1] - (player.direction.y * player.speed * 2),
        )

    def render(self, display):
        self.animation_timer += 1
        if self.animation_timer >= self.animation_delay:
            self.animation_timer = 0
            self.image_index = (self.image_index + 1) % len(self.images)
        display.blit(self.images[self.image_index], self.rect.topleft)


class Coin(pygame.sprite.Sprite):
    def __init__(self, pos, group):
        super().__init__(group)
        rand = random.randint(0, 2)
        if rand == 0:
            self.animation = assets["coin/gold"].copy()
        elif rand == 1:
            self.animation = assets["coin/silver"].copy()
        else:
            self.animation = assets["coin/bronze"].copy()
        self.image = self.animation.img()
        self.pos = list(pos)
        self.rect = self.image.get_rect(topleft=pos)

    def move_towards_player(self, center):
        self.angle = math.atan2(
            center.pos[1] - self.rect.centery, center.pos[0] - self.rect.centerx
        )
        self.pos[0] = 9 * math.cos(self.angle)
        self.pos[1] = 9 * math.sin(self.angle)
        self.rect.move_ip(
            self.pos[0] - (center.direction.x * center.speed * 2),
            self.pos[1] - (center.direction.y * center.speed * 2),
        )

    def update(self, player, coins):
        self.move_towards_player(player)
        self.animation.update()
        self.image = self.animation.img()
        if self.rect.colliderect(player.col):
            self.kill()
            return 1
        return 0

    def render(self, display):
        display.blit(self.image, self.rect.topleft)
