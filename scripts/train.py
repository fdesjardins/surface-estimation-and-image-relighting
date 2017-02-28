import os
import sys

import cPickle
import Image as pil
import itertools
import multiprocessing as mp
import numpy as np
import time

from sklearn import svm

def initSVMs(all_features, all_labels, C):
    
    def mkParam(features,labels,c):
        
        X = np.array(features)
        Y = np.array(labels)
        weak = svm.SVC(kernel='rbf',C=c)
        return (X,Y,weak)
    
    for lab in all_labels:
        yield mkParam(all_features,lab,C)

def _train(p):
    
    X,Y,learner = p[0],p[1],p[2]
    model = learner.fit(X,Y)
    return model

def trainSVMs(imgs, mesh_labels, C):
    
    ## energy-normalize each patch
    print '    performing normalization..........'
    features = []
    for img in imgs:
        features.append(
            (img-np.mean(img)) / ( (np.var(img)+.000001)**.5 )
        )
    features = np.array(features)
    
    ## stores the list of data and parameters for
    ## all svms so we can use multiprocessing below
    params = initSVMs(features, mesh_labels, C)

    #print 'params len: ', len(params)
    ## train the svms using the params we stored
    print '    training svms.....................'
    
    ## Global processing pool
    pool = mp.Pool(8)
    classifiers = []
    N = 8
    for i in xrange(len(mesh_labels)/N+1):
        somelearners = pool.map(_train, itertools.islice(params,N))
        classifiers.extend(somelearners)
        time.sleep(.5)
        sys.stdout.write('%d...' % i)
        if i % 8 == 0: sys.stdout.write('\n')
    
    print '    trained %d classifiers.............' % len(classifiers)
    
    return classifiers

def train():
    
    NLP = numlightpos = 27
    
    ## load illumination patches
    print 'Loading illumination patches............'
    
    def load(img_loc, img,var):
        if img % 100 == 0 and var == 0:
            sys.stdout.write('%d...' % img)
        return np.array(pil.open(img_loc),'uint32')[:,:,0].reshape(1,-1)[0]
    
    imgs = np.array([load('scripts/2x2/%d_%d.png' % (img,var), img,var)
            for img in xrange( (len(os.listdir('scripts/2x2'))-1)/NLP)
            for var in xrange(NLP)])
    
    sys.stdout.write('\n')
    
    ## generate labels
    #111000000....
    #000111000....
    #000000111....
    print "Generating labels......................"
    i = 0
    labels = np.zeros((len(imgs)/NLP,len(imgs)),'int8')
    for i in xrange(len(imgs)/NLP):
        y = NLP*i
        for x in xrange(len(imgs)):
            labels[i,x] = 1 if x>=y and x<=y+NLP else 0
        if i % 100 == 0: sys.stdout.write('%d...' % i)
    sys.stdout.write('\n')
    
    ## split into training/testing
    
    ## train classifiers
    ## grid search over C/Gamma
    print "Training classifiers................."
    for C in [1,10,100,1000,10000]: #for G in [.01,.001,.0001]
        
        print '  C=%f' % C
        svms = trainSVMs(imgs, labels, C)

        print "Saving classifiers..................."
        fp = open('scripts/2x2_svms/features_C%d.dat' % C,'w')
        for i,s in enumerate(svms):
            cPickle.dump(s, fp, cPickle.HIGHEST_PROTOCOL)
        fp.close()
    
if __name__ == '__main__':
    sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)
    train()