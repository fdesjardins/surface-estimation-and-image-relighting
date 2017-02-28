import sys

import Image
import numpy as np
import scipy.spatial
import pylab as plt
import itertools
from scipy import ndimage

import delaunay

from OpenGL.arrays import ArrayDatatype as ADT
from OpenGL.arrays import vbo
from OpenGL.GL.ARB.vertex_buffer_object import *
from OpenGL.GL import *
from OpenGL.GL import shaders
from OpenGL.GLUT import *
from OpenGL.GLU import *

import maths

import multiprocessing as mp
def find_neighbors(p):
    vertex,faces = p[0],p[1]
    return [f for f in xrange(len(faces)) if vertex in faces[f]]

class RenderObject(object):
    def __init__(self):
        self.template = None
        self.vbo = None
        self.cnt = 0
        
    def load_template(self, filename):
        with open(filename,'r') as ifp:
            data = [map(float, [x,y,0])
                for x,y,z in [line.strip().split()
                    for line in ifp.readlines()]]
        self.template = data
        
    def viewContinuous(self):
        
        def pfit2d(x, y, z, order=3):
            ncols = (order + 1)**2
            G = np.zeros((x.size, ncols))
            ij = itertools.product(range(order+1), range(order+1))
            for k, (i,j) in enumerate(ij):
                G[:,k] = x**i * y**j
            m, _, _, _ = np.linalg.lstsq(G, z)
            return m
        
        def pval2d(x, y, m):
            order = int(np.sqrt(len(m))) - 1
            ij = itertools.product(range(order+1), range(order+1))
            z = np.zeros_like(x)
            for a, (i,j) in zip(m, ij):
                z += a * x**i * y**j
            return z
        
        x,y,z = (self.save_vertices[:,0],
                 self.save_vertices[:,1],
                 self.save_vertices[:,2])
        
        #3rd order, 2d poly
        m = pfit2d(x,y,z)
    
        #evaluate it on a grid
        nx, ny = 75, 75
        xx, yy = np.meshgrid(np.linspace(x.min(), x.max(), nx), 
                             np.linspace(y.min(), y.max(), ny))
        zz = pval2d(xx, yy, m)
    
        #plot it
        plt.imshow(zz, extent=(x.min(), y.max(), x.max(), y.min()))
        plt.scatter(x, y, c=z)
        plt.show()
        
    def loadTexFromImg(self, filename):
        img = Image.open(filename)
        data = np.asarray(img, np.uint8)
        tex = glGenTextures(1)
        glPixelStorei(GL_UNPACK_ALIGNMENT,1)
        glBindTexture(GL_TEXTURE_2D, tex)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, img.size[0], img.size[1], 0, GL_RGB, GL_UNSIGNED_BYTE, data)
        return tex

TEMPLATES_LOCATION = 'data/mesh_templates/'
class JitteredMeshObject(RenderObject):
    def __init__(self, template_num):
        super(JitteredMeshObject,self).__init__()
        
        filename = '%s%dx%d.txt' % (TEMPLATES_LOCATION,template_num,template_num)
        
        #load template data
        self.load_template(filename)

        #16 light positions
        light_pos = [map(float, (x,y,10))
                     for x in xrange(-2,2+1,1)
                     for y in xrange(-2,2+1,1)]
        
        #generate all possible meshes
        self.depths =  [0.0, -.5]
        
        #load template data        
        jittered_indices = maths.jitter(self.template, self.depths[1:])
        self.jittered_vertices = maths.mapVertices(
                                    self.template,
                                    jittered_indices,
                                    self.depths)
        if len(sys.argv)==3:
            self.setMesh(int(sys.argv[2]))
        else:
            self.setMesh(0)

    def exportToLuxRender(self):
        try:
            sys.path.append('/home/forrest/Workspace/lux/build')
            import pylux
        except ImportError:
            print "Couldn't import pylux: see line 67ish in file src/objects.py"
        
        with open('scripts/lux_simple.lxs','r') as template:    
            mesh_data = '''
                "integer indices" [
                $indices
                   ] "point P" [
                $vertices
                ]
            '''
            #fill in the mesh_data template, then put it into the lux template
            mesh_data = mesh_data.replace('$indices',
                                          ''.join(['%d %d %d\n' % (v1,v2,v3)
                                                   for v1,v2,v3 in self.save_faces]))
            mesh_data = mesh_data.replace('$vertices',
                                          ''.join(['%.1f %.1f %.1f\n' % (v1,v2,v3)
                                                   for v1,v2,v3 in self.save_vertices]))
            template = ''.join(template.readlines())
            template = template.replace('$mesh_data',mesh_data)
        
        with open('lux_gen.lxs','w') as lux_gen:
            lux_gen.write(template)
            print "Exported scene to lux_gen.lxs"
        
    def setMesh(self, meshnum):
        
        #construct 2D surface triangulation
        vertices = np.array(self.jittered_vertices[meshnum])
        delaunay = scipy.spatial.Delaunay(vertices[:,0:2])
        faces = delaunay.vertices
        
        #create a map from vertices to neighboring faces
        #for vertex normal computation
        neighboring_faces = []
        [neighboring_faces.append([])
         for _ in vertices]
        
        print "Building params...................."
        params = [(v,faces) for v in xrange(len(vertices))]
        pool = mp.Pool(10)
        nf = pool.map(find_neighbors, params)
        #print nf
        neighboring_faces = nf
    
        #nf[v] = [f
        #         for f in xrange(len(faces))
         #for v in xrange(len(vertices))
         #if  v in faces[f]]

        #use cKDTree to find the 8 nearest neighbors
        #neighbors = delaunay.neighbors
        #ckdt = scipy.spatial.cKDTree(vertices[:,0:2])
        #
        ##print ckdt.query((0,0), min(len(vertices),8))
        #neighbors = -1 * np.ones([len(vertices),8], 'i')
        #for vtx_idx,vtx in enumerate(vertices):
        #    d,i = ckdt.query(vtx[0:2], min(len(vertices),8))
        #    start = np.sqrt(d[1]**2 + d[1]**2)
        #    #print start
        #    for nb_idx,neighbor in enumerate([[_d,_i] for _d,_i in zip(d,i)
        #                                     if (0 < _d <= start+.01)]):
        #        #print nb_idx,neighbor
        #        neighbors[vtx_idx,nb_idx] = neighbor[1]
        
        #compute face normals for each model
        norm = np.zeros(vertices.shape, 'f')
        tris = [vertices[f] for f in faces] #vertices
    
        n = []
        for f in faces:
            vtxs = vertices[f]
            n.append(np.cross(vtxs[2,:] - vtxs[0,:], vtxs[1,:] - vtxs[0,:]))
        n = np.array(n,dtype=n[0].dtype)

        #getting it into our coordinate system:
        #if the z-element is negative, perform a rotation on
        #that normal vector; ensure all the normals face us
        for i in xrange(len(n)):
            if n[i][2] < 0:
                n[i] = -1 * n[i]
        maths.normalizeV3(n)
        
        #use the face normals and neighbors list to compute vertex normals
        for i,f in enumerate(faces):
            for vtx in f:
                for neighboring_face in neighboring_faces[vtx]:
                    norm[vtx] += n[neighboring_face]
        maths.normalizeV3(norm)
        
        #create a view into vertices and normals
        va = vertices[faces]
        no = norm[faces]
        
        #pack into vertex buffer objects
        vtxs = np.array(np.split(va.flatten(), len(va.flatten())/3), 'f')
        norms = np.array(np.split(no.flatten(), len(no.flatten())/3), 'f')
        vertex_data = np.array(
            [[v[0],v[1],v[2], n[0],n[1],n[2]]
            for v,n in zip(vtxs,norms)], 'f'
        )
        self.vbo = vbo.VBO(vertex_data)
        self.cnt = vertex_data.shape[0]
        
        #save faces and vertices for exporting to LuxRender
        self.save_faces, self.save_vertices = faces, vertices
        
    def setTemplate(self, template_num, meshnum):
        filename = '%s%dx%d.txt' % (TEMPLATES_LOCATION, template_num,template_num)
        
        #load template data
        self.load_template(filename)
        
        jittered_indices = maths.jitter(self.template, self.depths[1:])
        self.jittered_vertices = maths.mapVertices(
                                    self.template,
                                    jittered_indices,
                                    self.depths)
        self.setMesh(meshnum)
        
class ReconMeshObject(RenderObject):
    def __init__(self, template_num):
        super(RenderObject,self).__init__()
        
        filename = '%s%dx%d.txt' % (TEMPLATES_LOCATION,template_num,template_num)
        
        #load template data
        self.load_template(filename)

        #16 light positions
        light_pos = [map(float, (x,y,10))
                     for x in xrange(-2,2+1,1)
                     for y in xrange(-2,2+1,1)]
        
        #generate all possible meshes
        self.depths =  [0.0, -.5]
        
        #load template data        
        jittered_indices = maths.jitter(self.template, self.depths[1:])
        self.jittered_vertices = maths.mapVertices(
                                    self.template,
                                    jittered_indices,
                                    self.depths)
        self.setMesh(0)

    def exportToLuxRender(self):
        with open('scripts/lux_reconstruct.lxs','r') as template:    
            mesh_data = '''
                "integer indices" [
                $indices
                    ] "point P" [
                $vertices
                    ] "float uv" [
                $uv    
                    ]
            '''
            #fill in the mesh_data template, then put it into the lux template
            mesh_data = mesh_data.replace('$indices',
                                          ''.join(['%d %d %d\n' % (v1,v2,v3)
                                                   for v1,v2,v3 in self.save_faces]))
            mesh_data = mesh_data.replace('$vertices',
                                          ''.join(['%.5f %.5f %.5f\n' % (v1,v2,v3)
                                                   for v1,v2,v3 in self.save_vertices]))
            
            mesh_data = mesh_data.replace('$uv',
                                          ''.join(['%.5f %.5f\n' % (u,v)
                                                   for u,v in self.save_uv]))
            
            template = ''.join(template.readlines())
            template = template.replace('$texture_image',sys.argv[2])
            template = template.replace('$mesh_data',mesh_data)
            template = template.replace(
                            '$light_pos',
                            '$X $Y $Z')
        
        with open('lux_gen.lxs','w') as lux_gen:
            lux_gen.write(template)
            print "Exported scene to lux_gen.lxs"
        
    def setMesh(self, meshnum):
        
        #construct 2D surface triangulation
        vertices = np.array(self.jittered_vertices[meshnum])

        ## load predicted patches
        print "Loading predictions................"
        with open('pred.txt') as ifp:
            patches = np.array([int(l.strip())
                                for l in ifp.readlines()])
        
        ## load vertex data
        print "Loading vertex data................"
        vertices = np.array([self.jittered_vertices[i]
                             for i in patches])
        
        ## overlay vertices, interpolate z values
        w = h = len(patches)**.5
        mesh = np.zeros((3*w,3*h,3),'f')
        
        i=0
        for r in xrange(0,int(3*w-w),2):
            for c in xrange(0,int(3*h-h),2):
                
                newpatch = np.zeros((3,3,3),'f')
                newpatch[0,:] = vertices[i][0:3]
                newpatch[1,:] = vertices[i][3:6]
                newpatch[2,:] = vertices[i][6:9]
                newpatch[:,:,0:1] += 1
                newpatch[:,:,2] *= -.35
                
                ## amount to shift patch up or down based on
                ## previous patches
                z_shift = 0
                
                if c >= 3:
                    left_patch = mesh[r:r+3,c-3:c]
                    left_patch_zavg = np.mean(left_patch[:,:,2][2])
                    z_shift = (left_patch_zavg + np.mean(newpatch[:,:,2][0])) / 2
                    
                if r >= 3:
                    up_patch = mesh[r-3:r,c:c+3]
                    up_patch_zavg = np.mean(up_patch[:,:,2][:,2])
                    z_shift += (up_patch_zavg + np.mean(newpatch[:,:,2][:,0])) / 2
                    
                if r >= 3 and c >= 3:
                    z_shift /= 2
                    
                newpatch[:,:,0] += r
                newpatch[:,:,1] += c
                newpatch[:,:,2] += z_shift
                
                ##kill existing values, since we're reconstructing
                ##the mesh with overlap
                if r > 0 and c > 0:
                    newpatch[:,:,0][0] = 0
                    newpatch[:,:,1][0] = 0
                    newpatch[:,:,0] *= [0,1,1]
                    newpatch[:,:,1] *= [0,1,1]
                elif r > 0:
                    newpatch[:,:,0][0] = 0
                    newpatch[:,:,1][0] = 0
                elif c > 0:
                    newpatch[:,:,0] *= [0,1,1]
                    newpatch[:,:,1] *= [0,1,1]
                
                mesh[r:r+3,c:c+3]  += newpatch
                mesh[r:r+3,c:c+3,2] = newpatch[:,:,2]

                i+=1
        

        meshshape = mesh.shape
        mesh = np.reshape(mesh,(mesh.shape[0]*mesh.shape[1],3))
        mesh -= np.array([meshshape[0]/3,meshshape[1]/3,0])
        
        ##texture coordinates for texture mapping
        uv = []
        for v in np.arange(0,1,1.0/meshshape[1]):
            for u in np.arange(0,1,1.0/meshshape[0]):
                uv.append(np.array([u,v]))
             
        ##freq-space smoothing   
        x = np.reshape(mesh[:,2],(3*w,3*h))
        #H = ndimage.filters.generic_filter(tofilter, )
        #y = np.random.random((2, 2)).astype(np.float32)
        #z = np.fft.irfft2(np.fft.rfft2(x) * np.fft.rfft2(y, x.shape))
        #mesh[:,2] = np.reshape(z,(z.shape[0]*z.shape[1]))
             
        ##gaussian smoothing, 2d conv   
        mesh[:,2] = np.reshape(
            ndimage.filters.gaussian_filter(
                np.reshape(mesh[:,2],(mesh.shape[0]**.5,mesh.shape[0]**.5)),
                [5,5]),
            mesh.shape[0])
        
        ##median filter
        #mesh[:,2] = np.reshape(
        #    ndimage.filters.median_filter(
        #        np.reshape(mesh[:,2],(mesh.shape[0]**.5,mesh.shape[0]**.5)),
        #        7),
        #    mesh.shape[0])
        
        mesh *= np.array([1.0/np.max(mesh[:,0]),1,1])
        mesh *= np.array([1,1.0/np.max(mesh[:,1]),1])
        
        vertices = np.array(mesh)
        d = scipy.spatial.Delaunay(vertices[:,0:2])
        faces = d.vertices
        
        #create a map from vertices to neighboring faces
        #for vertex normal computation
        neighboring_faces = []
        [neighboring_faces.append([])
         for _ in vertices]
        
        #print "Building params...................."
        #params = [(v,faces) for v in xrange(len(vertices))]
        #pool = mp.Pool(10)
        #nf = pool.map(find_neighbors, params)
        #print nf
        #neighboring_faces = nf
    
        #nf[v] = [f
        #         for f in xrange(len(faces))
         #for v in xrange(len(vertices))
         #if  v in faces[f]]

        #use cKDTree to find the 8 nearest neighbors
        #neighbors = delaunay.neighbors
        #ckdt = scipy.spatial.cKDTree(vertices[:,0:2])
        #
        ##print ckdt.query((0,0), min(len(vertices),8))
        #neighbors = -1 * np.ones([len(vertices),8], 'i')
        #for vtx_idx,vtx in enumerate(vertices):
        #    d,i = ckdt.query(vtx[0:2], min(len(vertices),8))
        #    start = np.sqrt(d[1]**2 + d[1]**2)
        #    #print start
        #    for nb_idx,neighbor in enumerate([[_d,_i] for _d,_i in zip(d,i)
        #                                     if (0 < _d <= start+.01)]):
        #        #print nb_idx,neighbor
        #        neighbors[vtx_idx,nb_idx] = neighbor[1]
        
        #compute face normals for each model
        norm = np.zeros(vertices.shape, 'f')
        tris = [vertices[f] for f in faces] #vertices
    
        n = []
        for f in faces:
            vtxs = vertices[f]
            n.append(np.cross(vtxs[2,:] - vtxs[0,:], vtxs[1,:] - vtxs[0,:]))
        n = np.array(n,dtype=n[0].dtype)

        #getting it into our coordinate system:
        #if the z-element is negative, perform a rotation on
        #that normal vector; ensure all the normals face us
        for i in xrange(len(n)):
            if n[i][2] < 0:
                n[i] = -1 * n[i]
        maths.normalizeV3(n)
        
        #use the face normals and neighbors list to compute vertex normals
        #for i,f in enumerate(faces):
        #    for vtx in f:
        #        for neighboring_face in neighboring_faces[vtx]:
        #            norm[vtx] += n[neighboring_face]
        #maths.normalizeV3(norm)
        
        #create a view into vertices and normals
        va = vertices[faces]
        no = norm[faces]
        
        #pack into vertex buffer objects
        vtxs = np.array(np.split(va.flatten(), len(va.flatten())/3), 'f')
        norms = np.array(np.split(no.flatten(), len(no.flatten())/3), 'f')
        vertex_data = np.array(
            [[v[0],v[1],v[2], n[0],n[1],n[2]]
            for v,n in zip(vtxs,norms)], 'f'
        )
        self.vbo = vbo.VBO(vertex_data)
        self.cnt = vertex_data.shape[0]
        
        #save faces and vertices for exporting to LuxRender
        self.save_faces, self.save_vertices, self.save_uv = faces, vertices, uv
        
    def setTemplate(self, template_num, meshnum):
        filename = '%s%dx%d.txt' % (TEMPLATES_LOCATION, template_num,template_num)
        
        #load template data
        self.load_template(filename)
        
        jittered_indices = maths.jitter(self.template, self.depths[1:])
        self.jittered_vertices = maths.mapVertices(
                                    self.template,
                                    jittered_indices,
                                    self.depths)
        self.setMesh(meshnum)