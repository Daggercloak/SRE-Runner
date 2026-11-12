import random
import sys

import pygame


# --------------------------------------------------
# Configuration
# --------------------------------------------------

WIDTH = 900
HEIGHT = 400

GROUND_Y = 320

FPS = 60

GRAVITY = 1
JUMP_STRENGTH = -18

STARTING_SPEED = 7
MAX_SPEED = 16


# --------------------------------------------------
# Colors
# --------------------------------------------------

BACKGROUND = (245, 245, 245)
GROUND = (45, 45, 45)

PLAYER_COLOR = (0, 120, 215)
OBSTACLE_COLOR = (220, 60, 60)

TEXT_COLOR = (40, 40, 40)
GAME_OVER_COLOR = (200, 40, 40)


# --------------------------------------------------
# Initialization
# --------------------------------------------------

pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))

pygame.display.set_caption(
    "SRE Runner"
)

clock = pygame.time.Clock()

font = pygame.font.Font(None, 32)
large_font = pygame.font.Font(None, 72)


# --------------------------------------------------
# Player
# --------------------------------------------------

player = pygame.Rect(
    100,
    GROUND_Y - 50,
    42,
    50
)

player_velocity_y = 0

on_ground = True


# --------------------------------------------------
# Obstacle
# --------------------------------------------------

obstacle = pygame.Rect(
    WIDTH,
    GROUND_Y - 45,
    35,
    45
)


# --------------------------------------------------
# Game state
# --------------------------------------------------

score = 0
high_score = 0

game_over = False

obstacle_speed = STARTING_SPEED


# --------------------------------------------------
# Functions
# --------------------------------------------------

def reset_obstacle():

    obstacle.x = (
        WIDTH + random.randint(200, 600)
    )

    obstacle.height = random.randint(35, 65)

    obstacle.y = (
        GROUND_Y - obstacle.height
    )


def reset_game():

    global score
    global game_over
    global player_velocity_y
    global on_ground
    global obstacle_speed

    player.x = 100
    player.y = GROUND_Y - player.height

    player_velocity_y = 0

    on_ground = True

    score = 0

    obstacle_speed = STARTING_SPEED

    game_over = False

    reset_obstacle()


def draw_text(text, font_object, color, x, y):

    surface = font_object.render(
        text,
        True,
        color
    )

    screen.blit(
        surface,
        (x, y)
    )


# --------------------------------------------------
# Start game
# --------------------------------------------------

reset_obstacle()


# --------------------------------------------------
# Main loop
# --------------------------------------------------

running = True

while running:

    # ----------------------------------------------
    # Events
    # ----------------------------------------------

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:

            if (
                event.key == pygame.K_SPACE
                and on_ground
                and not game_over
            ):

                player_velocity_y = JUMP_STRENGTH
                on_ground = False

            if (
                event.key == pygame.K_r
                and game_over
            ):

                reset_game()


    # ----------------------------------------------
    # Game update
    # ----------------------------------------------

    if not game_over:

        # Gravity

        player_velocity_y += GRAVITY
        player.y += player_velocity_y


        # Ground collision

        if player.bottom >= GROUND_Y:

            player.bottom = GROUND_Y

            player_velocity_y = 0
            on_ground = True


        # Move obstacle

        obstacle.x -= obstacle_speed


        # Passed obstacle

        if obstacle.right < 0:

            reset_obstacle()


        # Collision detection

        if player.colliderect(obstacle):

            game_over = True

            high_score = max(
                high_score,
                score
            )


        # Increase score

        score += 1


        # Increase difficulty

        obstacle_speed = min(
            STARTING_SPEED + score // 500,
            MAX_SPEED
        )


    # ----------------------------------------------
    # Draw
    # ----------------------------------------------

    screen.fill(BACKGROUND)


    # Ground

    pygame.draw.line(
        screen,
        GROUND,
        (0, GROUND_Y),
        (WIDTH, GROUND_Y),
        3
    )


    # Player

    pygame.draw.rect(
        screen,
        PLAYER_COLOR,
        player,
        border_radius=6
    )


    # Player eye

    pygame.draw.circle(
        screen,
        (255, 255, 255),
        (player.right - 10, player.top + 12),
        4
    )


    # Obstacle

    pygame.draw.rect(
        screen,
        OBSTACLE_COLOR,
        obstacle,
        border_radius=4
    )


    # ----------------------------------------------
    # HUD
    # ----------------------------------------------

    draw_text(
        f"Score: {score}",
        font,
        TEXT_COLOR,
        20,
        20
    )

    draw_text(
        f"High Score: {high_score}",
        font,
        TEXT_COLOR,
        20,
        55
    )

    draw_text(
        f"Speed: {obstacle_speed}",
        font,
        TEXT_COLOR,
        720,
        20
    )


    # ----------------------------------------------
    # Game over
    # ----------------------------------------------

    if game_over:

        draw_text(
            "GAME OVER",
            large_font,
            GAME_OVER_COLOR,
            285,
            110
        )

        draw_text(
            f"Score: {score}",
            font,
            TEXT_COLOR,
            390,
            190
        )

        draw_text(
            "Press R to restart",
            font,
            TEXT_COLOR,
            340,
            230
        )


    # ----------------------------------------------
    # Refresh display
    # ----------------------------------------------

    pygame.display.flip()

    clock.tick(FPS)


# --------------------------------------------------
# Shutdown
# --------------------------------------------------

pygame.quit()
sys.exit()