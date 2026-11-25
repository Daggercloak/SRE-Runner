import random
import sys

import pygame
from opentelemetry.trace import Status, StatusCode

from metrics import (
    collisions,
    current_score,
    current_speed,
    game_active,
    games_started,
    obstacles_avoided,
    start_metrics_server,
)

from telemetry import (
    logger,
    shutdown_telemetry,
    tracer,
)


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

GROUND_OBSTACLE = "ground"
FLYING_OBSTACLE = "flying"


# --------------------------------------------------
# Colors
# --------------------------------------------------

BACKGROUND = (245, 245, 245)
GROUND = (45, 45, 45)

PLAYER_COLOR = (0, 120, 215)
GROUND_OBSTACLE_COLOR = (220, 60, 60)
FLYING_OBSTACLE_COLOR = (150, 60, 200)

TEXT_COLOR = (40, 40, 40)
GAME_OVER_COLOR = (200, 40, 40)


# --------------------------------------------------
# Initialization
# --------------------------------------------------

pygame.init()

start_metrics_server(port=9090)

screen = pygame.display.set_mode(
    (WIDTH, HEIGHT)
)

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
    50,
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
    45,
)

obstacle_type = GROUND_OBSTACLE


# --------------------------------------------------
# Game state
# --------------------------------------------------

score = 0
high_score = 0

game_over = False

obstacle_speed = STARTING_SPEED


# --------------------------------------------------
# OpenTelemetry helpers
# --------------------------------------------------

def trace_game_started(event_name):
    with tracer.start_as_current_span(event_name) as span:
        span.set_attribute(
            "game.score",
            score,
        )

        span.set_attribute(
            "game.high_score",
            high_score,
        )

        span.set_attribute(
            "game.speed",
            obstacle_speed,
        )

        span.set_attribute(
            "game.active",
            True,
        )


def trace_obstacle_spawned():
    with tracer.start_as_current_span(
        "obstacle.spawn"
    ) as span:

        span.set_attribute(
            "obstacle.type",
            obstacle_type,
        )

        span.set_attribute(
            "obstacle.width",
            obstacle.width,
        )

        span.set_attribute(
            "obstacle.height",
            obstacle.height,
        )

        span.set_attribute(
            "obstacle.x",
            obstacle.x,
        )

        span.set_attribute(
            "obstacle.y",
            obstacle.y,
        )

        span.set_attribute(
            "game.score",
            score,
        )

        span.set_attribute(
            "game.speed",
            obstacle_speed,
        )


def trace_obstacle_avoided():
    with tracer.start_as_current_span(
        "obstacle.avoided"
    ) as span:

        span.set_attribute(
            "obstacle.type",
            obstacle_type,
        )

        span.set_attribute(
            "game.score",
            score,
        )

        span.set_attribute(
            "game.speed",
            obstacle_speed,
        )


def trace_collision():
    with tracer.start_as_current_span(
        "collision"
    ) as span:

        span.set_attribute(
            "obstacle.type",
            obstacle_type,
        )

        span.set_attribute(
            "game.score",
            score,
        )

        span.set_attribute(
            "game.speed",
            obstacle_speed,
        )

        span.set_attribute(
            "game.high_score",
            max(
                high_score,
                score,
            ),
        )

        span.set_status(
            Status(
                StatusCode.ERROR,
                "Player collided with obstacle",
            )
        )


def trace_player_jump():
    with tracer.start_as_current_span(
        "player.jump"
    ) as span:

        span.set_attribute(
            "game.score",
            score,
        )

        span.set_attribute(
            "game.speed",
            obstacle_speed,
        )

        span.set_attribute(
            "player.velocity_y",
            JUMP_STRENGTH,
        )


# --------------------------------------------------
# Game functions
# --------------------------------------------------

def reset_obstacle():
    global obstacle_type

    obstacle.x = WIDTH + random.randint(
        250,
        600,
    )

    # Only ground obstacles at the beginning.
    if score < 1000:

        obstacle_type = GROUND_OBSTACLE

    else:

        # After score 1000, flying obstacles may appear.
        obstacle_type = random.choices(
            [
                GROUND_OBSTACLE,
                FLYING_OBSTACLE,
            ],
            weights=[
                70,
                30,
            ],
            k=1,
        )[0]

    if obstacle_type == GROUND_OBSTACLE:

        obstacle.width = random.randint(
            30,
            45,
        )

        obstacle.height = random.randint(
            35,
            65,
        )

        obstacle.y = (
            GROUND_Y
            - obstacle.height
        )

    else:

        obstacle.width = 55
        obstacle.height = 30

        obstacle.y = (
            GROUND_Y
            - 105
        )

    # OpenTelemetry trace
    trace_obstacle_spawned()

    # OpenTelemetry log
    logger.info(
        "Obstacle spawned: type=%s score=%s speed=%s",
        obstacle_type,
        score,
        obstacle_speed,
    )


def reset_game():
    global score
    global game_over
    global player_velocity_y
    global on_ground
    global obstacle_speed

    player.x = 100
    player.y = (
        GROUND_Y
        - player.height
    )

    player_velocity_y = 0

    on_ground = True

    score = 0

    obstacle_speed = STARTING_SPEED

    game_over = False

    games_started.inc()

    game_active.set(1)

    current_score.set(
        score
    )

    current_speed.set(
        obstacle_speed
    )

    trace_game_started(
        "game.restart"
    )

    logger.info(
        "SRE Runner game restarted"
    )

    reset_obstacle()


def draw_text(
    text,
    font_object,
    color,
    x,
    y,
):

    surface = font_object.render(
        text,
        True,
        color,
    )

    screen.blit(
        surface,
        (x, y),
    )


# --------------------------------------------------
# Start game
# --------------------------------------------------

games_started.inc()

game_active.set(1)

current_score.set(
    score
)

current_speed.set(
    obstacle_speed
)

trace_game_started(
    "game.start"
)

logger.info(
    "SRE Runner game started"
)

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

            logger.info(
                "SRE Runner shutdown requested"
            )

            running = False

        if event.type == pygame.KEYDOWN:

            if (
                event.key == pygame.K_SPACE
                and on_ground
                and not game_over
            ):

                player_velocity_y = (
                    JUMP_STRENGTH
                )

                on_ground = False

                trace_player_jump()

                logger.info(
                    "Player jumped: score=%s speed=%s",
                    score,
                    obstacle_speed,
                )

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

        player.y += (
            player_velocity_y
        )

        # Ground collision
        if player.bottom >= GROUND_Y:

            player.bottom = GROUND_Y

            player_velocity_y = 0

            on_ground = True

        # Move obstacle
        obstacle.x -= (
            obstacle_speed
        )

        # Passed obstacle
        if obstacle.right < 0:

            obstacles_avoided.labels(
                type=obstacle_type
            ).inc()

            trace_obstacle_avoided()

            logger.info(
                "Obstacle avoided: type=%s score=%s speed=%s",
                obstacle_type,
                score,
                obstacle_speed,
            )

            reset_obstacle()

        # Player collision with obstacle
        if player.colliderect(
            obstacle
        ):

            collisions.labels(
                type=obstacle_type
            ).inc()

            trace_collision()

            logger.error(
                "Collision detected: type=%s score=%s speed=%s",
                obstacle_type,
                score,
                obstacle_speed,
            )

            game_active.set(0)

            game_over = True

            high_score = max(
                high_score,
                score,
            )

            logger.info(
                "Game over: score=%s high_score=%s",
                score,
                high_score,
            )

        # Increase score
        score += 5

        current_score.set(
            score
        )

        # Increase difficulty
        obstacle_speed = min(
            STARTING_SPEED
            + score // 500,
            MAX_SPEED,
        )

        current_speed.set(
            obstacle_speed
        )

    # ----------------------------------------------
    # Draw
    # ----------------------------------------------

    screen.fill(
        BACKGROUND
    )

    # Ground
    pygame.draw.line(
        screen,
        GROUND,
        (0, GROUND_Y),
        (WIDTH, GROUND_Y),
        3,
    )

    # Player
    pygame.draw.rect(
        screen,
        PLAYER_COLOR,
        player,
        border_radius=6,
    )

    # Player eye
    pygame.draw.circle(
        screen,
        (
            255,
            255,
            255,
        ),
        (
            player.right - 10,
            player.top + 12,
        ),
        4,
    )

    # ----------------------------------------------
    # Obstacle
    # ----------------------------------------------

    if (
        obstacle_type
        == GROUND_OBSTACLE
    ):

        pygame.draw.rect(
            screen,
            GROUND_OBSTACLE_COLOR,
            obstacle,
            border_radius=4,
        )

    else:

        pygame.draw.rect(
            screen,
            FLYING_OBSTACLE_COLOR,
            obstacle,
            border_radius=10,
        )

    # ----------------------------------------------
    # HUD
    # ----------------------------------------------

    draw_text(
        f"Score: {score}",
        font,
        TEXT_COLOR,
        20,
        20,
    )

    draw_text(
        f"High Score: {high_score}",
        font,
        TEXT_COLOR,
        20,
        55,
    )

    draw_text(
        f"Speed: {obstacle_speed}",
        font,
        TEXT_COLOR,
        720,
        20,
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
            110,
        )

        draw_text(
            f"Score: {score}",
            font,
            TEXT_COLOR,
            390,
            190,
        )

        draw_text(
            "Press R to restart",
            font,
            TEXT_COLOR,
            340,
            230,
        )

    # ----------------------------------------------
    # Refresh display
    # ----------------------------------------------

    pygame.display.flip()

    clock.tick(
        FPS
    )


# --------------------------------------------------
# Shutdown
# --------------------------------------------------

logger.info(
    "SRE Runner application shutting down"
)

shutdown_telemetry()

pygame.quit()

sys.exit()