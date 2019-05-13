"""Shooter

Usage:
    shooter.py 
"""

from game_mode import *
import docopt

if __name__ == "__main__":
    args = sys.argv
    if '-d' in args:
        debug = True
    else:
        debug = False
    if 'test' in args:
        GAME = TestGame((2500, 2500), (1300, 800), debug) # mapsize, screensize, debug_enable
        GAME.run()
    if '1v1client' in args:
        ip = args[2]
        GAME = Multi1v1((2500, 2500), (1300, 800), 'client', debug, ip) # mapsize, screensize, debug_enable
        GAME.run()
    if '1v1server' in args:
        GAME = Multi1v1((2500, 2500), (1300, 800), 'server', debug) # mapsize, screensize, debug_enable
        GAME.run()
