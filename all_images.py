import pygame
from animation import Animation

BASE = "images/"


def load_images(path, start, end, size):
    result = []
    for i in range(start, end + 1):
        result.append(
            pygame.transform.scale(pygame.image.load(f"{BASE+path}{i}.png"), size)
        )
    return result


assets = {
    "entity/walk": Animation(load_images("Knight-", 1, 3, (50, 43)), 6),
    "entity/attack": Animation(load_images("Knight_attack", 1, 4, (50, 43)), 15),
    "player/idle": Animation(load_images("idle", 1, 4, (40, 44)), 8),
    "player/walk": Animation(load_images("player_walk", 1, 4, (40, 44)), 10),
    "shooter/idle": Animation(load_images("gazlighter_idle", 1, 6, (40, 55)), 6),
    "shooter/walk": Animation(load_images("gazlighter_walk", 1, 6, (40, 55)), 6),
    "shotgun": pygame.image.load(BASE + "shotgun.png"),
    "rifle": pygame.image.load(BASE + "gun.png"),
    "pistol": pygame.image.load(BASE + "pistol.png"),
    "spikes": Animation(load_images("spike_", 0, 4, (25, 26)), 30),
    "coin/gold": Animation(load_images("Coin", 1, 6, (10, 10)), 4),
    "coin/silver": Animation(load_images("Coin_silver", 1, 6, (10, 10)), 4),
    "coin/bronze": Animation(load_images("Coin_bronze", 1, 6, (10, 10)), 4),
    "Revo": Animation(load_images("Revo", 1, 19, (500, 500)), 4),
    "shooter/game": Animation(load_images("gazlighter_idle", 1, 6, (400, 552)), 2),
}

