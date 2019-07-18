#leveleditor.py
import sys
import pygame
from pygame.locals import *
from platformer import load_spritesheet, sheetdata, wallpaperdata

pygame.init()
SCROLLER = [0, 0]
CURSOR = [0, 0]
CORNER = None
screen = pygame.display.set_mode((640, 480))
pygame.display.set_caption("Level Editor")

sprites = load_spritesheet('platformertileset.png', sheetdata, colorkey=(1, 255, 1))
wallpaper = load_spritesheet('backgrounds.png', wallpaperdata)
filename = ""

level = {
    "spawn": (2, 2),
    "title" : None,
    "platforms": [],
    "spikes": [],
    "grapes": [],
    "ayys": [],
    "lasers": [],
    "barrels": [],
    "ships": [],
    "diamond": None,
    "background": None
}
colormap = {
    K_1: 'pink',
    K_2: 'red',
    K_3: 'white',
    K_4: 'brwn'
}
backgroundmap = {
    K_0: 'blue',
    K_9: 'red',
    K_8: 'white',
    K_7: 'green',
}
actormap = {
    K_s: 'spikes',
    K_a: 'ayys',
    K_b: 'barrels',
    K_g: 'grapes',
}

if len(sys.argv) > 1:
    filename = sys.argv[-1]
    pygame.display.set_caption("Level Editor / "+filename)
    if filename:
        try:
            with open(filename, "r") as f:
                level = eval(f.read())
        except IOError:
            level['title'] = input("Level tile:")
            with open(filename, "w+") as f:
                f.write(repr(level))
def fill_back():
    for y in range(-1, int(screen.get_height() / 96)+1):
        for x in range(-1, int(screen.get_width() / 96)+1):
            screen.blit(wallpaper[level['background']], ((x * 96) + SCROLLER[0]%96, (y * 96) + SCROLLER[0]%96))

def makeplatform(color):
    global CORNER
    pos = min(CORNER[0] + SCROLLER[0], CURSOR[0] + SCROLLER[0]), min(CORNER[1] + SCROLLER[1], CURSOR[1] + SCROLLER[1])
    dim = abs(CORNER[0] - CURSOR[0]) + 1, abs(CORNER[1] - CURSOR[1]) + 1
    level["platforms"].append(((pos[0]*32, pos[1]*32), dim, color))
    CORNER = None

def draw_platform(pos, dim, color):
    """logical dimensions, re write this later"""
    x, y = pos[0] - SCROLLER[0] * 32, pos[1] - SCROLLER[1] * 32
    w, h = dim
    screen.blit(sprites[color + 'platform00'], (x, y))
    for x_ in range(1, w - 1):
        screen.blit(sprites[color + 'platform01'], (x + x_ * 32, y))
    screen.blit(sprites[color + 'platform02'], (x + (w-1) * 32, y))
    for y_ in range(1, h - 1):
        screen.blit(sprites[color + 'platform10'], (x, y + y_ * 32))
        for x_ in range(1, w - 1):
            screen.blit(sprites[color + 'platform11'], (x + x_ * 32, y + y_ * 32))
        screen.blit(sprites[color + 'platform12'], (x + (w-1) * 32, y + y_ * 32))
    screen.blit(sprites[color + 'platform20'], (x, y + (h-1) * 32))
    for x_ in range(1, w - 1):
        screen.blit(sprites[color + 'platform21'], (x + x_ * 32, y + (h-1) * 32))
    screen.blit(sprites[color + 'platform22'], (x + (w-1) * 32, y + (h-1) * 32))

while True:
    for e in pygame.event.get():
        if e.type == QUIT: quit()
        if e.type == KEYDOWN:
            if pygame.key.get_mods() & KMOD_LSHIFT:
                if e.key == K_LEFT: SCROLLER[0] -= 1
                if e.key == K_RIGHT: SCROLLER[0] += 1
                if e.key == K_UP: SCROLLER[1] -= 1
                if e.key == K_DOWN: SCROLLER[1] += 1
            else:
                if e.key == K_LEFT: CURSOR[0] -= 1
                if e.key == K_RIGHT: CURSOR[0] += 1
                if e.key == K_UP: CURSOR[1] -= 1
                if e.key == K_DOWN: CURSOR[1] += 1
            if not CORNER:
                if e.key in colormap: CORNER = tuple(CURSOR)
            else:
                if e.key in colormap: makeplatform(colormap[e.key])
            if e.key in backgroundmap: level['background'] = backgroundmap[e.key]
            if e.key in actormap: level[actormap[e.key]].append((CURSOR[0] + SCROLLER[0], CURSOR[1] + SCROLLER[1]))
            if e.key == K_d: level['diamond'] = (CURSOR[0] + SCROLLER[0], CURSOR[1] + SCROLLER[1])
            if e.key == K_SPACE: level['spawn'] = (CURSOR[0] + SCROLLER[0], CURSOR[1] + SCROLLER[1])

            if e.key == K_DELETE:
                c = (CURSOR[0] + SCROLLER[0], CURSOR[1] + SCROLLER[1])
                box = pygame.rect.Rect((c[0] * 32, c[1] * 32), (32, 32))
                checklist = [pygame.rect.Rect(pos, (dim[0]*32, dim[1]*32)) for pos, dim, col in level['platforms']]
                i = box.collidelist(checklist)
                if i != -1:
                    level['platforms'].pop(i)
                else:
                    if c in level['spikes']: level['spikes'].remove(c)
                    if c in level['ayys']: level['ayys'].remove(c)
                    if c in level['grapes']: level['grapes'].remove(c)
                    if c in level['barrels']: level['barrels'].remove(c)
            if e.key == K_RETURN:
                if not level['title']:
                    level['title'] = input("Level title: ")
                else:
                    title = input("Level title (blank to not change): ")
                    if title: level['title'] = title
                if filename: 
                    check = input("Save as (blank for " + filename + "): ")
                    if check:
                        filename = check
                else: filename = input("Save as: ")
                with open(filename, "w+") as f:
                    f.write(repr(level))
            if e.key == K_BACKSPACE:
                filename = input("Load file (blank to cancel): ")
                if filename:
                    try:
                        with open(filename, "r") as f:
                            level = eval(f.read())
                        pygame.display.set_caption("Level Editor / "+filename)
                    except IOError: print("failed to load")
    if not level['background']: screen.fill((255, 255, 255))
    else: fill_back()
    for pos, dim, col in level['platforms']:
        draw_platform(pos, dim, col)
    for spike in level['spikes']: screen.blit(sprites['spike'], ((spike[0] - SCROLLER[0]) * 32, (spike[1] - SCROLLER[1]) * 32))
    for grape in level['grapes']: screen.blit(sprites['grape0'], ((grape[0] - SCROLLER[0]) * 32, (grape[1] - SCROLLER[1]) * 32))
    for ayy in level['ayys']: screen.blit(sprites['alien0'], ((ayy[0] - SCROLLER[0]) * 32, (ayy[1] - SCROLLER[1]) * 32))
    for barrel in level['barrels']: screen.blit(sprites['barel0'], ((barrel[0] - SCROLLER[0]) * 32, (barrel[1] - SCROLLER[1]) * 32))
    if level['diamond']: screen.blit(sprites['dimnd'], ((level['diamond'][0] - SCROLLER[0]) * 32, (level['diamond'][1] - SCROLLER[1]) * 32))
    pygame.draw.rect(screen, (0, 255, 0), pygame.rect.Rect(((level['spawn'][0] - SCROLLER[0]) * 32, (level['spawn'][1] - SCROLLER[1]) * 32), (32, 32)))
    pygame.draw.line(screen, (255, 0, 0), (CURSOR[0]*32, CURSOR[1]*32), ((CURSOR[0]+1)*32, (CURSOR[1]+1)*32))
    pygame.display.update()
