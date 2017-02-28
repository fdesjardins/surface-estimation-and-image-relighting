import os
import sys

import cPickle
import Image as pil
import multiprocessing as mp
import numpy as np
import time

from scipy import ndimage
from sklearn import svm

##dummy method for now. we need a message-passing algorithm
##plus additional heuristics
def icm_map_assign(images, preds):
    return preds

def extract_patch(image, x, y, size):
    patch = [image[x+xoff,y+yoff]
             for xoff in xrange(size)
             for yoff in xrange(size)]
    patch = np.array(patch)
    
    ## energy normalize each patch
    patch = (patch-np.mean(patch))/( (np.var(patch)+.000001)**.5)
    #patch = patch / np.max(patch)
    
    return np.reshape(patch, (1,64))

def predict_patch(params):
    classifiers,patch = params[0],params[1]
    results = [classifiers[i].decision_function(patch)
               for i in xrange(len(classifiers))]
    return results

def predict_patches(classifiers, patches):
    params = [(classifiers,patches[i])
              for i in xrange(len(patches))]
    
    pool = mp.Pool(5)
    print len(patches),len(params[0][0])
    preds = pool.map(predict_patch, params)
    return preds

def extract_patches(image):
    patches = np.array([extract_patch(image, x,y,PATCH_SIZE)
                for x in xrange(0,image.shape[0]-PATCH_SIZE+1,PATCH_SIZE)
                for y in xrange(0,image.shape[1]-PATCH_SIZE+1,PATCH_SIZE)])
    return patches

def predict_image(classifiers, image):
    patches = extract_patches(image)
    preds = predict_patches(classifiers, patches)
    return np.array(preds)

def predict_images(classifiers, images):
    results = [predict_image(classifiers,image)
               for image in images]
    return results

NUM_SVMS = 512
PATCH_SIZE = 8
IMG_NUM = 10

def predict():
    
    #TESTING_IMAGES = 'scripts/2x2/$mn_%d.png' % IMG_NUM
    #TESTING_IMAGES = 'scripts/2x2/0_25.png'
    #TESTING_IMAGES = 'data/testing_images/Img001_01.bmp'
    #TESTING_IMAGES = 'data/testing_images/gradient.png'
    TESTING_IMAGES = 'data/testing_images/candles.jpg'
    #TESTING_IMAGES = 'data/img300x400/SET054/Img001_01.bmp'
    
    if sys.argv == 2: TESTING_IMAGES = sys.argv[1]
    
    print TESTING_IMAGES
    
    ## use best C as found during grid search
    SVMS = 'scripts/2x2_svms/features_C%d.dat' % 10
    
    ## load classifiers
    print "Loading classifiers.................."
    with open(SVMS,'rb') as fp:
        classifiers = [cPickle.load(fp)
                       for r in np.arange(1,NUM_SVMS+1)]

    ## load input images, predict
    print "Loading images......................."
    #images = [np.array(pil.open(TESTING_IMAGES.replace('$mn',str(i))).resize((8,8)).convert('L'))
    #          for i in xrange(20)]
    #images = [np.array(pil.open(TESTING_IMAGES).resize((1536,1536)).convert('L'))]
    images = [np.array(pil.open(TESTING_IMAGES).resize((768,768)).convert('L'))]
    #images = [ndimage.filters.gaussian_filter(im,[12,12]) for im in images]
    
    print "Classifying image patches............"
    preds = predict_images(classifiers, images)
    
    print "Performing MAP assignment............"
    preds = icm_map_assign(images, preds)
    
    ## save results
    with open('pred.txt','w') as ofp:
        for i,p in enumerate(preds[0]):
            s = np.sort(np.abs(p.flatten()))[0]
            ofp.write("%d\n" % np.where(np.abs(p.flatten())==s)[0][0])
               
    print 'done'    

if __name__ == '__main__':
    predict()