import copy
import pygame
import math
import cv2
import random

pygame.init()
LARGE_RADIUS = 190
SMALL_RADIUS = 25
dim = LARGE_RADIUS*4
SCREEN_WIDTH,SCREEN_HEIGHT = dim,dim
screen = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
pygame.display.set_caption("Synthwave Background")
clock = pygame.time.Clock()

FOCAL_LENGTH = 1666
grid_color = (4,196,202)
VEL_Z = 100


y_p = 25 # Number of pixels below the midpoint at which I want the perceived bottom to show at FULL_Z
# Need to solve for FULL_Z
FULL_Z = (SCREEN_HEIGHT*FOCAL_LENGTH/2/y_p)-FOCAL_LENGTH # Distance from FOCAL LENGTH to the end of the world
print(f"FULL_Z: {FULL_Z}")

def draw_universe():
    surf = pygame.Surface((SCREEN_HEIGHT,SCREEN_WIDTH))
    surf.fill((0,0,0))
    pygame.draw.rect(surf,(255,255,255),(0,SCREEN_HEIGHT*15/31,dim,SCREEN_HEIGHT/31))
    # OpenCV Gaussian blur
    rgb = pygame.surfarray.array3d(surf)
    cv2.GaussianBlur(rgb,[21,21],sigmaX=11,sigmaY=11,dst=rgb) #OpenCV expects array in (height,width), not (width,height) like pygame.
    surf = pygame.image.frombuffer(rgb.flatten(),rgb.shape[1::-1],'RGB')
    surf = pygame.transform.rotate(surf,-90)
    surf.set_colorkey((0,0,0))
    return surf
universe_draw = draw_universe()

def star_surface():
    surf = pygame.Surface((SCREEN_WIDTH,SCREEN_HEIGHT))
    pygame.draw.circle(surf,(225,225,255),(SCREEN_WIDTH/2,SCREEN_HEIGHT/2),75)
    # OpenCV Gaussian blur
    rgb = pygame.surfarray.array3d(surf)
    cv2.GaussianBlur(rgb,[21,21],sigmaX=10,sigmaY=10,dst=rgb) #OpenCV expects array in (height,width), not (width,height) like pygame.
    surf = pygame.image.frombuffer(rgb.flatten(),rgb.shape[1::-1],'RGB')
    surf = pygame.transform.rotate(surf,-90)
    surf.set_colorkey((0,0,0))
    return surf
star_draw = star_surface()

universe_draw.blit(star_draw,(0,0),special_flags=pygame.BLEND_RGB_ADD)


class CenteredRectangle:
    def __init__(self,y_real,w_real,h_real,vel_z):
        self.vel_z = vel_z
        self.x_real = SCREEN_WIDTH/2
        self.y_real =y_real
        self.y_fromcenter = self.y_real-(SCREEN_HEIGHT/2)
        self.w_real = w_real
        self.h_real = h_real
        self.z = FULL_Z+FOCAL_LENGTH
        self.adjustment_val = FOCAL_LENGTH/self.z
        self.x_perceived = (self.x_real-(dim/2)) * self.adjustment_val + (dim/2)
        self.w_perceived = self.w_real*self.adjustment_val
        self.h_perceived = self.h_real*self.adjustment_val
        self.y_perceived = (self.y_fromcenter*self.adjustment_val)+(SCREEN_HEIGHT/2)

    def update(self,movement):
        self.x_real += movement
        self.z -= self.vel_z
        self.adjustment_val = FOCAL_LENGTH/self.z
        self.x_perceived = (self.x_real-(dim/2)) * self.adjustment_val + (dim/2)
        self.w_perceived = self.w_real*self.adjustment_val
        self.h_perceived = self.h_real*self.adjustment_val
        self.y_perceived = (self.y_fromcenter*self.adjustment_val)+(SCREEN_HEIGHT/2)
        if self.z <= FOCAL_LENGTH-250:
            self.z = FULL_Z+FOCAL_LENGTH

    def draw(self,surface):
        rect = pygame.Rect(0,0,self.w_perceived,self.h_perceived)
        rect.midbottom = (self.x_perceived,self.y_perceived)
        pygame.draw.rect(surface,(100,255,100),rect,2)

rect1 = CenteredRectangle(SCREEN_HEIGHT,200,100,VEL_Z)
rect_static = pygame.Rect(0,0,200,100)
rect_static.midbottom = (SCREEN_WIDTH/2,SCREEN_HEIGHT)

# Draw the grid
def grid_Z_lines():
    surf = pygame.Surface((dim,dim))
    surf.fill((0,0,0))
    # pygame.draw.line(surf,grid_color,(0,(dim/2)+58),(dim,(dim/2)+58))
    pygame.draw.line(surf,grid_color,(dim/2,y_p+(SCREEN_HEIGHT/2)),(dim/2,dim))
    # Mirrored above horizon
    pygame.draw.line(surf,grid_color,(dim/2,-y_p+(SCREEN_HEIGHT/2)),(dim/2,0))
    # The Z-axis lines
    Z_LINES = 18 # from the center, in each direction
    dx_at_FULL_Z_FOCAL_LENGTH = (dim/2)/Z_LINES

    for n in range(1,Z_LINES+1):
        dx_perceived = dx_at_FULL_Z_FOCAL_LENGTH*n
        dx_true = (dx_perceived*(FOCAL_LENGTH+FULL_Z))/FOCAL_LENGTH
        pygame.draw.line(surf,grid_color,((dim/2)+dx_perceived,y_p+(SCREEN_HEIGHT/2)),((dim/2)+dx_true,dim))
        pygame.draw.line(surf,grid_color,((dim/2)-dx_perceived,y_p+(SCREEN_HEIGHT/2)),((dim/2)-dx_true,dim))
        #Mirrored above horizon
        pygame.draw.line(surf,grid_color,((dim/2)+dx_perceived,-y_p+(SCREEN_HEIGHT/2)),((dim/2)+dx_true,0))
        pygame.draw.line(surf,grid_color,((dim/2)-dx_perceived,-y_p+(SCREEN_HEIGHT/2)),((dim/2)-dx_true,0))      
    surf.set_colorkey((0,0,0))
    return surf
grid_lines = grid_Z_lines()

class GridZLines:
    def __init__(self,LINES):
        self.LINES=LINES
        self.dx = (dim/2)/LINES # At the full depth, FOCAL LENGTH + FULL Z
        self.x_positions_perceived = []
        self.x_positions_real = []
        for n in range(LINES+1):
            x_perceived = (n*self.dx)
            x_real = x_perceived*(FOCAL_LENGTH+FULL_Z)/FOCAL_LENGTH
            self.x_positions_perceived.append(x_perceived) # Now you have all of the line positions for the right half of the screen. Will need to create a mirroring effect
            self.x_positions_real.append(x_real)
        for val_real,val_perceived in zip(self.x_positions_real[1:-1],self.x_positions_perceived[1:-1]):
            self.x_positions_real.append(-val_real)
            self.x_positions_perceived.append(-val_perceived)
        print(self.x_positions_perceived,self.x_positions_real)

    def update(self,dx):
        self.x_positions_real = [x+dx for x in self.x_positions_real]
        for i,x_real in enumerate(self.x_positions_real):
            x_perceived = x_real*FOCAL_LENGTH/(FOCAL_LENGTH+FULL_Z)
            if x_perceived <-(dim/2):
                x_perceived = (dim/2)
                self.x_positions_real[i] = x_perceived * (FOCAL_LENGTH+FULL_Z)/FOCAL_LENGTH
            elif x_perceived > (dim/2):
                x_perceived = -(dim/2)
                self.x_positions_real[i] = x_perceived * (FOCAL_LENGTH+FULL_Z)/FOCAL_LENGTH
            self.x_positions_perceived[i] = x_perceived

    def draw(self,surface):
        for x_real,x_perceived in zip(self.x_positions_real,self.x_positions_perceived):
            pygame.draw.line(surface,grid_color,(x_real+(SCREEN_WIDTH/2),SCREEN_HEIGHT),(x_perceived+(SCREEN_WIDTH/2),(SCREEN_HEIGHT/2)+y_p))
            # pygame.draw.line(surface,grid_color,(-x_real+(SCREEN_WIDTH/2),SCREEN_HEIGHT),(-x_perceived+(SCREEN_WIDTH/2),(SCREEN_HEIGHT/2)+y_p))
            # Mirrored above the horizontal
            pygame.draw.line(surface,grid_color,(x_real+(SCREEN_WIDTH/2),0),(x_perceived+(SCREEN_WIDTH/2),(SCREEN_HEIGHT/2)-y_p))
            # pygame.draw.line(surface,grid_color,(-x_real+(SCREEN_WIDTH/2),0),(-x_perceived+(SCREEN_WIDTH/2),(SCREEN_HEIGHT/2)-y_p))
Z_lines = GridZLines(18)    

class GridXLines:
    def __init__(self,LINES,VEL_Z):
        self.LINES = LINES
        self.VEL_Z = VEL_Z
        self.lines_positions = []
        self.dz = (FULL_Z/self.LINES)
        for n in range (LINES):
            starting_Z = (FULL_Z+FOCAL_LENGTH)-(n*self.dz)
            self.lines_positions.append(starting_Z)

    def update(self):
        self.lines_positions = [z-self.VEL_Z for z in self.lines_positions]
        self.lines_positions = [z if z >= FOCAL_LENGTH else (FULL_Z+FOCAL_LENGTH) for z in self.lines_positions]

    def draw(self,surface):
        draw_y_perceived = [((dim/2)*FOCAL_LENGTH/z)+(dim/2) for z in self.lines_positions]
        # Mirrored above horizon
        draw_y_perceived_mirrored = [((-dim/2)*FOCAL_LENGTH/z)+(dim/2) for z in self.lines_positions]
        for i,pos in enumerate(draw_y_perceived):
            pygame.draw.line(surface,grid_color,(0,pos),(dim,pos))
            # Mirrored above horizon
            pygame.draw.line(surface,grid_color,(0,draw_y_perceived_mirrored[i]),(dim,draw_y_perceived_mirrored[i]))


X_lines = GridXLines(10,VEL_Z)

running = True
moving = False
movement_vel = 7
rect_movement_vel = 0
while running:
    clock.tick(60)
    screen.fill((0,0,0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        moving = True
        movement = -movement_vel
        rect_movement_vel = movement * 1
    if keys[pygame.K_RIGHT]:
        moving = True
        movement = movement_vel
        rect_movement_vel = movement * 1

    if moving:
        Z_lines.update(movement)

    # screen.blit(universe_draw,(0,0))
    # screen.blit(grid_lines,(0,0))
    Z_lines.draw(screen)
    X_lines.draw(screen)
    X_lines.update()


    # pygame.draw.line(screen,(255,255,255),(0,SCREEN_HEIGHT/2),(SCREEN_WIDTH,SCREEN_HEIGHT/2))
    # Horizontal line at world's end perceived
    pygame.draw.line(screen,(180,180,255),(0,(SCREEN_HEIGHT/2)+y_p),(SCREEN_WIDTH,(SCREEN_HEIGHT/2)+y_p))
    # And mirrored
    pygame.draw.line(screen,(180,180,255),(0,(SCREEN_HEIGHT/2)-y_p),(SCREEN_WIDTH,(SCREEN_HEIGHT/2)-y_p))
    pygame.draw.rect(screen,(50,130,50),rect_static,2)

    rect1.draw(screen)
    rect1.update(rect_movement_vel)
    # print(rect1.x_real)

    moving = False
    rect_movement_vel = 0
    # print(clock.get_fps())
    pygame.display.flip()

pygame.quit()