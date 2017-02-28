#!/usr/bin/env python

import sys
sys.path.append('src')

import render

def checkArgs(argv):
    return argv[1],argv[2:]

def main():
    
    if len(sys.argv) < 2:
        print 'usage: python main.py [jitter|view_mesh|view_image|predict_one|recon] [args]'
        sys.exit(-1)
    else:
        ctx,args = checkArgs(sys.argv)
        app = render.Application(ctx,args)
        app.mainLoop()

if __name__ == '__main__':
    main()