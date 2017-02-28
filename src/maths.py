import itertools
import numpy as np

def jitter(data, depth):
    '''generates indices of the vertices for every
    possible mesh configuration for the given depth.'''
    return [a for a in
            itertools.product([0,1], repeat=len(data))]

def mapVertices(vertices, all_indices, depths):
    '''given indices (likely from jitter()), map the given
    vertices to the depths indicated by all_indices'''
    combs = []
    for indices in all_indices:
        comb = []
        for vtx,i in zip(vertices,indices):
            comb.append(
                np.array([vtx[0],vtx[1],depths[i]]))
        combs.append(comb)
    return combs

def normalizeV3(arr):
    lens = np.sqrt(arr[:,0]**2 + arr[:,1]**2 + arr[:,2]**2) + 0.00001
    arr[:,0] /= lens
    arr[:,1] /= lens
    arr[:,2] /= lens                
    return arr