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

BLACK_HOLE_RADIUS = 0.15*SCREEN_WIDTH

def draw_elliptical_decor():
    X = SCREEN_WIDTH*1.2
    Y = SCREEN_HEIGHT*1.2
    surf = pygame.Surface((X,Y))
    pygame.draw.ellipse(surf,(4,44,132),(X/2-SCREEN_WIDTH*5/10,Y/2-SCREEN_HEIGHT*5/60,SCREEN_WIDTH*5/5,SCREEN_HEIGHT*5/30))
    pygame.draw.ellipse(surf,(16,169,226),(X/2-SCREEN_WIDTH*4/10,Y/2-SCREEN_HEIGHT*4/60,SCREEN_WIDTH*4/5,SCREEN_HEIGHT*4/30))
    pygame.draw.ellipse(surf,(128,252,252),(X/2-SCREEN_WIDTH*3/10,Y/2-SCREEN_HEIGHT*3/60,SCREEN_WIDTH*3/5,SCREEN_HEIGHT*3/30))
    pygame.draw.ellipse(surf,(240,255,255),(X/2-SCREEN_WIDTH*1/4,Y/2-SCREEN_HEIGHT*1/24,SCREEN_WIDTH/2,SCREEN_HEIGHT/12))
    # OpenCV Gaussian blur
    rgb = pygame.surfarray.array3d(surf)
    cv2.GaussianBlur(rgb,[51,51],sigmaX=21,sigmaY=21,dst=rgb) #OpenCV expects array in (height,width), not (width,height) like pygame.
    surf = pygame.image.frombuffer(rgb.flatten(),rgb.shape[1::-1],'RGB')
    surf = pygame.transform.rotate(surf,-90)
    surf.set_colorkey((0,0,0))
    return surf

def draw_fwd_elliptical_decor(full_decor_surf):
    black_height = BLACK_HOLE_RADIUS*0.30
    surf = pygame.Surface((SCREEN_WIDTH,SCREEN_HEIGHT))
    surf.blit(full_decor_surf,(-SCREEN_WIDTH*0.1,-SCREEN_HEIGHT*0.1))
    pygame.draw.rect(surf,(0,0,0),(0,0,SCREEN_WIDTH,SCREEN_HEIGHT/2))
    pygame.draw.ellipse(surf,(0,0,0),(SCREEN_WIDTH/2-BLACK_HOLE_RADIUS,SCREEN_HEIGHT/2-black_height/2,BLACK_HOLE_RADIUS*2,BLACK_HOLE_RADIUS*0.25))
    surf.set_colorkey((0,0,0))
    return surf

# def draw_black_hole():
#     surf = pygame.Surface((SCREEN_WIDTH,SCREEN_HEIGHT))
#     surf.fill((0,0,255))
#     pygame.draw.circle(surf,(0,0,0),(SCREEN_WIDTH/2,SCREEN_HEIGHT/2),BLACK_HOLE_RADIUS)
#     surf.set_colorkey((0,0,255))
#     return surf

def draw_black_hole():
    surf = pygame.Surface((SCREEN_WIDTH,SCREEN_HEIGHT))
    surf.fill((0,255,0))
    pygame.draw.circle(surf,(4,44,132),(SCREEN_WIDTH/2,SCREEN_HEIGHT/2),BLACK_HOLE_RADIUS*1.1)
    pygame.draw.circle(surf,(0,0,0),(SCREEN_WIDTH/2,SCREEN_HEIGHT/2),BLACK_HOLE_RADIUS/1.5)
    # OpenCV Gaussian blur
    rgb = pygame.surfarray.array3d(surf)
    cv2.GaussianBlur(rgb,[51,51],sigmaX=41,sigmaY=41,dst=rgb) #OpenCV expects array in (height,width), not (width,height) like pygame.
    surf = pygame.image.frombuffer(rgb.flatten(),rgb.shape[1::-1],'RGB')
    surf = pygame.transform.rotate(surf,-90)

    surf.set_colorkey((0,255,0))
    return surf

def draw_black_hole_glow():
    surf = pygame.Surface((SCREEN_WIDTH,SCREEN_HEIGHT))
    surf.fill((0,0,0))
    pygame.draw.circle(surf,(128,252,252),(SCREEN_WIDTH/2,SCREEN_HEIGHT/2),BLACK_HOLE_RADIUS*1.4)
    pygame.draw.circle(surf,(240,255,255),(SCREEN_WIDTH/2,SCREEN_HEIGHT/2),BLACK_HOLE_RADIUS*1.3)
    # OpenCV Gaussian blur
    rgb = pygame.surfarray.array3d(surf)
    cv2.GaussianBlur(rgb,[21,21],sigmaX=15,sigmaY=15,dst=rgb) #OpenCV expects array in (height,width), not (width,height) like pygame.
    surf = pygame.image.frombuffer(rgb.flatten(),rgb.shape[1::-1],'RGB')
    surf = pygame.transform.rotate(surf,-90)
    pygame.draw.circle(surf,(0,0,0),(SCREEN_WIDTH/2,SCREEN_HEIGHT/2),BLACK_HOLE_RADIUS)

    surf.set_colorkey((0,0,0))
    return surf

def draw_glow_spots():
    surf = pygame.Surface((BLACK_HOLE_RADIUS*2,BLACK_HOLE_RADIUS*2))
    surf.fill((0,0,0))
    pygame.draw.circle(surf,(4,44,132),(BLACK_HOLE_RADIUS,BLACK_HOLE_RADIUS),BLACK_HOLE_RADIUS/2)
    pygame.draw.circle(surf,(128,252,252),(BLACK_HOLE_RADIUS,BLACK_HOLE_RADIUS),BLACK_HOLE_RADIUS/5)
    # OpenCV Gaussian blur
    rgb = pygame.surfarray.array3d(surf)
    cv2.GaussianBlur(rgb,[41,41],sigmaX=15,sigmaY=15,dst=rgb) #OpenCV expects array in (height,width), not (width,height) like pygame.
    surf = pygame.image.frombuffer(rgb.flatten(),rgb.shape[1::-1],'RGB')
    surf = pygame.transform.rotate(surf,-90)
    
    surf.set_alpha(200)
    surf.set_colorkey((0,0,0))
    return surf


oval_surf = draw_elliptical_decor()
fwd_oval_surf = draw_fwd_elliptical_decor(oval_surf)
black_hole = draw_black_hole()
black_hole_glow = draw_black_hole_glow()
glow_spot = draw_glow_spots()

# oval_surf = pygame.transform.rotate(oval_surf,25)
oval_rect = oval_surf.get_rect(center=(SCREEN_WIDTH/2,SCREEN_HEIGHT/2))

# fwd_oval_surf = pygame.transform.rotate(fwd_oval_surf,25)
fwd_oval_rect = fwd_oval_surf.get_rect(center=(SCREEN_WIDTH/2,SCREEN_HEIGHT/2))

glow_spot_rect1 = glow_spot.get_rect(center=(SCREEN_WIDTH/2-BLACK_HOLE_RADIUS*1.25,SCREEN_HEIGHT/2-BLACK_HOLE_RADIUS*0.1))
glow_spot_rect2 = glow_spot.get_rect(center=(SCREEN_WIDTH/2+BLACK_HOLE_RADIUS*1.25,SCREEN_HEIGHT/2-BLACK_HOLE_RADIUS*0.1))


def all_together_blackhole(oval,oval_rect,black_hole,black_hole_glow,fwd_oval,fwd_oval_rect,glow_spot,glow_spot_rect1,glow_spot_rect2):
    surf = pygame.Surface((SCREEN_WIDTH,SCREEN_HEIGHT))
    surf.fill((0,1,0))
    pygame.draw.circle(surf,(0,0,0),(SCREEN_WIDTH/2,SCREEN_HEIGHT/2),SCREEN_WIDTH/1.9)
    surf.blit(oval,oval_rect)
    surf.blit(black_hole,(0,0))
    surf.blit(black_hole_glow,(0,0),special_flags=pygame.BLEND_RGB_ADD)
    surf.blit(fwd_oval,fwd_oval_rect)
    surf.blit(glow_spot,glow_spot_rect1,special_flags=pygame.BLEND_RGB_ADD)
    surf.blit(glow_spot,glow_spot_rect2,special_flags=pygame.BLEND_RGB_ADD)
    
    surf.set_colorkey((0,1,0))
    return surf

full_black_hole = all_together_blackhole(oval_surf,oval_rect,black_hole,black_hole_glow,fwd_oval_surf,fwd_oval_rect,glow_spot,glow_spot_rect1,glow_spot_rect2)
full_black_hole = pygame.transform.rotate(full_black_hole,25)
full_black_hole_rect = full_black_hole.get_rect(center=(SCREEN_WIDTH/2,SCREEN_HEIGHT/2))
new_width = full_black_hole.get_width()*1.0
new_height = full_black_hole.get_height()*1.0

scaled_black_hole = pygame.transform.smoothscale(full_black_hole,(new_width,new_height))
scaled_black_hole_rect = scaled_black_hole.get_rect(center=(SCREEN_WIDTH/2,SCREEN_HEIGHT/2))
far_black_hole = pygame.transform.rotate(full_black_hole,-40)
scaled_far_black_hole = pygame.transform.smoothscale(far_black_hole,(new_width*0.5,new_height*0.5))
scaled_far_black_hole_rect = scaled_far_black_hole.get_rect(center=(SCREEN_WIDTH*2/3,SCREEN_HEIGHT*1/5))

small_far_black_hole = pygame.transform.rotate(full_black_hole,-25)
small_scaled_far_black_hole = pygame.transform.smoothscale(small_far_black_hole,(new_width*0.2,new_height*0.2))
small_scaled_far_black_hole_rect = small_scaled_far_black_hole.get_rect(center=(SCREEN_WIDTH*1/5,SCREEN_HEIGHT*6/7))

def draw_stars(N):
    surf = pygame.Surface((SCREEN_WIDTH,SCREEN_HEIGHT))
    for _ in range(N):
        x = random.randint(0,SCREEN_WIDTH)
        y = random.randint(0,SCREEN_HEIGHT)
        pygame.draw.circle(surf,(200,200,200),(x,y),1)

    return surf
stars = draw_stars(2500)

running = True
while running:
    clock.tick(60)
    screen.fill((0,0,0))


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.blit(stars,(0,0))
    # screen.blit(oval_surf,oval_rect)
    # screen.blit(black_hole,(0,0))
    # screen.blit(black_hole_glow,(0,0),special_flags=pygame.BLEND_RGB_ADD)
    # screen.blit(fwd_oval_surf,fwd_oval_rect)
    # screen.blit(glow_spot,glow_spot_rect1,special_flags=pygame.BLEND_RGB_ADD)
    # screen.blit(glow_spot,glow_spot_rect2,special_flags=pygame.BLEND_RGB_ADD)
    # screen.blit(full_black_hole,full_black_hole_rect)
    screen.blit(scaled_black_hole,scaled_black_hole_rect)
    # screen.blit(scaled_far_black_hole,scaled_far_black_hole_rect)
    screen.blit(small_scaled_far_black_hole,small_scaled_far_black_hole_rect)

    # pygame.draw.rect(screen,(255,0,0),scaled_black_hole_rect,2)
    # pygame.draw.rect(screen,(255,0,0),scaled_far_black_hole_rect,2)
    # pygame.draw.rect(screen,(255,0,0),small_scaled_far_black_hole_rect,2)
    print(f"{clock.get_fps():.0f}")
    pygame.display.flip()

pygame.quit()