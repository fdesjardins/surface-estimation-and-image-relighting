import os
import sys

import cPickle
import numpy as np
import scipy.spatial

sys.path.append('../src')
import maths

try:
    sys.path.append('/home/forrest/Workspace/lux/build')
    import pylux
except ImportError:
    print "Couldn't import pylux: see line 11"

class RenderObject(object):
    def __init__(self):
        self.active_light = None
        self.template = None
        self.cnt = 0
        
    def load_template(self, filename):
        with open(filename,'r') as ifp:
            data = [map(float, [x,y,0])
                for x,y,z in [line.strip().split()
                    for line in ifp.readlines()]]
        self.template = data

class MeshObject(RenderObject):
    def __init__(self, template_num):
        super(MeshObject,self).__init__()
        
        filename = '../data/mesh_templates/%dx%d.txt' % (template_num,template_num)
        
        #load template data
        self.load_template(filename)

        # light positions
        self.light_pos = [map(float, (x,y,z))
                         for x in xrange(-2, 2+1, 1)
                         for y in xrange(-1,-7-1,-3)
                         for z in xrange(-2, 2+1, 1)]
        #print self.light_pos, len(self.light_pos)
        
        #generate all possible meshes
        self.depths =  [(0.00,-.10),
                        #(0.00,-.35),
                        (0.00,-.75)]
        
        #load template data        
        jittered_indices = maths.jitter(self.template, self.depths[1:])
        self.jittered_vertices = sum([maths.mapVertices(
                                    self.template,
                                    jittered_indices,
                                    depths) for depths in self.depths],[])
        
        print self.jittered_vertices[0]
        print 'len: %d' % len(self.jittered_vertices)
        
        if len(sys.argv)==3:
            self.setMesh(int(sys.argv[2]))
        else:
            self.setMesh(0)

    def exportToLux(self):
        
        with open('lux_simple.lxs','r') as template:    
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
            template = template.replace(
                            '$light_pos',
                            '%.2f %.2f %.2f' % (self.active_light[0],
                                                self.active_light[1],
                                                self.active_light[2]))
        
        with open('lux_gen.lxs','w') as lux_gen:
            lux_gen.write(template)
            print "Exported scene to lux_gen.lxs"
            
    def jitter(self):
        jittered_indices = maths.jitter(self.template, self.depths[1:])
        self.jittered_vertices = [maths.mapVertices(
                                    self.template,
                                    jittered_indices,
                                    depths) for depths in self.depths[0]]
        
    def renderInLux(self, mesh_num):
        for i in xrange(len(self.light_pos)):
            self.setLight(i)
            self.exportToLux()
            ctx = pylux.Context('export') #start a rendering context
            ctx.parse('./lux_gen.lxs', False) #use lux_gen.lxs as our scene file
            #write out each rendered illumination patch
            os.system('mv luxout.png %dx%d/%d_%d.png' % (MESH_TEMPLATE,MESH_TEMPLATE,mesh_num,i))
    
    def setLight(self, lightnum):
        self.active_light = self.light_pos[lightnum]
        
    def setMesh(self, meshnum):
        
        #construct 2D surface triangulation
        vertices = np.array(self.jittered_vertices[meshnum])
        delaunay = scipy.spatial.Delaunay(vertices[:,0:2])
        faces = delaunay.vertices
        
        #save faces and vertices for exporting to LuxRender
        self.save_faces, self.save_vertices = faces, vertices
        return self
    
    def setCustomMesh(self, mesh):
        
        self.active_light = (0,-3,0)
        
        #construct 2D surface triangulation
        vertices = np.array(mesh)
        delaunay = scipy.spatial.Delaunay(vertices[:,0:2])
        faces = delaunay.vertices
        
        #save faces and vertices for exporting to LuxRender
        self.save_faces, self.save_vertices = faces, vertices
        
        self.exportToLux()
        ctx = pylux.Context('export') #start a rendering context
        ctx.parse('./lux_gen.lxs', False) #use lux_gen.lxs as our scene file
        
        return self
        
    def setTemplate(self, template_num):
        filename = '../data/mesh_templates/%dx%d.txt' % (template_num,template_num)
        
        #load template data
        self.load_template(filename)

MESH_TEMPLATE = 2

def main():
    
    #load mesh template
    obj = MeshObject(MESH_TEMPLATE)
    
    #perform pertubation of vertices
    #obj.jitter()
    
    print len(obj.jittered_vertices)
    
    #generate light positions
    with open('%dx%d/labels.txt' % (MESH_TEMPLATE,MESH_TEMPLATE),'w') as ofp:
        
        #render each mesh configuration in luxrender
        for i in xrange(0,len(obj.jittered_vertices)):
            obj.setMesh(i)
            obj.renderInLux(i)
            cPickle.dump(obj.save_vertices, ofp, cPickle.HIGHEST_PROTOCOL)
    
    #reduce the output images to 3x3 pixels
    pass

if __name__ == '__main__':
    main()