import os
import sys
import time

import Image
import numpy as np
import scipy

from OpenGL.arrays import ArrayDatatype as ADT
from OpenGL.arrays import vbo
from OpenGL.GL.ARB.vertex_buffer_object import *
from OpenGL.GL import *
from OpenGL.GL import shaders
from OpenGL.GLUT import *
from OpenGL.GLU import *

import callbacks
import objects

class Application(object):
    def __init__(self, ctx, args):
        
        #Init GLUT and Create Window
        glutInit()
        glutInitWindowSize(800,800)
        glutCreateWindow("Image Relighting v0")
        glutInitDisplayMode(GLUT_DOUBLE| GLUT_RGBA | GLUT_DEPTH)
        
        self.ctx = ctx
        
        #Create Rendering Context
        if ctx == 'jitter':
            self.rc = JitterRenderContext(args)
        elif ctx == 'view_mesh':
            self.rc = ViewMeshRenderContext(args)
        elif ctx == 'recon':
            self.rc = ReconRenderContext(args)
        
        #Init GL and load our shaders
        self.rc.initGL()
        self.rc.initShaders()
        
        #Create UI Elements
        self.ui = None
        
        #Register Callbacks
        self.registerCallbacks()
    
    def displayFunc(self):
        self.rc.render()
        
    def keyboardFunc(self, key, x, y):
        callbacks.keyboardFunc(self.rc, key, x, y)
    
    def mainLoop(self):
        glutMainLoop()
        
    def mouseButton(self, button, mode, x, y):
        callbacks.mouseButton(self.rc, button, mode, x, y)
        
    def mouseMotion(self, x, y):
        callbacks.mouseMotion(self.rc, x, y)
        
    def registerCallbacks(self):
        glutKeyboardFunc(self.keyboardFunc)
        glutSpecialFunc(self.specialFunc)
        glutMouseFunc(self.mouseButton)
        glutMotionFunc(self.mouseMotion)
        glutDisplayFunc(self.displayFunc)
        glutReshapeFunc(self.reshapeFunc)
        glutIdleFunc(self.rc.onTimerFunc)
        
    def reshapeFunc(self, width, height):
        callbacks.reshape(self.rc, width,height)
        
    def specialFunc(self, key, x, y):
        callbacks.specialFunc(self.rc, key, x,y)
        
class JitterRenderContext(object):
    def __init__(self, args):
        self.objects = []
        self.lights  = []
        self.cameras = []
        self.shaders = []

        self.name = 'jitter'

        self.active_template_num = int(args[0])    
        self.active_obj = objects.JitteredMeshObject(self.active_template_num)
        self.active_obj_num = int(args[1])
            
        self.active_lights = []
        self.active_cam = (0.0,0.0,1)
        self.shader = None
        
        self.tVec = [0,0,0]
        self.rVec = [0,0,0]
        self.sVec = [1,1,1]
        
        self.ortho = False
        self.time_val = 0
        
        self.needCompileShader = True
        self.show_vertices = True
        self.show_passthrough = True
        self.show_wireframe = True
        self.show_ppixel = True
        self.show_normals = True
        self.show_lux = True
        
    def initGL(self):
        glClearColor(0.0, 0.0, 0.0, 0.0)
        glClearDepth(1.0)  
        glColor3f(1.0, 1.0, 1.0)
        glPointSize(1.0)
        
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS)
        glEnable(GL_TEXTURE_2D)
        
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        #glOrtho(0.0, 400.0, 400.0, 0.0, 0.1, 100.0)
        #glOrtho(0.0, 1.0, 0.0, 1.0, -1.0, 1.0)
        gluPerspective(45.0, 1.0, .1, 50.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
    def initShaders(self):
        
        vertices    = ('vertices_vs.txt',   'vertices_gs.txt',   'vertices_fs.txt')
        passthrough = ('passthrough_vs.txt','passthrough_gs.txt','passthrough_fs.txt')
        wireframe   = ('wireframe_vs.txt',  'wireframe_gs.txt',  'wireframe_fs.txt')
        ppixel      = ('pvtx_vs.txt',       'pvtx_gs.txt',       'pvtx_fs.txt')
        shownormals = ('shownormals_vs.txt','shownormals_gs.txt','shownormals_fs.txt')
        showlux     = ('showlux_vs.txt',    'showlux_gs.txt',    'showlux_fs.txt')
        
        shader_locs = (vertices,passthrough,wireframe,ppixel,shownormals,showlux)
        for sloc in shader_locs:
            for i,filename in enumerate(sloc):
                filename = './src/shaders/'+filename
                with open(filename,'r') as ofp:
                    if i==0:
                        _VS = (''.join(ofp.readlines()),
                               GL_VERTEX_SHADER)
                    if i==1:
                        _GS = (''.join(ofp.readlines()),
                               GL_GEOMETRY_SHADER)
                    if i==2:
                        _FS = (''.join(ofp.readlines()),
                               GL_FRAGMENT_SHADER)

            #use a single shader and pass in all our needed
            #information as uniform variables
            self.shaders.append(
                shaders.compileProgram(
                    shaders.compileShader(*_VS),
                    shaders.compileShader(*_GS),
                    shaders.compileShader(*_FS)
                )
            )
        self.show_vertices = True
        self.show_passthrough = False
        self.show_wireframe = False
        self.show_ppixel = False
        self.show_normals = False
        self.show_lux = False
        
    def compileShader(self, shader):
        
        shaders.glUseProgram(shader)
        uniforms = (
            'global_ambient',
            'light_ambient',
            'light_diffuse',
            'light_pos',
            'material_ambient',
            'material_diffuse',
            'time',
            'm'
        )
        for uniform in uniforms:
            location = glGetUniformLocation(shader, uniform)
            if location in (None, -1):
                print 'Warning, no uniform: %s' % (uniform)
            setattr(self, uniform, location)
            
        attributes = (
            'vtx_pos',
            'vtx_norm',
            'vtx_texcoord'
        )
        for attribute in attributes:
            location = glGetAttribLocation(shader, attribute)
            if location in (None, -1):
                print 'Warning, no attribute: %s' % (attribute)
            setattr(self, attribute, location)
    
    def exportToLuxRender(self):
        self.active_obj.exportToLuxRender()
            
    def next_obj(self):
        self.active_obj_num = min([len(self.active_obj.jittered_vertices)-1,
                                       self.active_obj_num+1])
        self.active_obj.setMesh(self.active_obj_num)
        
    def next_template(self):
        self.active_template_num = min([10,
                                        self.active_template_num+1])
        self.active_obj.setTemplate(self.active_template_num,
                                    self.active_obj_num)
    
    def prev_obj(self):
        self.active_obj_num = max([0,self.active_obj_num-1])
        self.active_obj.setMesh(self.active_obj_num)
        
    def prev_template(self):
        self.active_template_num = max([1,self.active_template_num-1])
        self.active_obj.setTemplate(self.active_template_num,
                                    self.active_obj_num)
    
    def render(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        
        glTranslatef(*(-1.0 * np.array(self.active_cam)))
        glTranslatef(self.tVec[0], self.tVec[1], self.tVec[2])  
        glRotatef(self.rVec[0], 1,0,0)
        glRotatef(self.rVec[1], 0,1,0)
        glRotatef(self.rVec[2], 0,0,1)
        
        if self.name == 'recon':
            glRotatef(-90.0, 0,0,1)
        
        if self.needCompileShader:
            for shader in self.shaders:
                self.active_shader = shader
                self.compileShader(shader) 
            self.needCompileShader = False
        
        try:
            for i in xrange(0,6):
                
                if   i==0 and not self.show_vertices:
                        continue
                elif i==1 and not self.show_passthrough:
                        continue
                elif i==2 and not self.show_wireframe:
                        continue
                elif i==3 and not self.show_ppixel:
                        continue
                elif i==4 and not self.show_normals:
                        continue
                elif i==5 and not self.show_lux:
                        continue
                    
                if self.show_lux:
                    #glBindTexture(GL_TEXTURE_2D, self.tex)
                    glEnable(GL_TEXTURE_2D)
                    
                shaders.glUseProgram(self.shaders[i])

                self.active_obj.vbo.bind()
                
                glUniform4f(self.global_ambient, .3,.3,.3,.1)
                glUniform4f(self.light_ambient,  .3,.3,.3, 1.0) #activelight.ambient, etc
                glUniform4f(self.light_diffuse,  .6,.6,.6,.6)
                
                #calc light pos after user movement
                light_pos = np.array([0,0,2,0],'f')
                mv = glGetDoublev(GL_MODELVIEW_MATRIX)
                m = glGetFloatv(GL_MODELVIEW_MATRIX)
                glUniformMatrix4fv(self.m, 1, True, m)
                
                light_pos = np.dot(light_pos, np.linalg.inv(np.array(mv)))
                light_pos = light_pos - np.append(self.tVec, 0.0)
                light_pos = light_pos[0:3]
                
                glUniform3f(self.light_pos, *light_pos)
                glUniform4f(self.material_ambient, .2,.2,.2, 1.0)
                glUniform4f(self.material_diffuse, .8,.8,.8, 1)
                
                #animate normal vectors, etc
                glUniform1f(self.time, self.time_val)
                
                try:
                    glEnableVertexAttribArray(self.vtx_pos)
                    glEnableVertexAttribArray(self.vtx_norm)
                    glVertexAttribPointer(
                        self.vtx_pos,
                        3, GL_FLOAT, False, 24, self.active_obj.vbo
                    )
                    glVertexAttribPointer( 
                        self.vtx_norm, 
                        3, GL_FLOAT, False, 24, self.active_obj.vbo+12
                    )
                    glDrawArrays(GL_TRIANGLES, 0, self.active_obj.cnt)
                
                finally:
                    glDisableVertexAttribArray(self.vtx_norm)
                    glDisableVertexAttribArray(self.vtx_pos)        
                    self.active_obj.vbo.unbind()
        finally:
            shaders.glUseProgram(0)
            
        glutSwapBuffers()
    
    def onTimerFunc(self):
        time.sleep(.0025)
        self.time_val += 1.0
        glutPostRedisplay()
        
class ReconRenderContext(JitterRenderContext):
    def __init__(self, args):
        self.objects = []
        self.lights  = []
        self.cameras = []
        self.shaders = []
        
        self.name = 'recon'

        self.active_template_num = 2 
        self.active_obj = objects.ReconMeshObject(self.active_template_num)
        self.active_obj_num = 2
            
        self.active_lights = []
        self.active_cam = (0.0,0.0,1)
        self.shader = None
        
        self.tVec = [0,0,0]
        self.rVec = [0,0,0]
        self.sVec = [1,1,1]
        
        self.ortho = False
        self.time_val = 0
        
        self.needCompileShader = True
        self.show_vertices = True
        self.show_passthrough = True
        self.show_wireframe = True
        self.show_ppixel = True
        self.show_normals = True
        self.show_lux = True
        
        #self.tex = self.active_obj.loadTexFromImg('data/testing_images/tshirt.png')