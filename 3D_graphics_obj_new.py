import pygame
import numpy as np
from math import cos, sin, pi
import os.path

SCREEN_WIDTH = 512
SCREEN_HEIGHT = 512
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('3D cube rotating')

clock = pygame.Clock()

fps_font = pygame.font.SysFont('Comic Sans MS', 30)


CENTER = np.array([SCREEN_WIDTH/2, SCREEN_HEIGHT/2])
SCALE = 200


LOCALDIR = os.path.dirname(os.path.realpath(__name__))



def getinfo(dir:str):
    with open(dir) as f:
        lines = f.readlines()

    all_points =    np.array([line[2:].replace('\n', '').split(' ') for line in lines if line[0]=='v'], dtype=np.float32)
    #the minimum index for a obj file is 1 so I set it to 0
    all_triangles = np.array([line[2:].replace('\n', '').split(' ') for line in lines if line[0]=='f'], dtype=np.int32)-1
    
    return all_points, all_triangles


model_dir = os.path.join(LOCALDIR, 'Standford_bunny.txt')
original_points, faces_index = getinfo(model_dir)
print(original_points.shape, faces_index.shape)


points = np.copy(original_points)

def rotx(all_points, ang):
    return np.dot(all_points, np.array([[1.,0.,0.],[0., cos(ang), -sin(ang)], [0., sin(ang), cos(ang)]]))
    
def roty(all_points, ang):
    return np.dot(all_points, np.array([[cos(ang),0.,sin(ang)],[0., 1., 0.], [-sin(ang), 0., cos(ang)]]))
    

def rotz(all_points, ang):
    return np.dot(all_points, np.array([[cos(ang), -sin(ang), 0.],[sin(ang), cos(ang), 0.], [0., 0., 1.]]))
    

def perspective(points):
    newpoints = np.copy(points)

    z = 1/np.clip(newpoints[:, 2], 0.0625, 2048)
    newpoints = newpoints[:, :2]
    newpoints *= z[:, None]
    newpoints[:,1]*=-1
    newpoints = newpoints*SCALE+CENTER
    

    return newpoints



def getnormal(triangles):

    vecs1 = triangles[:, 1] - triangles[:, 0]
    vecs2 = triangles[:, 2] - triangles[:, 0]

    normals = np.cross(vecs1, vecs2)
    dists = np.sqrt(np.sum(np.square(normals), axis=1))
    normals /= dists[:, None]

    return normals

done = False

rotationx = 0
rotationy = 0
#rotationz = 0

ArrowKeyState = [False, False, False, False]
MoveKeyState = [False, False, False, False, False, False]
offset = np.array([0, 0, 0.5], dtype=np.float16)
MOVE_AMOUNT = 0.02
ROTATION_AMOUNT = 0.04

while not done:
    screen.fill((52, 177, 235))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:
                ArrowKeyState[0] = True
            elif event.key == pygame.K_LEFT:
                ArrowKeyState[1] = True
            elif event.key == pygame.K_UP:
                ArrowKeyState[2] = True
            elif event.key == pygame.K_DOWN:
                ArrowKeyState[3] = True

            elif event.key == pygame.K_d:
                MoveKeyState[0] = True
            elif event.key == pygame.K_q:
                MoveKeyState[1] = True
            elif event.key == pygame.K_z:
                MoveKeyState[2] = True
            elif event.key == pygame.K_s:
                MoveKeyState[3] = True

            elif event.key == pygame.K_LSHIFT:
                MoveKeyState[4] = True
            elif event.key == pygame.K_LCTRL:
                MoveKeyState[5] = True

        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_RIGHT:
                ArrowKeyState[0] = False
            elif event.key == pygame.K_LEFT:
                ArrowKeyState[1] = False
            elif event.key == pygame.K_UP:
                ArrowKeyState[2] = False
            elif event.key == pygame.K_DOWN:
                ArrowKeyState[3] = False

            elif event.key == pygame.K_d:
                MoveKeyState[0] = False
            elif event.key == pygame.K_q:
                MoveKeyState[1] = False
            elif event.key == pygame.K_z:
                MoveKeyState[2] = False
            elif event.key == pygame.K_s:
                MoveKeyState[3] = False

            elif event.key == pygame.K_LSHIFT:
                MoveKeyState[4] = False
            elif event.key == pygame.K_LCTRL:
                MoveKeyState[5] = False


    if ArrowKeyState[0]:
        rotationy += ROTATION_AMOUNT
    if ArrowKeyState[1]:
        rotationy -= ROTATION_AMOUNT
    if ArrowKeyState[2]:
        rotationx -= ROTATION_AMOUNT
    if ArrowKeyState[3]:
        rotationx += ROTATION_AMOUNT

    if MoveKeyState[0]:
        offset[0] -= cos(rotationy)*MOVE_AMOUNT
        offset[2] += sin(rotationy)*MOVE_AMOUNT
    if MoveKeyState[1]:
        offset[0] += cos(rotationy)*MOVE_AMOUNT
        offset[2] -= sin(rotationy)*MOVE_AMOUNT

    if MoveKeyState[3]:
        offset[0] += sin(rotationy)*MOVE_AMOUNT
        offset[2] += cos(rotationy)*MOVE_AMOUNT
    if MoveKeyState[2]:
        offset[0] -= sin(rotationy)*MOVE_AMOUNT
        offset[2] -= cos(rotationy)*MOVE_AMOUNT

    if MoveKeyState[4]:
        offset[1] -= MOVE_AMOUNT*0.5
    if MoveKeyState[5]:
        offset[1] += MOVE_AMOUNT*0.5
        


    points = original_points + offset


    points = roty(points, rotationy)
    points = rotx(points, rotationx)
    #points = rotz(points, rotationz)

    


    
    trianles_coords = points[faces_index]

    normals = getnormal(trianles_coords)



    camera = np.copy(offset)
    camera*=-1
    camera = roty(camera, rotationy)
    camera = rotx(camera, rotationx)
    camera /= np.sqrt(np.sum(np.square(camera)))
    dots = np.dot(normals, camera)





    drawtriangles = perspective(points)
    drawtriangles = drawtriangles[faces_index]

    average_z = np.sum(trianles_coords[:,:,2], axis=1)/3

    indexs=np.argsort(average_z)
    indexs = indexs[::-1]
    drawtriangles = drawtriangles[indexs]


    for index, triangle in enumerate(drawtriangles):
        if dots[indexs[index]]>-0.2:
            color_triangle = np.clip(dots[indexs[index]],0,1)*255
            pygame.draw.polygon(screen, (color_triangle, color_triangle, color_triangle), triangle, 0)



    clock.tick(100)
    fps = clock.get_fps()
    text_surface = fps_font.render(str(round(fps))+' fps', False, (255, 255, 255))
    screen.blit(text_surface, (0,0))

    pygame.display.flip()


pygame.quit()
