import numpy as np

for N in range(1,10+1,1):
    vtxs = [(x,y,0.0) for x in np.arange(-1,1+0.1,2.0/N)
            for y in np.arange(-1,1+0.1,2.0/N)]
    with open(str(N)+'x'+str(N)+'.txt','w') as ofp:
            [ofp.write('%.3f %.3f %.3f\n' % (x,y,z))
             for x,y,z in vtxs]