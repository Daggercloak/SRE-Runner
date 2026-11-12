import sys
import pygame

pygame.init()

screen = pygame.display.set_mode((800, 400))
pygame.display.set_caption("Pygame Test")

clock = pygame.time.Clock()

running = True

while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((30, 30, 30))

    pygame.draw.rect(
        screen,
        (0, 150, 255),
        (100, 250, 50, 50)
    )

    pygame.display.flip()

    clock.tick(60)

pygame.quit()
sys.exit()
