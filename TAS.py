#TAS.py
"""
Still gets desyncs, though nowhere near as often...
"""
import pygame
from pygame.locals import *
import platformer as plt
from copy import deepcopy
import sys
import pickle
import os

HEL12 = pygame.font.SysFont("Helvetica", 12)

keymaster = {K_SPACE: False, K_RIGHT: False, K_LEFT: False, K_DOWN: False}
eventlist = []
events = []
keyslist = []
statelist = []
frame = 0

class Event(object):
    def __init__(self, key, type=KEYDOWN):
        self.key = key
        self.type = type
    def __repr__(self):
        return "<key:" + str(self.key) + ", type:" + str(self.type) + ">"

screen = pygame.display.set_mode((640, 480))
pygame.display.set_caption("Super Red Pants Turbo | Cheaters Edition")
plt.sprites = plt.load_spritesheet("platformertileset.png", plt.sheetdata, colorkey=(1, 255, 1))
pygame.draw.rect(plt.sprites['alien2'], (1, 255, 1), pygame.rect.Rect((0, 0), (32, 16)))
plt.wallpaper = plt.load_spritesheet("backgrounds.png", plt.wallpaperdata)
plt.endframe = pygame.image.load('endframe.png').convert()
plt.endframe.set_colorkey((1, 255, 1))

def eventfunc(): return eventlist[frame]
def keysfunc(): return keyslist[frame]
def bouncer(thing): 
    def bounce(thing=thing): return thing
    return bounce

def play_tas():
    global frame
    plt.level = 0
    frame = 0
    plt.level_title(plt.levels[plt.level])
    plt.g = plt.reset()
    plt.flag = True
    plt.IGT = 0
    plt.clock.tick()
    while plt.flag:
        frame += 1
        if frame >= len(eventlist):
            frame -= 1
            break
        plt.g['count'] += 1
        plt.IGT += plt.clock.tick(30)
        plt.evaluate_input(plt.g['count'], eventfunc=eventfunc, keysfunc=keysfunc)
        plt.adjust_scroll()
        plt.move_actors(plt.levels[plt.level], plt.g['count'])
        plt.move_player(plt.levels[plt.level])
        plt.fill_back(plt.levels[plt.level])
        plt.draw_level(plt.levels[plt.level])
        pygame.display.update()
    plt.flag = 1
    while plt.flag:
        plt.clock.tick(30)
        plt.fill_back(plt.levels[plt.level])
        plt.screen.blit(plt.endframe, (0, 0))
        plt.screen.blit(plt.HEL32.render(str(plt.IGT // 60000) +":"+ ("0" + str(plt.IGT // 1000 % 60))[-2:], 0, (0, 0, 0)),(180, 160))
        pygame.display.update()
        for e in pygame.event.get():
            if e.type == QUIT or e.type == KEYDOWN and e.key == K_ESCAPE: quit()
            elif e.type == KEYDOWN and e.key == K_SPACE and plt.count >= 30: flag = False

def new_frame():
    global events
    plt.g['count'] += 1
    plt.IGT += plt.clock.tick(30)
    plt.evaluate_input(plt.g['count'], bouncer(events.copy()), keysfunc=bouncer(keymaster.copy()))
    plt.move_actors(plt.levels[plt.level], plt.g['count'])
    plt.move_player(plt.levels[plt.level])
    statelist.append((deepcopy(plt.g), deepcopy(plt.levels[plt.level])))
    eventlist.append(events)
    keyslist.append(keymaster.copy())
    events = []

def select_frame(frame):
    global events, keymaster
    if not frame >= len(statelist):
        plt.g, plt.levels[plt.level] = statelist[frame]
        events = eventlist[frame]
        keymaster = keyslist[frame]
    else: new_frame()
    plt.adjust_scroll()
    plt.fill_back(plt.levels[plt.level])
    plt.draw_level(plt.levels[plt.level])

def get_tastools():
    surf = pygame.Surface(((640, 14)))
    surf.fill((255, 255, 255))
    surf.blit(HEL12.render(str(frame), 0, (0, 0, 0)), (2, 2))
    for i, key in enumerate([K_SPACE, K_DOWN, K_LEFT, K_RIGHT]):
        if keymaster[key]: pygame.draw.rect(surf, (255, 0, 0), pygame.rect.Rect(((i*48)+122, 2,), (46, 12)))
        surf.blit(HEL12.render(str(key), 0, (0, 0, 0)), ((i*48)+122, 2))
    surf.blit(HEL12.render(repr(events), 0, (0, 0, 0)), (314, 2))
    return surf

def make_event(type=KEYDOWN):
    while True:
        for e in pygame.event.get():
            if e.type == QUIT: quit()
            if e.type == KEYDOWN:
                events.append(Event(e.key, type=type))
                return

def flush():
    global frame, statelist
    statelist = []
    plt.level = 0
    frame = 0
    plt.level_title(plt.levels[plt.level])
    plt.g = plt.reset()
    plt.flag = True
    plt.IGT = 0
    plt.clock.tick()
    while plt.flag:
        statelist.append((deepcopy(plt.g), deepcopy(plt.levels[plt.level])))
        frame += 1
        if frame >= len(eventlist):
            frame -= 1
            break
        plt.g['count'] += 1
        plt.IGT += plt.clock.tick(30)
        plt.evaluate_input(plt.g['count'], eventfunc=eventfunc, keysfunc=keysfunc)
        plt.adjust_scroll()
        plt.move_actors(plt.levels[plt.level], plt.g['count'])
        plt.move_player(plt.levels[plt.level])
        plt.fill_back(plt.levels[plt.level])
        plt.draw_level(plt.levels[plt.level])
        pygame.display.update()


def foo(statelist):
    for i, state in enumerate(statelist):
        print("Frame", i, "Count", state[0]['count'])

def find_desync(statelist):
    c = 0
    for frame, state in enumerate(statelist):
        if state[0]['count'] != c+1: 
            if state[0]['count'] == 0: print("new level ", frame)
            else: print("desync frame ", frame)
        c = state[0]['count']

def load(filename):
    global eventlist, keyslist, statelist
    with open(filename, "rb") as file:
        eventlist, keyslist, statelist = pickle.load(file)
        frame = 0
        select_frame(frame)

plt.level = 0
frame = 0
plt.level_title(plt.levels[plt.level])
plt.g = plt.reset()
statelist.append((deepcopy(plt.g), deepcopy(plt.levels[plt.level])))
eventlist.append(events)
keyslist.append(keymaster.copy())
try:
    with open(sys.argv[-1], "rb") as file:
        eventlist, keyslist, statelist = pickle.load(file)
        frame = 0
    play_tas()
except:
    pass

while True:
    pygame.display.update()
    for e in pygame.event.get():
        if e.type == QUIT or e.type == KEYDOWN and e.key == K_ESCAPE: quit()

        if e.type == KEYDOWN:

            if e.key == K_n: frame += 1 # next
            if e.key == K_b: frame -= 1 # back
            if e.key in [K_n, K_b]: select_frame(frame)

            if e.key == K_j:

                try:
                    frame = int(input("Jump to frame : "))
                    select_frame(frame)
                except TypeError: pass

            if e.key == K_w: # what?
                print(plt.g)
                foo(statelist)
            if e.key == K_SLASH:
                find_desync(statelist)
            if e.key == K_c: # clear
                statelist = statelist[:frame]
                eventlist = eventlist[:frame]
                keyslist = keyslist[:frame]
                statelist.append((deepcopy(plt.g), deepcopy(plt.levels[plt.level])))
                eventlist.append(events)
                keyslist.append(keymaster.copy())

            if e.key == K_d: make_event() # keydown event
            if e.key in keymaster:  # key toggle
                keymaster[e.key] = False if keymaster[e.key] else True
            if e.key == K_p: play_tas() # play
            if e.key == K_o: flush()

            if e.key == K_RETURN:
                filename = input("Save as (blank to cancel): ")
                if os.path.isfile(filename):
                    if input("Overwrite? Are you sure?") in ["N", "n", "no"]:
                        filename = None
                if filename:        
                    with open(filename, "wb+") as file:
                        pickle.dump((eventlist, keyslist, statelist), file)

            if e.key == K_TAB:
                filename = input("Load from (blank for cancel): ")
                if filename:
                    load(filename)
    screen.blit(get_tastools(), (0, 0))
    pygame.display.update()
