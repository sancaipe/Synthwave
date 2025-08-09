import copy
import pygame
import math
import cv2
import random
import numpy as np

pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 1000,1000

screen = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
pygame.display.set_caption("Synthwave Background")
clock = pygame.time.Clock()

X = SCREEN_WIDTH*1.0
Y = SCREEN_HEIGHT*1.0


def planet():
    surf0 = pygame.Surface((X,Y))
    surf0.fill((0,0,0))
    pygame.draw.circle(surf0,(15,15,15),(X/2,Y/2),300)

    surf1 = pygame.Surface((X,Y))
    surf1.fill((0,0,0))
    pygame.draw.circle(surf1,(215,230,225),(X/2,Y/2),305)
    pygame.draw.circle(surf1,(200,225,220),(X/2,Y/2 + 6),300)
    pygame.draw.circle(surf1,(125,150,145),(X/2,Y/2 + 12),300)
    pygame.draw.circle(surf1,(0,0,0),(X/2,Y/2+50),310)
    # OpenCV Gaussian blur
    rgb = pygame.surfarray.array3d(surf1)
    cv2.GaussianBlur(rgb,[31,31],sigmaX=11,sigmaY=11,dst=rgb) #OpenCV expects array in (height,width), not (width,height) like pygame.
    surf1 = pygame.image.frombuffer(rgb.flatten(),rgb.shape[1::-1],'RGB')
    surf1 = pygame.transform.rotate(surf1,-90)

    surf2 = pygame.Surface((X,Y))
    surf2.fill((0,0,0))
    pygame.draw.circle(surf2,(1,1,1),(X/2,Y/2),300)
    surf2.set_colorkey((1,1,1))
    surf1.blit(surf2,(0,0))

    surf1.set_colorkey((0,0,0))

    surf0.blit(surf1,(0,0),special_flags=pygame.BLEND_RGB_ADD)

    surf0.set_colorkey((0,0,0))

    return surf0
planet_surf = planet()

def stars(n):
    surf = pygame.Surface((X,Y))
    for i in range(n):
        x = random.randint(1,X-1)
        y = random.randint(1,Y-1)
        surf.set_at((x,y),(170,170,170))
    return surf

stars_surf = stars(1000)

sunshine_alpha = 150
def sun_shine():
    surf = pygame.Surface((X,Y),pygame.SRCALPHA)
    surf.fill((0,0,0))
    pygame.draw.circle(surf,(73,27,1),(X/2,Y/2),140)
    pygame.draw.circle(surf,(76,34,14),(X/2,Y/2),120)
    pygame.draw.circle(surf,(80,42,27),(X/2,Y/2),100)
    pygame.draw.circle(surf,(165,106,81),(X/2,Y/2),80)
    pygame.draw.circle(surf,(200,121,85),(X/2,Y/2),60)
    # pygame.draw.circle(surf,(0,0,0),(X/2,Y/2),50)

    # OpenCV Gaussian blur
    rgb = pygame.surfarray.array3d(surf)    
    cv2.GaussianBlur(rgb,[51,51],sigmaX=21,sigmaY=21,dst = rgb) #OpenCV expects array in (height,width), not (width,height) like pygame.
    surf = pygame.image.frombuffer(rgb.flatten(),surf.get_size(),'RGB')
    surf = pygame.transform.rotate(surf,-90)

    surf.set_colorkey((0,0,0))

    return surf

sunshine_surf = sun_shine()


running = True

current_y=-25
current_x = 0
while running:
    clock.tick(60)
    screen.fill((0,0,0))
    

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.blit(stars_surf,(0,0))

    pygame.draw.circle(screen,(250,250,250),(SCREEN_WIDTH/2,SCREEN_HEIGHT/2-300+10-current_y+250),50)

    # pygame.draw.circle(screen,(100,100,100),(SCREEN_WIDTH/2,SCREEN_HEIGHT/2),300)
    # pygame.draw.circle(screen,(0,0,0),(SCREEN_WIDTH/2,SCREEN_HEIGHT/2+50),310)

    screen.blit(planet_surf,(0,0+250))
    screen.blit(sunshine_surf,(0,-300+10-current_y+250),special_flags=pygame.BLEND_RGB_ADD)

    current_y += 0.01
    current_x += 0.1
    pygame.display.flip()

pygame.quit()