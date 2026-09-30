import pygame

pygame.init()
sheet = pygame.image.load("Sprites/2-Sprites/spritesheet.png")

for row in range(14):
    for col in range(22):
        # The death animation usually has multiple frames in a row.
        # Let's save the whole sheet as an artifact but wait, I can just look at the artifact image provided by the user.
        pass
