import pygame
import random
import sys
import os
import logging
import argparse

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
BACKGROUND_MUSIC_PATH = os.path.join(ASSETS_DIR, "lady_of_the_80's.mp3")
GAME_OVER_MUSIC_PATH = os.path.join(ASSETS_DIR, "game-over.mp3")
FRUIT_EATEN_SOUND_PATH = os.path.join(ASSETS_DIR, "bite.mp3")
POWER_UP_DURATION = 10

pygame.init()

SCREEN_WIDTH = 900
SCREEN_HEIGHT = 700
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Snake CTF")

snake_head_normal = pygame.image.load(os.path.join(ASSETS_DIR, "head.png"))
snake_head_normal = pygame.transform.scale(snake_head_normal, (30, 30))
background = pygame.image.load(os.path.join(ASSETS_DIR, "background.jpg"))
background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))
fruit = pygame.image.load(os.path.join(ASSETS_DIR, "burger.png"))
fruit = pygame.transform.scale(fruit, (30, 30))
powerup_image = pygame.image.load(os.path.join(ASSETS_DIR, "milkshake.png"))
powerup_image = pygame.transform.scale(powerup_image, (30, 30))

pygame.mixer.music.load(BACKGROUND_MUSIC_PATH)
fruit_eaten_sound = pygame.mixer.Sound(FRUIT_EATEN_SOUND_PATH)
pygame.mixer.music.set_volume(0.1)

def play_background_music():
    pygame.mixer.music.play(-1)

def play_game_over_music():
    pygame.mixer.music.load(GAME_OVER_MUSIC_PATH)
    pygame.mixer.music.play()

class Snake:
    def __init__(self):
        self.position = [100, 50]
        self.body = [[100, 50], [90, 50], [80, 50]]
        self.direction = "RIGHT"
        self.change_direction = self.direction

    def change_direction_to(self, direction):
        if direction == "RIGHT" and not self.direction == "LEFT":
            self.direction = "RIGHT"
        if direction == "LEFT" and not self.direction == "RIGHT":
            self.direction = "LEFT"
        if direction == "UP" and not self.direction == "DOWN":
            self.direction = "UP"
        if direction == "DOWN" and not self.direction == "UP":
            self.direction = "DOWN"

    def move(self, food_pos):
        if self.direction == "RIGHT":
            self.position[0] += 10
        if self.direction == "LEFT":
            self.position[0] -= 10
        if self.direction == "UP":
            self.position[1] -= 10
        if self.direction == "DOWN":
            self.position[1] += 10

        if (
            self.position[0] >= SCREEN_WIDTH
            or self.position[0] < 0
            or self.position[1] >= SCREEN_HEIGHT
            or self.position[1] < 0
        ):
            return 1

        self.body.insert(0, list(self.position))
        if self.position == food_pos:
            return 2
        else:
            self.body.pop()
            return 0

    def check_collision(self):
        for block in self.body[1:]:
            if self.position == block:
                return 1
        return 0

    def get_head_position(self):
        return self.position

    def get_body(self):
        return self.body


class Food:
    def __init__(self):
        self.position = [0, 0]  
        self.is_food_on_screen = False

    def spawn_food(self):
        if not self.is_food_on_screen:
            score_area = (SCREEN_WIDTH - 200, 0, 200, 50) 
            timer_area = (0, 0, 200, 50)  
            avoid_areas = [score_area, timer_area]

            while True:
                x = random.randrange(1, (SCREEN_WIDTH // 10)) * 10
                y = random.randrange(1, (SCREEN_HEIGHT // 10)) * 10
                if not any(
                    area[0] <= x <= area[0] + area[2] and area[1] <= y <= area[1] + area[3]
                    for area in avoid_areas
                ):
                    break

            self.position = [x, y]
            self.is_food_on_screen = True

        return self.position

    def set_food_on_screen(self, choice):
        self.is_food_on_screen = choice


def format_time(seconds):
    minutes, seconds = divmod(seconds, 60)
    return "{:02}:{:02}".format(int(minutes), int(seconds))

def display_end_game_message(screen, score, fruit_collected):
    if fruit_collected > 50:
        font = pygame.font.SysFont("Arial", 30)
        message = font.render(r"FLAG{EnterYourStringHere!!}", True, (0, 255, 0))
        screen.blit(message, ((SCREEN_WIDTH - message.get_width()) // 2, 300))

def main(clock, FPS):
    global game_over, snake, food, score

    font = pygame.font.SysFont("Arial", 30)
    large_font = pygame.font.SysFont("Arial", 40)

    snake = Snake()
    food = Food()
    score = 0
    fruit_collected = 0

    play_background_music()

    power_up_spawned = False
    power_up_position = [150, 100]  

    start_time = pygame.time.get_ticks()

    while True:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and game_over:
                    game_over = False
                    score = 0
                    fruit_collected = 0
                    snake = Snake()
                    food = Food()
                    start_time = pygame.time.get_ticks()
                elif event.key == pygame.K_RIGHT:
                    snake.change_direction_to("RIGHT")
                elif event.key == pygame.K_LEFT:
                    snake.change_direction_to("LEFT")
                elif event.key == pygame.K_UP:
                    snake.change_direction_to("UP")
                elif event.key == pygame.K_DOWN:
                    snake.change_direction_to("DOWN")
        
        if not power_up_spawned:
            power_up_position = [
                random.randrange(1, (SCREEN_WIDTH // 10)) * 10,
                random.randrange(1, (SCREEN_HEIGHT // 10)) * 10,
            ]
            power_up_spawned = True

        screen.fill((0, 0, 0)) 
        screen.blit(powerup_image, power_up_position)

        food_pos = food.spawn_food()
        collision_status = snake.move(food_pos)

        for pos in snake.get_body():
            head_rect = snake_head_normal.get_rect(topleft=(pos[0], pos[1]))
            pygame.draw.rect(screen, (255, 255, 255), head_rect, 1)
            screen.blit(snake_head_normal, (pos[0], pos[1]))
            fruit_rect = fruit.get_rect(topleft=(food_pos[0], food_pos[1]))
            pygame.draw.rect(screen, (255, 255, 255), fruit_rect, 1)
            screen.blit(fruit, (food_pos[0], food_pos[1]))

        if collision_status == 1:
            game_over = True
        elif collision_status == 2:
            score += 1
            fruit_collected += 1
            food.set_food_on_screen(False)
            fruit_eaten_sound.play()

        screen.blit(background, (0, 0))

        for pos in snake.get_body():
            screen.blit(snake_head_normal, (pos[0], pos[1]))

        screen.blit(fruit, (food_pos[0], food_pos[1]))

        if snake.check_collision() == 1:
            game_over = True

        if game_over:
            pygame.mixer.music.stop()
            play_game_over_music()
            game_over_text = large_font.render("Game Over", True, (255, 0, 0))
            screen.blit(
                game_over_text, ((SCREEN_WIDTH - game_over_text.get_width()) // 2, 150)
            )

            score_text = font.render("Your Score: " + str(score), True, (255, 255, 255))
            screen.blit(score_text, ((SCREEN_WIDTH - score_text.get_width()) // 2, 200))

            instruction_text = font.render(
                "Press Space Bar to Play Again", True, (255, 255, 255)
            )
            screen.blit(
                instruction_text,
                ((SCREEN_WIDTH - instruction_text.get_width()) // 2, 250),
            )

            display_end_game_message(screen, score, fruit_collected)

        else:
            elapsed_time = pygame.time.get_ticks() - start_time
            timer_text = font.render("Time: " + format_time(elapsed_time // 1000), True, (255, 255, 255))
            screen.blit(timer_text, (SCREEN_WIDTH - timer_text.get_width() - 10, 10))

            score_text = font.render("Score: " + str(score), True, (255, 255, 255))
            screen.blit(score_text, (10, 10))

        pygame.display.flip()
        pygame.display.update()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Snake CTF game with debug mode")
    parser.add_argument("-d", "--debug", action="store_true", help="Enable debug mode")
    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
        logging.debug("Debug mode is enabled.")
    else:
        logging.basicConfig(level=logging.INFO)

    game_over = False
    clock = pygame.time.Clock()
    FPS = 20
    main(clock, FPS)
