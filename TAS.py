#TAS.py
"""
Game mode for making and playing TASes, should work, needs testing
"""
import pygame
from pygame.locals import *
import platformer as plt
from copy import deepcopy
import pickle

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
        
def new_frame():
    global events
    plt.g['count'] += 1
    plt.IGT += plt.clock.tick(30)
    plt.evaluate_input(plt.g['count'], bouncer(events.copy()), keysfunc=bouncer(keymaster.copy()))
    plt.move_actors(plt.levels[plt.level], plt.g['count'])
    plt.move_player(plt.levels[plt.level])
    statelist.append((plt.g.copy(), deepcopy(plt.levels[plt.level])))
    eventlist.append(events)
    keyslist.append(keymaster.copy())
    events = []

def select_frame(frame):
    global events, keymaster
    if not frame >= len(statelist):
        plt.g, plt.levels[plt.level] = statelist[frame]
        events = eventlist[frame]
        keymaster = keyslist[frame]
    else:
        print(frame, len(statelist))
        new_frame()
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

def foo(statelist):
    for i, state in enumerate(statelist):
        print("Frame", i, "Count", state[0]['count'])

select_frame(frame)
while True:
    pygame.display.update()
    for e in pygame.event.get():
        if e.type == QUIT or e.type == KEYDOWN and e.key == K_ESCAPE: quit()

        if e.type == KEYDOWN:

            if e.key == K_n: frame += 1 # next
            if e.key == K_b: frame -= 1 # back
            if e.key in [K_n, K_b]: select_frame(frame)

            if e.key == K_w: # what?
                print(plt.g)
                foo(statelist)
            if e.key == K_c: # clear
                statelist = statelist[:frame]
                eventlist = eventlist[:frame]
                keyslist = keyslist[:frame]
                statelist.append((deepcopy(plt.g), deepcopy(plt.levels[plt.level])))
                filename = input("Save as (blank for TAS): ")
                if not filename: filename = "TAS"
                with open(filename, "wb+") as file:
                    pickle.dump((eventlist, keyslist, statelist), file)

            if e.key == K_TAB:
                filename = input("Load from (blank for TAS): ")
                if not filename: filename = "TAS"
                with open(filename, "rb") as file:
                    eventlist, keyslist, statelist = pickle.load(file)
                    frame = 0
                    select_frame(frame)

    screen.blit(get_tastools(), (0, 0))
    pygame.display.update()
