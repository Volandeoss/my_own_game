import threading
import random
from entities import *




def spawn_entities_threaded(is_game, player, amount_entities, phase, shooters, entities):
    def spawn_entities_worker(is_game, player, amount_entities, phase):
        randik = random.random()
        probability = 0
        if phase == 2:
            probability = 0.2

        if (
            randik < 0.5 + probability and is_game and amount_entities < 70
        ):  # Adjust this probability to control the spawn rate
            random_speed = random.uniform(2, 4)
            randx = random.randint(-1230, 1173)
            randy = random.randint(-700, 650)
            while (
                randx > player.rect.x - 300
                and randx < player.rect.x + 300
                or randy > player.rect.y - 300
                and randy < player.rect.y + 300
            ):
                randx = random.randint(-1230, 1173)
                randy = random.randint(-700, 650)
            if randik < 0.01:
                shooters.add(
                    Shooter(randx, randy, random_speed)
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


