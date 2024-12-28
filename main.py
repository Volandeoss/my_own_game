import pygame
import sys
import time
import random
from entities import *
from camera import CameraGroup
from guns import *
from scipy.ndimage import gaussian_filter
import numpy as np
from tilemap import Floor, Spikes
import threading


pygame.init()

WIDTH = 600  # 1366
HEIGHT = 600  # 750
# Set up the drawing window
screen = pygame.display.set_mode((WIDTH, HEIGHT))


def display_kill_count(kill_count):
    font = pygame.font.SysFont(None, 36)
    text = font.render(f"Kills: {kill_count}", True, (255, 100, 0))
    text_rect = text.get_rect()
    text_rect.topright = (WIDTH - 10, 10)
    screen.blit(text, text_rect)


def display_coins(amount_coins):
    font = pygame.font.SysFont(None, 36)
    text = font.render(f":{amount_coins}", True, (0, 0, 0))
    text_rect = text.get_rect()
    text_rect.topright = (WIDTH - 200, 10)
    screen.blit(
        pygame.transform.scale(pygame.image.load("images/Coin2.png"), (20, 20)),
        text_rect,
    )
    screen.blit(
        text,
        (text_rect[0] + 30, text_rect[1]),
    )


def display_player_pos(player):
    font = pygame.font.SysFont(None, 36)
    text = font.render(f"Pos: {player.rect.x},{player.rect.y}", True, (169, 168, 141))
    text_rect = text.get_rect()
    text_rect.topright = (140, 30)
    screen.blit(text, text_rect)


def display_health(player):
    font = pygame.font.SysFont(None, 36)
    text = font.render(f"{player.health}/{player.max_health}", True, (255, 100, 0))

    # Define a fixed width for the health bar
    max_health_width = 200

    # Calculate the width of the health bar based on the player's health percentage
    health_width = max_health_width * (player.health / player.max_health)

    # Draw the health bar background
    pygame.draw.rect(screen, (1, 1, 1), (10, 10, max_health_width, 20))

    # Draw the health bar with the calculated width
    pygame.draw.rect(screen, (255, 0, 0), (10, 10, health_width, 20))

    # Render and display the health text
    text_rect = text.get_rect()
    text_rect.topleft = (10, 40)
    screen.blit(text, text_rect)


def game_over(is_game):


    custom_cursor = pygame.image.load("images/cursor.png").convert_alpha()
    pygame.mouse.set_visible(False)
    cursor_img_rect = custom_cursor.get_rect()
    custom_cursor.set_colorkey((104, 75, 45))
    gaz = assets["shooter/game"].copy()
    # screen.blit(custom_cursor, cursor_img_rect)

    font = pygame.font.SysFont(None, 50)
    game_over_text = font.render("Game Over", True, (255, 0, 0))
    game_over_text_rect = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    restart_text = font.render("Restart", True, (255, 0, 0))
    restart_text_rect = restart_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))

    while True:
        gaz.update()
        screen.fill((0, 0, 0))  # Fill the screen with black
        screen.blit(gaz.img(), (50, 50))
        screen.blit(game_over_text, game_over_text_rect)  # Display "Game Over" message
        screen.blit(restart_text, restart_text_rect)  # Display "Restart" button
        cursor_img_rect = custom_cursor.get_rect(center=pygame.mouse.get_pos())
        screen.blit(custom_cursor, cursor_img_rect)
        pygame.display.flip()  # Update the display

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    if restart_text_rect.collidepoint(
                        event.pos
                    ):  # Check if mouse clicked on "Restart" button
                        is_game = True
                        return  # Exit the game_over function and restart the game


def menu():
    # custom_cursor = pygame.image.load("images/cursor.png").convert_alpha()
    # pygame.mouse.set_visible(False)
    # cursor_img_rect = custom_cursor.get_rect()
    # custom_cursor.set_colorkey((104, 75, 45))
    revo = assets["Revo"].copy()
    while True:

        revo.update()
        # image = revo.img()

        screen.blit(pygame.image.load("images/menu.png"), (0, 0))
        screen.blit(revo.img(), (50, 50))
        play_button_rect = pygame.Rect(
            250, 300, 100, 50
        )  # Define the "Play" button rect
        pygame.draw.rect(
            screen, (255, 255, 255), play_button_rect, 2
        )  # Draw button outline

        # Display text on the button
        font = pygame.font.SysFont(None, 30)
        text = font.render("Play", True, (255, 255, 255))
        text_rect = text.get_rect(center=play_button_rect.center)
        screen.blit(text, text_rect)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    if play_button_rect.collidepoint(
                        event.pos
                    ):  # Check if mouse clicked on button
                        return  # Exit the menu function and start the game
        # screen.blit(custom_cursor, cursor_img_rect)


TRANSPARENT_BLACK = (0, 0, 0, 128)  # Чорний колір з прозорістю 50%


def blur_surface(surface, radius):
    arr = pygame.surfarray.pixels3d(surface)
    blurred_arr = np.empty_like(arr)
    for i in range(3):
        blurred_arr[:, :, i] = gaussian_filter(arr[:, :, i], sigma=radius)
    return pygame.surfarray.make_surface(blurred_arr)


# Set up blur radius
blur_radius = 5


def darken_screen():
    darken_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    darken_surface.fill(TRANSPARENT_BLACK)
    screen.blit(darken_surface, (0, 0))


entities = pygame.sprite.Group()
shooters = pygame.sprite.Group()
healt_pots = pygame.sprite.Group()
bullets = pygame.sprite.Group()
blocks = pygame.sprite.Group()
entitybullets = pygame.sprite.Group()
spikes = pygame.sprite.Group()
coins = pygame.sprite.Group()


def spawn_coins(
    x,
    y,
):
    if random.random() < 0.5:
        coins.add(Coin((x, y), coins))


def spawn_entities_threaded(is_game, player, amount_entities, phase):
    def spawn_entities_worker(is_game, player, amount_entities, phase):
        randik = random.random()
        probability = 0
        if phase == 2:
            probability = 0.2

        if (
            randik < 0.5 + probability and is_game and amount_entities < 70
        ):  # Adjust this probability to control the spawn rate
            random_speed = random.uniform(2, 4)
            randx = random.randint(-1232, 1174)
            randy = random.randint(-700, 656)
            while (
                randx > player.rect.x - 300
                and randx < player.rect.x + 300
                or randy > player.rect.y - 300
                and randy < player.rect.y + 300
            ):
                randx = random.randint(-1232, 1174)
                randy = random.randint(-700, 656)
            if randik < 0.01:
                print(f"{randx, randy, random_speed}")
                shooters.add(
                    Shooter(randx, randy, random_speed, shooters)
                )
                amount_entities += 1
            elif randik < 0.05:
                entities.add(
                    Entity(randx, randy, random_speed)
                )
                amount_entities += 1



    # Create a thread to run the spawning worker function
    spawn_thread = threading.Thread(target=spawn_entities_worker, args=(is_game, player, amount_entities, phase))
    spawn_thread.start()

def spawn_entities(is_game, player, amount_entities, phase):
    randik = random.random()
    probability = 0
    if phase == 2:
        probability = 0.2

    if (
        randik < 0.5 + probability and is_game and amount_entities < 70
    ):  # Adjust this probability to control the spawn rate
        random_speed = random.uniform(2, 4)
        randx = random.randint(-1232, 1174)
        randy = random.randint(-700, 656)
        while (
            randx > player.rect.x - 300
            and randx < player.rect.x + 300
            or randy > player.rect.y - 300
            and randy < player.rect.y + 300
        ):
            randx = random.randint(-1232, 1174)
            randy = random.randint(-700, 656)
        if randik < 0.01:
            shooters.add(
                Shooter(randx, randy, random_speed, shooters),
            )
            amount_entities += 1
        elif randik < 0.05:
            
            entities.add(
                Entity(
                    randx,
                    randy,
                    random_speed,
                ),
            )
            amount_entities += 1


def game():
    pygame.display.set_caption("Не для клаустрофобів")
    custom_cursor = pygame.image.load("images/cursor.png").convert_alpha()
    pygame.mouse.set_visible(False)
    cursor_img_rect = custom_cursor.get_rect()
    custom_cursor.set_colorkey((104, 75, 45))
    screen.blit(custom_cursor, cursor_img_rect)

    clock = pygame.time.Clock()

    camera_group = CameraGroup(entities, shooters, entitybullets, spikes)

    for i in range(49):
        for j in range(28):
            random_number = random.randint(1, 8)
            random_spike = random.random()
            Floor(
                f"images/floor{random_number}.png",
                (-1233 + (i * 50), -700 + (j * 50)),
                camera_group,
            )
            if random_spike < 0.1:
                Spikes((-1233 + (i * 50), -700 + (j * 50)), spikes)

    player = PhysicsEntity(screen, (WIDTH // 2, HEIGHT // 2), (40, 44), camera_group)

    gun = Pistol((player.col.x, player.col.y))
    # gun = Shotgun((player.rect.x, player.rect.y))

    for i in range(25):
        # down
        blocks.add(Block((1117 - (i * 100), 700), 1, camera_group))
        # up
        blocks.add(Block((-1235 + (i * 100), -725), 0, camera_group))
    for i in range(14):
        # left
        blocks.add(Block((-1259, -700 + (i * 100)), 2, camera_group))
        # right
        blocks.add(Block((1215, -700 + (i * 100)), 3, camera_group))

    is_game = True
    is_shooting = False
    running = True

    phase = 1
    amount_entities = 0
    amount_coins = 0
    last_shot_time = 0  # Time of the last shots
    kill_count = 0

    while running:
        screen.fill((0, 0, 0))
        cursor_position = pygame.mouse.get_pos()
        camera_group.update(cursor_position, blocks)
        camera_group.custom_draw(player)
        if player.health <= 0:
            kill_count = 0
            amount_coins = 0
            phase = 1
            # screen.fill((150, 0, 0))
            # is_game = False
            entities.empty()
            bullets.empty()
            shooters.empty()
            healt_pots.empty()
            entitybullets.empty()
            game_over(is_game)
            gun = Pistol((player.col.x, player.col.y))
            player.health = player.max_health

        current_time = pygame.time.get_ticks()

        # pygame.draw.aaline(
        #     screen,
        #     (0, 0, 0),
        #     cursor_position,
        #     (player.col.centerx, player.col.centery),
        # )

        cursor_img_rect.center = pygame.mouse.get_pos()  # update position

        screen.blit(custom_cursor, cursor_img_rect)  # draw the cursor

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and is_game:
                    is_shooting = True
                elif not is_game:
                    is_shooting = False
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    is_shooting = False

        if amount_coins == 5 and phase == 1:
            gun = Shotgun((player.col.x, player.col.y))
            amount_coins = 0
            phase += 1
            amount_entities += 30
        elif amount_coins == 200 and phase == 2:
            gun = Gun((player.col.x, player.col.y))
            phase += 1
            amount_entities += 30
            amount_coins = 0

        # spawn_entities(is_game, player, amount_entities, phase)
        spawn_entities_threaded(is_game, player, amount_entities, phase)

        
        current_time = time.time()
        if is_shooting and current_time - last_shot_time > gun.reload:
            gun.shoot(cursor_position, bullets)
            last_shot_time = current_time


       

        for bullet in entitybullets:

            bullet.update(player)
            screen.blit(bullet.image, bullet.rect.topleft)
            if bullet.rect.colliderect(player.col):
                player.health -= 1
                entitybullets.remove(bullet)
            if (
                bullet.rect.x > 1200
                or bullet.rect.x < -1200
                or bullet.rect.y > 590
                or bullet.rect.y < -700
            ):
                entitybullets.remove(bullet)

        for pot in healt_pots:
            pot.update(player)
            pot.render(screen)
            # pot.move_towards_player(player)
            pot.stand_still(player)
        # print(amount_coins)
        for coin in coins:
            amount_coins += coin.update(player, amount_coins)
            # print(amount_coins)
            coin.render(screen)

            # if coin.col.colliderect(player.col):
            #     coins.remove(coin)

        for spike in spikes:
            spike.update(player)

        for shooter in shooters:
            shooter.update(player, entitybullets)
            for bullet in bullets:
                if shooter.col.colliderect(bullet.rect):
                    kill_count += 1
                    spawn_coins(shooter.col.x, shooter.col.y)
                    bullets.remove(bullet)
                    shooter.die(kill_count, healt_pots)

        for entity in entities:
            entity.update(player)
            # pygame.draw.rect(screen, (255, 0, 0), ((entity.rect.topleft), entity.rect.size))
            for bullet in bullets:
                if entity.col.colliderect(bullet.rect):
                    amount_entities -= 1
                    spawn_coins(entity.col.x, entity.col.y)
                    bullets.remove(bullet)
                    kill_count += 1
                    if (kill_count % 30) == 0:
                        healt_pots.add(
                            HealthPotion(
                                (entity.col.x, entity.col.y),
                                (50, 50),
                            )
                        )
                    entities.remove(entity)
                if not bullet.rect.colliderect(pygame.Rect(0, 0, WIDTH, HEIGHT)):
                    bullets.remove(bullet)

        bullets.update(player)
        for bullet in bullets:
            screen.blit(bullet.image, bullet.rect.topleft)

        player.update(cursor_position, blocks)

        display_kill_count(kill_count)
        display_coins(amount_coins)
        gun.update(cursor_position, (player.col.x, player.col.y))
        if player.pos[0] > cursor_position[0] and is_game:
            screen.blit(
                pygame.transform.flip(gun.image, True, False),
                gun.rect.topleft,
            )
        elif is_game:
            screen.blit(gun.image, gun.rect.topleft)
        display_health(player)
        # display_player_pos(player)
        # darken_screen()
        # blur_surface(screen, blur_radius)
        # blurred_image = blur_surface(image, blur_radius)
        # screen.blit(blurred_image, (0, 0))
        pygame.display.flip()

        clock.tick(60)


def start_game():
    menu()
    game()


start_game()
