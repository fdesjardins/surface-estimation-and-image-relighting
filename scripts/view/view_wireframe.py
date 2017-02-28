import os
import sys
import numpy as np
import pygame
from OpenGL.arrays import vbo
from OpenGL.arrays import ArrayDatatype as ADT
from OpenGL.GL.ARB.vertex_buffer_object import *
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from scipy.spatial import Delaunay
 
def initFunc():
   initDataVBO()
   initGL()
   registerCallbacks()

def initDataVBO():
    global rP
    fp = sys.argv[1]
    
    print "Loading vertex data..."
    vtxs = np.array([(float(x),float(y),float(z))
                     for x,y,z in [line.strip().split()
                                  for line in open(fp,'r').readlines()]], dtype=np.float32)
    
    #with open('%s.obj'%sys.argv[1],'w') as of:
    #    [of.write('v %.3f %.3f %.3f\n' % (x,y,z)) for x,y,z in vtxs]
    
    print "Computing Delaunay triangulation..."
    triang = Delaunay(vtxs[:,0:2])
    print triang.vertices
    
    norms = np.array([(0.0,0.0,1.0) for _ in vtxs], dtype=np.float32)
    #rP.points = vbo.VBO(np.array(zip(norms,vtxs),dtype=np.float32))
    rP.points = vbo.VBO(vtxs)
    
    #rP.indices = np.array(range(len(vtxs)),dtype=np.ubyte)
    
    rP.indices = np.array(triang.vertices, dtype=np.ubyte).flatten()
    
    print len(vtxs),len(rP.indices)
    
    rP.normals = vbo.VBO(norms)
    rP.cnt = len(vtxs)

zero = (0,0,0,0)
one = (1,1,1,1)
lpos = (0,0,1,0)
def initGL():
   
    glClearColor(0.0, 0.0, 0.0, 0.0)
    glClearDepth(1.0)  
    glColor3f(1.0, 1.0, 1.0)
    glPointSize(1.0)
    
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LESS)
    glShadeModel(GL_SMOOTH)
    glEnable(GL_NORMALIZE)
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
    
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glLightfv(GL_LIGHT0, GL_AMBIENT, zero)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, one)
    glLightfv(GL_LIGHT0, GL_SPECULAR, one)
    glLightfv(GL_LIGHT0, GL_POSITION, lpos)
    
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45.0, 1.0, .1, 100.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(0.0,0.0,1.0, 0.0,0.0,0.0, 0.0,0.0,1.0)

def displayFunc():
    global rP
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    glTranslatef(0.0, 0.0, -3.0)

    glPushMatrix()
    
    glRotatef(rP.rVec[0], 1,0,0)
    glRotatef(rP.rVec[1], 0,1,0)
    glRotatef(rP.rVec[2], 0,0,1)
    glTranslatef(rP.tVec[0], rP.tVec[1], rP.tVec[2])    
    glScalef(rP.sVec[0], rP.sVec[1], rP.sVec[2])

    try:
        rP.points.bind()
        try:
            glEnableClientState(GL_VERTEX_ARRAY);
            glVertexPointerf(rP.points)
            #rP.normals.bind()
            #glNormalPointerf(rP.normals)
            glDrawArrays(GL_POINTS, 0, rP.cnt)
            #glDrawElements(
            #    GL_TRIANGLES, len(rP.indices), GL_UNSIGNED_INT, rP.indices
            #)
        finally:
            glDisableClientState(GL_VERTEX_ARRAY);
    finally:
        #rP.normals.unbind()
        rP.points.unbind()
        
    glPopMatrix()
    
    glutSwapBuffers()

class renderParam(object):
    def __init__(self):
        self.mouseButton = None
        self.tVec = [0, 0, 0]
        self.rVec = [0, 0, 0]
        self.sVec = [1, 1, 1]
        self.points = None
        self.indices = None
        self.cnt = 0

    def reset(self):
        self.mouseButton = None
        self.tVec = [0, 0, 0]
        self.rVec = [0, 0, 0]
        self.sVec = [1, 1, 1]
        self.points = None
        self.indices = None
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
    glutInit()    
    glutInitWindowSize(400,400)
    glutCreateWindow("Scatter")
    glutInitDisplayMode(GLUT_DOUBLE| GLUT_RGBA | GLUT_DEPTH)
    
    initFunc()
    glutMainLoop()

if __name__ == '__main__':
    main()