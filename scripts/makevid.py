import math
import os
import sys

def main():
    
    #gen light positions and lux template files
    radius = 2
    with open('lux_gen.lxs','r') as template:
        lines = ''.join(template.readlines())
        
        for x in xrange(0,360,6):
            temp = lines
            degInRad = math.radians(x)
            X,Z = math.cos(degInRad)*radius, math.sin(degInRad)*radius
            temp = temp.replace('$X','%.3f'%X).replace('$Y','-2.5').replace('$Z','%.3f'%Z)
            
            with open('vid/lux_gen_%d.lxs' % x,'w') as lux_gen:
                lux_gen.write(temp)
                print "Exported scene to lux_gen_%d.lxs" % x
                
    #render those files
    for x in xrange(0,360,6):
        os.system('luxconsole vid/lux_gen_%d.lxs -o ./%d.png' % (x,x))

if __name__ == '__main__':
    main()