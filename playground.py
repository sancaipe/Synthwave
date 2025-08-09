import copy
import pygame
import math
import cv2
import random

pygame.init()
LARGE_RADIUS = 300
SMALL_RADIUS = 25
dim = LARGE_RADIUS*4
SCREEN_WIDTH,SCREEN_HEIGHT = dim,dim
screen = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
pygame.display.set_caption("Synthwave Background")
clock = pygame.time.Clock()

FOCAL_LENGTH = 1666
grid_color = (4,196,202)
VEL_Z = 76
STARS = 100

text_font = pygame.font.Font(None,30)
max_speed_font = text_font.render("Max speed!",True,(255,125,100))
min_speed_font = text_font.render("Min speed!",True,(255,255,255))

y_p = 80 # Number of pixels below the midpoint at which I want the perceived bottom to show at FULL_Z
# Need to solve for FULL_Z
FULL_Z = (SCREEN_HEIGHT*FOCAL_LENGTH/2/y_p)-FOCAL_LENGTH # Distance from FOCAL LENGTH to the end of the world
FULL_HALF_WIDTH = (dim/2)*(FOCAL_LENGTH+FULL_Z)/FOCAL_LENGTH
print(f"FULL Z: {FULL_Z}")

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
def stars_surface():
    surf = pygame.Surface((dim,dim))
    surf.fill((0,0,0))
    for _ in range(STARS):
        x = random.randint(1,dim)
        y = random.randint((dim/2)-y_p,(dim/2)+y_p)
        pygame.draw.circle(surf,(180,180,180),(x,y),1)
    surf.set_colorkey((0,0,0))
    return surf
stars_surf = stars_surface()

class MovingRectangle:
    _instances = []
    def __init__(self,x_real,y_real,z,w_real,h_real,vel_z,color):
        self.color = color
        self.vel_z = vel_z
        self.x_real = x_real
        self.y_real =y_real
        self.y_fromcenter = self.y_real-(SCREEN_HEIGHT/2)
        self.w_real = w_real
        self.h_real = h_real
        self.z = z
        self.adjustment_val = FOCAL_LENGTH/self.z
        self.x_perceived = (self.x_real-(dim/2)) * self.adjustment_val + (dim/2)
        self.w_perceived = self.w_real*self.adjustment_val
        self.h_perceived = self.h_real*self.adjustment_val
        self.y_perceived = (self.y_fromcenter*self.adjustment_val)+(SCREEN_HEIGHT/2)
        MovingRectangle._instances.append(self)

    @classmethod
    def update(cls,movement):
        for obj in cls._instances:
            obj.x_real += movement
            obj.z -= obj.vel_z
            obj.adjustment_val = FOCAL_LENGTH/obj.z
            obj.x_perceived = (obj.x_real-(dim/2)) * obj.adjustment_val + (dim/2)
            obj.w_perceived = obj.w_real*obj.adjustment_val
            obj.h_perceived = obj.h_real*obj.adjustment_val
            obj.y_perceived = (obj.y_fromcenter*obj.adjustment_val)+(SCREEN_HEIGHT/2)
            if obj.z <= FOCAL_LENGTH-250:
                obj.z = FULL_Z+FOCAL_LENGTH

    @classmethod
    def draw(cls,surface):
        for obj in cls._instances:
            rect = pygame.Rect(0,0,obj.w_perceived,obj.h_perceived)
            rect.midbottom = (obj.x_perceived,obj.y_perceived)
            pygame.draw.rect(surface,obj.color,rect)


rect_static = pygame.Rect(0,0,200,100)
rect_static.midbottom = (SCREEN_WIDTH/2,SCREEN_HEIGHT)

class GridZLines:
    def __init__(self,dx_real):
        self.dx_perceived = dx_real*FOCAL_LENGTH/(FOCAL_LENGTH+FULL_Z)
        self.LINES=(dim/2)/self.dx_perceived
        self.x_positions_perceived = []
        self.x_positions_real = []
        for n in range(round(self.LINES)+1):
            x_perceived = (n*self.dx_perceived)
            x_real = x_perceived*(FOCAL_LENGTH+FULL_Z)/FOCAL_LENGTH
            self.x_positions_perceived.append(x_perceived) # Now you have all of the line positions for the right half of the screen. Will need to create a mirroring effect
            self.x_positions_real.append(x_real)
        for val_real,val_perceived in zip(self.x_positions_real[1:-1],self.x_positions_perceived[1:-1]):
            self.x_positions_real.append(-val_real)
            self.x_positions_perceived.append(-val_perceived)
        # print(self.x_positions_perceived,self.x_positions_real)

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
Z_lines = GridZLines((dim/2))    

class GridXLines:
    def __init__(self,LINES,VEL_Z):
        self.LINES = LINES
        self.lines_positions = []
        self.dz = ((FULL_Z)/self.LINES)
        for n in range (LINES):
            starting_Z = (FULL_Z+FOCAL_LENGTH)-(n*self.dz)
            self.lines_positions.append(starting_Z)
        self.VEL_Z = round(self.dz*0.001,4)
        print(self.dz,self.VEL_Z)
        print(self.lines_positions)

    def update(self):
        self.lines_positions = [round(z-self.VEL_Z,4) for z in self.lines_positions]
        # for i,z in enumerate(self.lines_positions):
        #     if i < len(self.lines_positions)-1:
        #         if z <= FOCAL_LENGTH and not (FOCAL_LENGTH+FULL_Z-self.lines_positions[i+1])<self.dz:
        #             self.lines_positions[i]=FOCAL_LENGTH+FULL_Z
        #     if i == len(self.lines_positions)-1:
        #         if z <= FOCAL_LENGTH and not (FOCAL_LENGTH+FULL_Z-self.lines_positions[0])<self.dz:
        #             self.lines_positions[i]=FOCAL_LENGTH+FULL_Z


        self.lines_positions = [z if z >= FOCAL_LENGTH else (FULL_Z+FOCAL_LENGTH) for z in self.lines_positions]
        if FULL_Z+FOCAL_LENGTH in self.lines_positions:
            print(self.lines_positions, self.VEL_Z)

    def draw(self,surface):
        draw_y_perceived = [((dim/2)*FOCAL_LENGTH/z)+(dim/2) for z in self.lines_positions]
        # Mirrored above horizon
        draw_y_perceived_mirrored = [((-dim/2)*FOCAL_LENGTH/z)+(dim/2) for z in self.lines_positions]
        for i,pos in enumerate(draw_y_perceived):
            pygame.draw.line(surface,grid_color,(0,pos),(dim,pos))
            # Mirrored above horizon
            pygame.draw.line(surface,grid_color,(0,draw_y_perceived_mirrored[i]),(dim,draw_y_perceived_mirrored[i]))


X_lines = GridXLines(10,VEL_Z)
rect1 = MovingRectangle(SCREEN_WIDTH/2,SCREEN_HEIGHT,FULL_Z+FOCAL_LENGTH,200,100,X_lines.VEL_Z,(100,255,100))
rect2 = MovingRectangle(SCREEN_WIDTH/2-300,SCREEN_HEIGHT,FOCAL_LENGTH+1800,200,100,X_lines.VEL_Z,(255,100,100))

running = True
moving = False
movement_vel = 45
rect_movement_vel = 0
VEL_Z_MAX = X_lines.dz*0.25

# speed_rect_outline_surf = pygame.Surface((25,250))
# pygame.draw.rect(speed_rect_outline_surf,(255,255,255),(0,0,25,250),4)
# speed_rect_outline_surf.set_colorkey((0,0,0))
while running:
    clock.tick(60)
    screen.fill((0,0,0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        moving = True
        movement = movement_vel
        rect_movement_vel = movement * 1
    if keys[pygame.K_RIGHT]:
        moving = True
        movement = -movement_vel
        rect_movement_vel = movement * 1
    if keys[pygame.K_UP]:
        if X_lines.VEL_Z < VEL_Z_MAX:
            X_lines.VEL_Z += 0.001*X_lines.dz
            X_lines.VEL_Z = X_lines.VEL_Z
            for instance in MovingRectangle._instances:
                instance.vel_z = X_lines.VEL_Z*1
        else:
            # print("Max Speed!")
            screen.blit(max_speed_font,((dim/2)-250,(dim/2)-15))
    if keys[pygame.K_DOWN]:
        if X_lines.VEL_Z >0.001:
            X_lines.VEL_Z -= 0.001*X_lines.dz
            X_lines.VEL_Z = X_lines.VEL_Z
            for instance in MovingRectangle._instances:
                instance.vel_z = X_lines.VEL_Z*1
        else:
            # print("Min Speed!")
            screen.blit(min_speed_font,((dim/2)-250,(dim/2)-15))

    if moving:
        Z_lines.update(movement)

    # screen.blit(universe_draw,(0,0))
    # screen.blit(grid_lines,(0,0))
    screen.blit(stars_surf,(0,0))
    pygame.draw.rect(screen,(25,25,90),(0,(dim/2)+y_p,dim,dim-(dim/2+y_p)))
    pygame.draw.rect(screen,(25,25,90),(0,0,dim,dim-(dim/2+y_p)))
    Z_lines.draw(screen)
    X_lines.draw(screen)
    X_lines.update()


    # pygame.draw.line(screen,(255,255,255),(0,SCREEN_HEIGHT/2),(SCREEN_WIDTH,SCREEN_HEIGHT/2))
    # Horizontal line at world's end perceived
    pygame.draw.line(screen,(180,180,255),(0,(SCREEN_HEIGHT/2)+y_p),(SCREEN_WIDTH,(SCREEN_HEIGHT/2)+y_p))
    # And mirrored
    pygame.draw.line(screen,(180,180,255),(0,(SCREEN_HEIGHT/2)-y_p),(SCREEN_WIDTH,(SCREEN_HEIGHT/2)-y_p))
    pygame.draw.rect(screen,(50,130,50),rect_static,2)

    MovingRectangle.draw(screen)
    MovingRectangle.update(rect_movement_vel)
    # print(rect1.x_real)

    moving = False
    rect_movement_vel = 0
    # print(clock.get_fps())
    
    # Draw the speed indicator, most of this is dependent on the dimensions of the defined outline rect and the max vel currently set to 500 in the if statement of the get_pressed()
    # screen.blit(speed_rect_outline_surf,(25,(dim/2)-125))
    vel_ratio = (X_lines.VEL_Z/VEL_Z_MAX)

    if vel_ratio >= 0.5:
        R_val = 255
        G_val = 255 - ((vel_ratio-0.5)/0.5)*255
    elif 0 <= vel_ratio < 0.5:
        R_val = 255 * (vel_ratio/0.5) 
        G_val = 255
    print(X_lines.VEL_Z,VEL_Z_MAX)
    pygame.draw.rect(screen,(0,0,0),(25,(dim/2)-125,25,250))
    pygame.draw.rect(screen,(R_val,G_val,0),(25,(dim/2+125)-(vel_ratio*250),25,vel_ratio*250))
    pygame.draw.rect(screen,(255,255,255),(25,(dim/2)-125,25,250),2)

    pygame.display.flip()

pygame.quit()