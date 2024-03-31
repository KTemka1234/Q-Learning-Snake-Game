import math
import pygame
import random
from enum import Enum
from collections import namedtuple
import numpy as np

pygame.init()
font = pygame.font.Font('arial.ttf', 25)


class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4


Point = namedtuple('Point', 'x, y')

BACKGROUND_COLOR = (175, 215, 70)
GRASS_COLOR = (167, 209, 61)
FONT_COLOR = (56, 74, 12)

BLOCK_SIZE = 40
SPEED = 1000

COLLISION_REWARD = -100
FOOD_REWARD = 10
STEP_TO_FOOD_REWARD = 1
STEP_FROM_FOOD_REWARD = -2


class SnakeGameAI:
    def __init__(self, w=800, h=800):
        self.w = w
        self.h = h
        # init display
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption('Snake')
        self.clock = pygame.time.Clock()

        # init game state
        self.direction = Direction.RIGHT
        self.head = Point(self.w / 2, self.h / 2)
        self.snake = [self.head,
                      Point(self.head.x - BLOCK_SIZE, self.head.y),
                      Point(self.head.x - (2 * BLOCK_SIZE), self.head.y)]
        self.last_head_position = self.head

        self.score = 0

        self.apple = pygame.image.load("resources/apple.png").convert_alpha()
        self.food = None
        self._place_food()
        self.frame_iteration = 0

        def load_image(name):
            return pygame.image.load(f"resources/snake/{name}.png").convert_alpha()

        self.graphics = {"head": {}, "tail": {}, "body": {}}
        self.graphics["head"][(0, -BLOCK_SIZE)] = load_image("head_up")
        self.graphics["head"][(0, BLOCK_SIZE)] = load_image("head_down")
        self.graphics["head"][(BLOCK_SIZE, 0)] = load_image("head_right")
        self.graphics["head"][(-BLOCK_SIZE, 0)] = load_image("head_left")

        self.graphics["tail"][(0, -BLOCK_SIZE)] = load_image("tail_up")
        self.graphics["tail"][(0, BLOCK_SIZE)] = load_image("tail_down")
        self.graphics["tail"][(BLOCK_SIZE, 0)] = load_image("tail_right")
        self.graphics["tail"][(-BLOCK_SIZE, 0)] = load_image("tail_left")

        self.graphics["body"][(0, -BLOCK_SIZE)] = load_image("body_vertical")
        self.graphics["body"][(0, BLOCK_SIZE)] = load_image("body_vertical")
        self.graphics["body"][(BLOCK_SIZE, 0)] = load_image("body_horizontal")
        self.graphics["body"][(-BLOCK_SIZE, 0)] = load_image("body_horizontal")
        self.graphics["body"][(BLOCK_SIZE, -BLOCK_SIZE)] = load_image("body_tr")
        self.graphics["body"][(-BLOCK_SIZE, -BLOCK_SIZE)] = load_image("body_tl")
        self.graphics["body"][(BLOCK_SIZE, BLOCK_SIZE)] = load_image("body_br")
        self.graphics["body"][(-BLOCK_SIZE, BLOCK_SIZE)] = load_image("body_bl")

    def reset(self):
        # init game state
        self.direction = Direction.RIGHT

        self.head = Point(self.w / 2, self.h / 2)
        self.snake = [self.head,
                      Point(self.head.x - BLOCK_SIZE, self.head.y),
                      Point(self.head.x - (2 * BLOCK_SIZE), self.head.y)]
        self.last_head_position = self.head

        self.score = 0
        self.food = None
        self._place_food()
        self.frame_iteration = 0

    def _place_food(self):
        x = random.randint(0, (self.w - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
        y = random.randint(0, (self.h - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
        self.food = Point(x, y)
        if self.food in self.snake:
            self._place_food()

    def play_step(self, action):
        self.frame_iteration += 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        self._move(action)  # update the head
        self.snake.insert(0, self.head)

        reward = 0
        game_over = False
        if self.is_collision() or self.frame_iteration > 100 * len(self.snake):
            game_over = True
            reward += COLLISION_REWARD
            return reward, game_over, self.score

        prev_dist_to_food = math.sqrt((self.food.x - self.last_head_position.x)**2 +
                                      (self.food.y - self.last_head_position.y)**2)
        new_dist_to_food = math.sqrt((self.food.x - self.head.x)**2 +
                                     (self.food.y - self.head.y)**2)
        if new_dist_to_food < prev_dist_to_food:
            reward += STEP_TO_FOOD_REWARD
        else:
            reward += STEP_FROM_FOOD_REWARD

        if self.head == self.food:
            self.score += 1
            reward += FOOD_REWARD
            self._place_food()
        else:
            self.snake.pop()

        self._update_ui()
        self.clock.tick(SPEED)
        return reward, game_over, self.score

    def is_collision(self, pt=None):
        if pt is None:
            pt = self.head
        # hits boundary
        if pt.x > self.w - BLOCK_SIZE or pt.x < 0 or pt.y > self.h - BLOCK_SIZE or pt.y < 0:
            return True
        # hits itself
        if pt in self.snake[1:]:
            return True

        return False

    def _update_ui(self):
        self.display.fill(BACKGROUND_COLOR)
        self._draw_grass()
        self._draw_snake()
        self._draw_food()
        self._draw_score()
        pygame.display.flip()

    def _draw_grass(self):
        for row in range(self.h // BLOCK_SIZE):
            if row % 2 == 0:
                for col in range(self.w // BLOCK_SIZE):
                    if col % 2 == 0:
                        grass_rect = pygame.Rect(col * BLOCK_SIZE, row * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
                        pygame.draw.rect(self.display, GRASS_COLOR, grass_rect)
            else:
                for col in range(self.w // BLOCK_SIZE):
                    if col % 2 != 0:
                        grass_rect = pygame.Rect(col * BLOCK_SIZE, row * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
                        pygame.draw.rect(self.display, GRASS_COLOR, grass_rect)

    def _draw_food(self):
        fruit_rect = pygame.Rect(self.food.x, self.food.y, BLOCK_SIZE, BLOCK_SIZE)
        self.display.blit(self.apple, fruit_rect)

    def _draw_score(self):
        score_text = str(len(self.snake) - 3)
        score_surface = font.render(score_text, True, FONT_COLOR)
        score_x = int(self.w - 60)
        score_y = int(self.h - 40)
        score_rect = score_surface.get_rect(center=(score_x, score_y))
        apple_rect = self.apple.get_rect(midright=(score_rect.left, score_rect.centery))
        bg_rect = pygame.Rect(apple_rect.left, apple_rect.top, apple_rect.width + score_rect.width + 6,
                              apple_rect.height)

        pygame.draw.rect(self.display, GRASS_COLOR, bg_rect)
        self.display.blit(score_surface, score_rect)
        self.display.blit(self.apple, apple_rect)
        pygame.draw.rect(self.display, FONT_COLOR, bg_rect, 2)

    def _draw_snake(self):
        for index, block in enumerate(self.snake):
            block_rect = pygame.Rect(block.x, block.y, BLOCK_SIZE, BLOCK_SIZE)
            if index == 0:
                body_part = "head"
                snake_direction = (self.snake[0].x - self.snake[1].x, self.snake[0].y - self.snake[1].y)
            elif index == len(self.snake) - 1:
                body_part = "tail"
                snake_direction = (self.snake[-1].x - self.snake[-2].x, self.snake[-1].y - self.snake[-2].y)
            else:
                body_part = "body"
                previous_block = (self.snake[index + 1].x - block.x, self.snake[index + 1].y - block.y)
                next_block = (self.snake[index - 1].x - block.x, self.snake[index - 1].y - block.y)
                if previous_block[0] == next_block[0]:
                    snake_direction = (0, BLOCK_SIZE)
                elif previous_block[1] == next_block[1]:
                    snake_direction = (BLOCK_SIZE, 0)
                else:
                    snake_direction = (previous_block[0] + next_block[0], previous_block[1] + next_block[1])
            self.display.blit(self.graphics[body_part][tuple(snake_direction)], block_rect)

    def _move(self, action):
        # [straight, right, left]

        clock_wise = [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP]
        idx = clock_wise.index(self.direction)

        if np.array_equal(action, [1, 0, 0]):
            new_dir = clock_wise[idx]  # no change
        elif np.array_equal(action, [0, 1, 0]):
            next_idx = (idx + 1) % 4
            new_dir = clock_wise[next_idx]  # right turn r -> d -> l -> u
        else:  # [0, 0, 1]
            next_idx = (idx - 1) % 4
            new_dir = clock_wise[next_idx]  # left turn r -> u -> l -> d

        self.direction = new_dir

        x = self.head.x
        y = self.head.y
        if self.direction == Direction.RIGHT:
            x += BLOCK_SIZE
        elif self.direction == Direction.LEFT:
            x -= BLOCK_SIZE
        elif self.direction == Direction.DOWN:
            y += BLOCK_SIZE
        elif self.direction == Direction.UP:
            y -= BLOCK_SIZE

        self.head = Point(x, y)
