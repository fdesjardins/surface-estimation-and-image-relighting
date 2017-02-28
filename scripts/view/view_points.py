import os
import sys
import numpy as np
from OpenGL.arrays import vbo
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

def initFunc():
   initDataVBO()
   initGL()
   registerCallbacks()

def initDataVBO():
    global rP
    fp = sys.argv[1]
    vtxs = np.array([(float(x),float(y),float(z))
                     for x,y,z in [line.strip().split()
                                  for line in open(fp,'r').readlines()]], dtype=np.float32)
    #x,y,z = [vtxs[:,i] for i in range(3)]
    rP.vbo = vbo.VBO(vtxs)
    rP.cnt = len(vtxs)

def initGL():
    glutInit()    
    glutInitWindowSize(400,400)
    glutCreateWindow("Scatter")
    glutInitDisplayMode(GLUT_SINGLE | GLUT_RGBA)
    
    glClearColor(0.0, 0.0, 0.0, 1.0)
    glColor3f(1.0, 1.0, 1.0)
    glPointSize(1.0)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    #gluOrtho2D(0.0,400.0,0.0,400.0)
    gluPerspective(45.0, 1.0, .1, 10000.0)
    gluLookAt(0.0,0.0,1.0, 0.0,0.0,0.0, 0.0,0.0,1.0)

def displayFunc():
    global rP
    glClear(GL_COLOR_BUFFER_BIT)
    glLoadIdentity()

    glPushMatrix()
    glRotatef(rP.rVec[0], 1,0,0)
    glRotatef(rP.rVec[1], 0,1,0)
    glRotatef(rP.rVec[2], 0,0,1)
    glTranslatef(rP.tVec[0], rP.tVec[1], rP.tVec[2])    
    glScalef(rP.sVec[0], rP.sVec[1], rP.sVec[2])
    try:
        rP.vbo.bind()
        try:
            glEnableClientState(GL_VERTEX_ARRAY);
            glVertexPointerf(rP.vbo)
            glDrawArrays(GL_POINTS, 0, rP.cnt)
        finally:
            glDisableClientState(GL_VERTEX_ARRAY);
    finally:
        rP.vbo.unbind()  
    glPopMatrix()
    
    glFlush()

class renderParam(object):
    def __init__(self):
        self.mouseButton = None
        self.tVec = [0, 0, 0]
        self.rVec = [0, 0, 0]
        self.sVec = [1, 1, 1]
        self.vbo = None
        self.cnt = 0

    def reset(self):
        self.mouseButton = None
        self.tVec = [0, 0, 0]
        self.rVec = [0, 0, 0]
        self.sVec = [1, 1, 1]
        self.vbo = None
        self.cnt = 0
        
rP = renderParam()
oldMousePos = [0, 0]
def mouseButton(button, mode, x, y):
    global rP, oldMousePos
    if mode == GLUT_DOWN:
        rP.mouseButton = button
    else:
        rP.mouseButton = None
    oldMousePos[0], oldMousePos[1] = x, y
    glutPostRedisplay( )

def mouseMotion(x, y):
    global rP, oldMousePos
    deltaX = x - oldMousePos[ 0 ]
    deltaY = y - oldMousePos[ 1 ]
    if rP.mouseButton == GLUT_LEFT_BUTTON:
        factor = 0.005
        rP.tVec[0] += deltaX * factor
        rP.tVec[1] -= deltaY * factor
        oldMousePos[0], oldMousePos[1] = x, y
    if rP.mouseButton == GLUT_RIGHT_BUTTON:
        factor = 0.1
        rP.rVec[0] += deltaY * factor
        rP.rVec[1] += deltaX * factor
        oldMousePos[0], oldMousePos[1] = x, y
    if rP.mouseButton == GLUT_MIDDLE_BUTTON:
        factor = 0.05
        rP.sVec[0] += deltaX * factor
        rP.sVec[1] += deltaY * factor
        oldMousePos[0], oldMousePos[1] = x, y

    glutPostRedisplay( )

def registerCallbacks():
    glutMouseFunc(mouseButton)
    glutMotionFunc(mouseMotion)
    glutDisplayFunc(displayFunc)

def main():
    initFunc()
    glutMainLoop()

if __name__ == '__main__':
    main()