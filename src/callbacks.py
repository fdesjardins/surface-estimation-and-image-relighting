from OpenGL.GL import *
from OpenGL.GLUT import * 
from OpenGL.GLU import *

def keyboardFunc(render_context, key, x, y):  
    if key == 'n':
        render_context.show_normals = not render_context.show_normals
    elif key == 'p':
        render_context.show_ppixel = not render_context.show_ppixel
    elif key == 'w':
        render_context.show_wireframe = not render_context.show_wireframe
    elif key == 't':
        render_context.show_passthrough = not render_context.show_passthrough
    elif key == 'v':
        render_context.show_vertices = not render_context.show_vertices
    elif key == 'o':
        render_context.ortho = not render_context.ortho
        reshape(render_context, render_context.width, render_context.height)
    elif key == 'e':
        if not render_context.show_lux:
            render_context.exportToLuxRender()
        render_context.show_lux = not render_context.show_lux
    elif key == 'c':
        
        glutCreateWindow("Continuous")
        glutDisplayFunc(render_context.render);
        
        render_context.active_obj.viewContinuous()
        
    glutPostRedisplay()
    
def specialFunc(render_context, key, x, y):
    if key == 100:
        #print 'left'
        render_context.prev_obj()
    elif key == 101:
        #print 'up'
        render_context.next_template()
    elif key == 102:
        #print 'right'
        render_context.next_obj()
    elif key == 103:
        #print 'down'
        render_context.prev_template()
    glutPostRedisplay()

oldMousePos = [0, 0]
def mouseButton(render_context, button, mode, x, y):
    global oldMousePos
    if mode == GLUT_DOWN:
        render_context.mouseButton = button
        if button == 3:
            factor = 0.2
            render_context.tVec[2] += -1 * factor
        elif button == 4:
            factor = 0.2
            render_context.tVec[2] += 1 * factor
    else:
        #print button
        render_context.mouseButton = None
    oldMousePos[0], oldMousePos[1] = x, y
    glutPostRedisplay()

def mouseMotion(render_context, x, y):
    global oldMousePos
    deltaX = x - oldMousePos[ 0 ]
    deltaY = y - oldMousePos[ 1 ]
    
    if render_context.mouseButton == GLUT_LEFT_BUTTON:
        factor = 0.005
        render_context.tVec[0] += deltaX * factor
        render_context.tVec[1] -= deltaY * factor
        oldMousePos[0], oldMousePos[1] = x, y
    if render_context.mouseButton == GLUT_RIGHT_BUTTON:
        factor = 0.1
        render_context.rVec[0] += deltaY * factor
        render_context.rVec[1] += deltaX * factor
        oldMousePos[0], oldMousePos[1] = x, y
    if render_context.mouseButton == GLUT_MIDDLE_BUTTON:
        factor = 0.01
        render_context.tVec[2] += deltaY * factor
        oldMousePos[0], oldMousePos[1] = x, y

    glutPostRedisplay()
    
def reshape(render_context, width, height):
    glViewport(0,0,width,height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    
    if render_context.ortho:
        glOrtho(-1.0, 1.0, -1.0, 1.0, 0.1, 50.0)
    else:
        gluPerspective(45.0, float(width)/height, .1, 50.)
        
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    
    render_context.width = width
    render_context.height = height