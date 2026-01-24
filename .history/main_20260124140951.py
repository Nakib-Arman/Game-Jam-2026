import pygame

pygame.init()

screen = pygame.display.set_mode((1200,800)) 

running = True
while running:
    for event in pygame.event.get()