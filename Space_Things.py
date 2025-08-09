import copy
import pygame
import math
import cv2
import random

pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 1000,1000

screen = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
pygame.display.set_caption("Synthwave Background")
clock = pygame.time.Clock()

X = SCREEN_WIDTH*1.2
Y = SCREEN_HEIGHT*1.2


running = True
while running:
    clock.tick(60)
    screen.fill((0,0,0))


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    pygame.draw.circle(screen,(250,250,250),(SCREEN_WIDTH/2,SCREEN_HEIGHT/2-300+10),50)

    pygame.draw.circle(screen,(100,100,100),(SCREEN_WIDTH/2,SCREEN_HEIGHT/2),300)
    pygame.draw.circle(screen,(0,0,0),(SCREEN_WIDTH/2,SCREEN_HEIGHT/2+50),310)



    pygame.display.flip()

pygame.quit()