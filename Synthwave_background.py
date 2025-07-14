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

LARGE_RADIUS = 300
SMALL_RADIUS = 25

FULL_Z = 15000
FOCAL_LENGTH = 1666
print(FULL_Z, FOCAL_LENGTH)
grid_color = (4,196,202)
# Draw the sun
def sun_colors():
    top_color = (255,211,25)
    bottom_color = (242,34,255)

    DIVISIONS = 15
    delta_R =(top_color[0]-bottom_color[0])/DIVISIONS 
    delta_G =(top_color[1]-bottom_color[1])/DIVISIONS 
    delta_B =(top_color[2]-bottom_color[2])/DIVISIONS 
    box_height = LARGE_RADIUS*2/DIVISIONS

    surf = pygame.Surface((LARGE_RADIUS*2,LARGE_RADIUS*2))
    surf.fill((0,0,0))

    pygame.draw.rect(surf,top_color,(0,0,LARGE_RADIUS*2,box_height))
    for n in range(1,DIVISIONS-1):
        n_color = (top_color[0]-(delta_R*n),top_color[1]-(delta_G*n),top_color[2]-(delta_B*n))
        n_starting_height = n*box_height
        pygame.draw.rect(surf,n_color,(0,n_starting_height,LARGE_RADIUS*2,box_height))
    pygame.draw.rect(surf,bottom_color,(0,(DIVISIONS-1)*box_height,LARGE_RADIUS*2,box_height))

    # OpenCV Gaussian blur
    rgb = pygame.surfarray.array3d(surf)
    cv2.GaussianBlur(rgb,[51,51],sigmaX=21,sigmaY=21,dst=rgb) #OpenCV expects array in (height,width), not (width,height) like pygame.
    surf = pygame.image.frombuffer(rgb.flatten(),rgb.shape[1::-1],'RGB')
    surf = pygame.transform.rotate(surf,-90)
    surf.set_colorkey((0,0,0))
    return surf
def circle_window():
    surf = pygame.Surface((LARGE_RADIUS*4,LARGE_RADIUS*4))
    surf.fill((0,0,0))

    pygame.draw.circle(surf,(0,0,255),(LARGE_RADIUS*2,LARGE_RADIUS*2),0.9*LARGE_RADIUS)
    surf.set_colorkey((0,0,255))

    return surf
def slots():
    dim = LARGE_RADIUS*4
    surf = pygame.Surface((dim,dim))
    surf.fill((0,0,255))

    SLOTS = 10
    starting_y = LARGE_RADIUS*1.8
    ending_y = LARGE_RADIUS*3
    SLOT_HEIGHT = 10
    spacing = (ending_y-starting_y-(SLOT_HEIGHT*SLOTS))/SLOTS
    y_spacing = SLOT_HEIGHT+spacing

    for n in range(SLOTS-1):
        pygame.draw.rect(surf,(0,0,0),(0,starting_y+(n*y_spacing),dim,SLOT_HEIGHT))
    surf.set_colorkey((0,0,255))
    return surf
blurry_sun = sun_colors()
sun_window = circle_window()
slot_decor = slots()
def draw_sun(sun_colors,circle_window,slots):
    dim = LARGE_RADIUS*4
    surf = pygame.Surface((dim,dim))

    surf.blit(sun_colors,(dim/4,dim/4-200))
    surf.blit(circle_window,(0,0-200))
    surf.blit(slots,(0,0-200))
    surf.set_colorkey((0,0,0))
    return surf
sun = draw_sun(blurry_sun,sun_window,slot_decor)

# Draw the universe background
def universe():
    dim = LARGE_RADIUS*4
    surf = pygame.Surface((dim,dim))
    surf.fill((0,0,0))
    black = (0,0,0)
    mid = (60,25,80)

    pygame.draw.rect(surf,mid,(0,dim/4.5,dim,dim*2.5/4.5))
    # OpenCV Gaussian blur
    rgb = pygame.surfarray.array3d(surf)
    cv2.GaussianBlur(rgb,[511,511],sigmaX=201,sigmaY=201,dst=rgb) #OpenCV expects array in (height,width), not (width,height) like pygame.
    surf = pygame.image.frombuffer(rgb.flatten(),rgb.shape[1::-1],'RGB')
    surf = pygame.transform.rotate(surf,-90)
    
    STARS = 500
    for _ in range(STARS):
        center = (random.randint(0,dim),random.randint(0,dim/1.5))
        if math.sqrt((center[0]-LARGE_RADIUS*2)**2+(center[1]-LARGE_RADIUS*2+200)**2) < LARGE_RADIUS:
            continue
        else:
            pygame.draw.circle(surf,(220,220,220),center,1)

    return surf
space_background = universe()

# Draw the grid
def grid_Z_lines():
    surf = pygame.Surface((dim,dim))
    surf.fill((0,0,0))
    pygame.draw.rect(surf,(10,10,50),(0,(dim/2)+58,dim,LARGE_RADIUS*2))
    pygame.draw.line(surf,grid_color,(0,(dim/2)+58),(dim,(dim/2)+58))
    pygame.draw.line(surf,grid_color,(LARGE_RADIUS*2,(dim/2)+58),(LARGE_RADIUS*2,dim))
    
    # The Z-axis lines
    Z_LINES = 9 # from the center, in each direction
    dx_at_FULL_Z = (LARGE_RADIUS*2)/Z_LINES

    for n in range(1,Z_LINES+1):
        dx_perceived = dx_at_FULL_Z*n
        dx_true = (dx_perceived*(FOCAL_LENGTH+FULL_Z))/FOCAL_LENGTH
        pygame.draw.line(surf,grid_color,(LARGE_RADIUS*2+dx_perceived,(dim/2)+58),(LARGE_RADIUS*2+dx_true,dim))
        pygame.draw.line(surf,grid_color,(LARGE_RADIUS*2-dx_perceived,(dim/2)+58),(LARGE_RADIUS*2-dx_true,dim))
    surf.set_colorkey((0,0,0))
    return surf
grid_lines = grid_Z_lines()

class grid_X_lines:   
    def __init__(self,LINES, VEL_Z,starting_y):
        if LINES <= 1:
            raise ValueError("Number of Lines (LINES) must be greated than 1")
        self.LINES = LINES
        self.VEL_Z = VEL_Z
        self.starting_y = starting_y
        self.lines_positions = [] # Raw Z positions of the LINES
        self.dz = (FULL_Z-FOCAL_LENGTH)/LINES
        for n in range (LINES+1):
            starting_pos = FULL_Z - ((n-1)*self.dz)
            self.lines_positions.append(starting_pos)

    def update(self):
        self.lines_positions = [x-self.VEL_Z for x in self.lines_positions]
        self.lines_positions = [x if x >= FOCAL_LENGTH else FULL_Z+self.dz for x in self.lines_positions]

    def draw(self,color,surface):
        draw_y_positions = [((dim/2)*FOCAL_LENGTH/x)+(dim/2) for x in self.lines_positions]
        for pos in draw_y_positions:
            pygame.draw.line(surface,color,(0,pos),(dim,pos))


X_lines = grid_X_lines(9,40,LARGE_RADIUS*2.2)
print(X_lines.lines_positions)

def bright_horizon():
    surf = pygame.Surface((dim,200))
    pygame.draw.rect(surf,(255,255,255),(0,95,dim,10))
    # OpenCV Gaussian blur
    rgb = pygame.surfarray.array3d(surf)
    cv2.GaussianBlur(rgb,[11,11],sigmaX=10,sigmaY=10,dst=rgb) #OpenCV expects array in (height,width), not (width,height) like pygame.
    surf = pygame.image.frombuffer(rgb.flatten(),rgb.shape[1::-1],'RGB')
    surf = pygame.transform.rotate(surf,-90)
    surf.set_colorkey((0,0,0))
    return surf
horizon = bright_horizon()

y_p = (dim/2)*FOCAL_LENGTH/(FOCAL_LENGTH+FULL_Z)
running = True
while running:
    clock.tick(60)
    screen.fill((0,0,255))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.blit(space_background,(0,0))
    screen.blit(sun,(0,0))
    screen.blit(grid_lines,(0,0))

    
    # pygame.draw.line(screen,grid_color,(0,y_p+(dim/2)),(dim,y_p+(dim/2)),5)
    X_lines.draw(grid_color,screen)
    X_lines.update()
    screen.blit(horizon,(0,(dim/2)+58-100),special_flags=pygame.BLEND_RGB_ADD)

    pygame.display.flip()

pygame.quit()