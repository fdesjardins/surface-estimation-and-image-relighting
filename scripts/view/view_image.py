import os
import sys
import numpy as np
from OpenGL.arrays import vbo
from OpenGL.arrays import ArrayDatatype as ADT
from OpenGL.GL.ARB.vertex_buffer_object import *
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from scipy.spatial import Delaunay
from Image import open
 
def initFunc():
   initGL()

def initData():
    global rP
    
    #load texture
    im = open(sys.argv[1])
    try:
        ix, iy, image = im.size[0], im.size[1], im.tostring("raw", "RGBA", 0, -1)
    except SystemError:
        ix, iy, image = im.size[0], im.size[1], im.tostring("raw", "RGBX", 0, -1)
    
    rP.texID = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, rP.texID)
    glPixelStorei(GL_UNPACK_ALIGNMENT,1)
    glTexImage2D(
        GL_TEXTURE_2D, 0, 3, ix, iy, 0,
        GL_RGBA, GL_UNSIGNED_BYTE, image
    )

    texl,text,texr,texb = 0.0,1.0,1.0,0.0
    left,top,right,bottom = -1.0,1.0,1.0,-1.0
    
    vtxs = np.array([
        (left,top,0.0),
        (right,top,0.0),
        (right,bottom,0.0),
        (left,bottom,0.0)
    ],'f')
    triang = Delaunay(vtxs[:,0:2])
    
    interleaved = np.array([
        texl,text, left,top,0.0,
        texr,text, right,top,0.0,
        texr,texb, right,bottom,0.0,
        texl,text, left,top,0.0,
        texr,texb, right,bottom,0.0,
        texl,texb, left,bottom,0.0,
    ],'f')
    
    print interleaved
    
    norms = np.array([(0.0,0.0,1.0) for _ in vtxs], dtype=np.float32)
    rP.points = vbo.VBO(interleaved)
    rP.indices = np.array(triang.vertices, dtype=np.ubyte).flatten()
    #print len(vtxs),len(rP.indices)
    
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

def displayFunc1():
    global rP
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    #glTranslatef(0.0, 0.0, -3.0)

    glPushMatrix()
    
    #glRotatef(rP.rVec[0], 1,0,0)
    #glRotatef(rP.rVec[1], 0,1,0)
    #glRotatef(rP.rVec[2], 0,0,1)
    #glTranslatef(rP.tVec[0], rP.tVec[1], rP.tVec[2])    
    #glScalef(rP.sVec[0], rP.sVec[1], rP.sVec[2])
    
    glTranslatef(rP.tVec[0], rP.tVec[1], rP.tVec[2])  
    glRotatef(rP.rVec[0], 1,0,0)
    glRotatef(rP.rVec[1], 0,1,0)
    glRotatef(rP.rVec[2], 0,0,1)

    try:
        glEnable(GL_TEXTURE_2D)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)
        glBindTexture(GL_TEXTURE_2D, rP.texID)
        
        rP.points.bind()
        try:
            glEnableClientState(GL_VERTEX_ARRAY)
            glEnableClientState(GL_TEXTURE_COORD_ARRAY_EXT)
            glEnableClientState(GL_TEXTURE_COORD_ARRAY)
            glTexCoordPointer(2, GL_FLOAT, 20, rP.points)
            glVertexPointer(3, GL_FLOAT, 20, rP.points+8)
            #glVertexPointerf(rP.points)
            glDrawArrays(GL_TRIANGLES, 0, rP.cnt*2)
        finally:
            glDisableClientState(GL_VERTEX_ARRAY)
            glDisableClientState(GL_TEXTURE_COORD_ARRAY)
            glDisableClientState(GL_TEXTURE_COORD_ARRAY_EXT)
    finally:
        #rP.normals.unbind()
        rP.points.unbind()
        glDisable(GL_TEXTURE_2D)
        
    glPopMatrix()
    
    glutSwapBuffers()

def displayFunc2():
    global rP
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    
        #glTranslatef(0.0, 0.0, -3.0)

    glPushMatrix()
    
    #glRotatef(rP.rVec[0], 1,0,0)
    #glRotatef(rP.rVec[1], 0,1,0)
    #glRotatef(rP.rVec[2], 0,0,1)
    #glTranslatef(rP.tVec[0], rP.tVec[1], rP.tVec[2])    
    #glScalef(rP.sVec[0], rP.sVec[1], rP.sVec[2])
    
    glTranslatef(rP.tVec[0], rP.tVec[1], rP.tVec[2])  
    glRotatef(rP.rVec[0], 1,0,0)
    glRotatef(rP.rVec[1], 0,1,0)
    glRotatef(rP.rVec[2], 0,0,1)

    try:
        #glEnable(GL_TEXTURE_2D)
        #glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        #glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        #glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)
        #glBindTexture(GL_TEXTURE_2D, rP.texID)
        
        rP.points.bind()
        try:
            glEnableClientState(GL_VERTEX_ARRAY)
            #glEnableClientState(GL_TEXTURE_COORD_ARRAY_EXT)
            #glEnableClientState(GL_TEXTURE_COORD_ARRAY)
            #glTexCoordPointer(2, GL_FLOAT, 20, rP.points)
            glVertexPointer(3, GL_FLOAT, 20, rP.points+8)
            #glVertexPointerf(rP.points)
            glDrawArrays(GL_TRIANGLES, 0, rP.cnt)
        finally:
            glDisableClientState(GL_VERTEX_ARRAY)
            #glDisableClientState(GL_TEXTURE_COORD_ARRAY)
            #glDisableClientState(GL_TEXTURE_COORD_ARRAY_EXT)
    finally:
        #rP.normals.unbind()
        rP.points.unbind()
        #glDisable(GL_TEXTURE_2D)
        
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
        factor = 0.01
        rP.tVec[2] += deltaY * factor
        oldMousePos[0], oldMousePos[1] = x, y
    glutPostRedisplay( )

def registerCallbacks():
    glutMouseFunc(mouseButton)
    glutMotionFunc(mouseMotion)

def main():
    glutInit()    
    glutInitWindowSize(400,400)
    glutInitDisplayMode(GLUT_DOUBLE| GLUT_RGBA | GLUT_DEPTH)
    
    glutCreateWindow("Scatter1")
    initFunc()
    initData()
    glutDisplayFunc(displayFunc1)
    registerCallbacks()
    
    #glutCreateWindow("Scatter2")
    #initFunc()
    #glutDisplayFunc(displayFunc2)
    #registerCallbacks()
    
    glutMainLoop()

if __name__ == '__main__':
    main()