#platformer.py
"""
checklist:

Stage 1 :) !!
------------
[x] grapes
[x] ayys
[x] lasers
[x] barrels
[x] ships
[x] backgrounds

Stage 2
--------------
[xxxxxxxxxx] levels
[?] sounds
[?] music
"""
import sys
import pdb
import pygame
from pygame.locals import *
pygame.init()
HEL32 = pygame.font.SysFont("Helvetica", 32)
HEL16 = pygame.font.SysFont("Helvetica", 16)

def init_level(level):
    """returns initialized version of the level"""
    grapes = []
    for grape in level['grapes']:
        grapes.append([grape, -1, 0, 16])
    level['grapes'] = grapes
    ayys = []
    for ayy in level['ayys']:
        ayys.append([ayy, -1, 0, 10])
    level['ayys'] = ayys
    barrels = []
    for barrel in level['barrels']:
        barrels.append([barrel, 1, 0, 0])
    level['barrels'] = barrels
    return level

level = 0
challange = 0
def reset():
    global levels, challange
    levels = []
    with open('levels', 'r') as file:
        lvls = eval(file.read())
    for lvl in lvls: levels.append(init_level(lvl))
    if challange:
        with open('challange', 'r') as file:
            levels.insert(0, init_level(eval(file.read())))
    spawn = levels[level]['spawn']
    return  {
        'x': spawn[0]*32, 'y': spawn[1]*32, 'x_vel': 0, 'y_vel': 0, 'jumps': 0,
        'P': 1, 'scroller': [0,0], 'direction': 1,
        'face': 0, 'body': 0, 'crouch': 0, "count": 0,
    }
g = reset()
# --- sprites ---
def load_spritesheet(filename, data, colorkey=None):
    """data should be dict with key: ((x, y), (w, h)), assumes w, h are 32, 32"""
    surf = pygame.image.load(filename).convert()
    sheet = {}
    for name in data:
        sprite = pygame.Surface(data[name][1])
        x, y = 0 - data[name][0][0], 0 - data[name][0][1]
        sprite.blit(surf, (x, y))
        sprite.set_colorkey(colorkey)
        sheet[name] = sprite
    return sheet

wallpaperdata = {}
for x, pape in enumerate(['blue', 'red', 'white', 'green']):
    wallpaperdata[pape] = ((x * 96, 0), (96, 96))

sheetdata = {
    'face0' : ((12 * 32, 0), (32, 32)),
    'face1' : ((13 * 32, 0), (32, 32)),
    'face2' : ((14 * 32, 0), (32, 32)),
    'body0' : ((12 * 32, 32), (32, 32)),
    'body1' : ((13 * 32, 32), (32, 32)),
    'body2' : ((14 * 32, 32), (32, 32)),
    'crouch': ((15 * 32, 32), (32, 32)),
    'grape0': ((16 * 32, 0), (32, 32)),
    'grape1': ((16 * 32, 32), (32, 32)),
    'grape2': ((15 * 32, 0), (32, 32)),
    'alien0': ((17 * 32, 0), (32, 64)),
    'alien1': ((18 * 32, 0), (32, 64)),
    'alien2': ((19 * 32, 0), (32, 64)), #needs fixiing....
    'ship'  : ((19 * 32, 0), (32, 16)),
    'spike' : ((12 * 32, 64), (32, 32)),
    'laser' : ((13 * 32, 64), (64, 32)),
    'barel0': ((15 * 32, 64), (64, 32)),
    'barel1': ((17 * 32, 64), (64, 32)),
    'dimnd' : ((19 * 32, 64), (32, 32))
}

for y in range(3):
    for x in range(3):
        sheetdata['pinkplatform'+str(y)+str(x)] = ((x * 32, y * 32), (32, 32))
        sheetdata['redplatform'+str(y)+str(x)] = (((x+3) * 32, y * 32), (32, 32))
        sheetdata['whiteplatform'+str(y)+str(x)] = (((x+6) * 32, y * 32), (32, 32))
        sheetdata['brwnplatform'+str(y)+str(x)] = (((x+9) * 32, y * 32), (32, 32))

# --- drawing ---
def fill_back(level):
    if 'background' not in level: screen.fill((255, 255, 255))
    else:
        for y in range(-1, int(screen.get_height() / 96)+1):
            for x in range(-1, int(screen.get_width() / 96)+1):
                screen.blit(wallpaper[level['background']], ((x * 96) + int(g['scroller'][0]/32)%96, (y * 96) + int(g['scroller'][0]/32)%96))

def draw_player():
    x, y = g['x'] + g['scroller'][0], g['y'] + g['scroller'][1]
    if not g['crouch']:
        if g['direction'] == 1:
            screen.blit(sprites['face' + str(g['face'])], (x, y))
            screen.blit(sprites['body' + str(g['body'])], (x, y + 32))
        else:
            screen.blit(pygame.transform.flip(sprites['face' + str(g['face'])], True, False), (x, y))
            screen.blit(pygame.transform.flip(sprites['body' + str(g['body'])], True, False), (x, y + 32))
    else: 
        if g['direction'] == 1: screen.blit(sprites['crouch'], (x, y))
        else: screen.blit(pygame.transform.flip(sprites['crouch'], True, False), (x, y))
    pygame.draw.rect(screen, (255/10 * g['P'], 0, 0), pygame.rect.Rect((x, y - 12), (g['P'] * 3, 10)))


def draw_platform(pos, dim, color):
    x, y = pos[0] + g['scroller'][0], pos[1] + g['scroller'][1]
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

def draw_level(level):
    for pos, dim, col in level['platforms']:
        draw_platform(pos, dim, col)
    for spike in level['spikes']: screen.blit(sprites['spike'], (spike[0] * 32 + g['scroller'][0], spike[1] * 32 + g['scroller'][1]))
    for grape, direct, frame, c in level['grapes']:
        if direct == -1: screen.blit(sprites['grape' + str(frame)], (grape[0] * 32 + g['scroller'][0], grape[1] * 32 + g['scroller'][1]))
        else: screen.blit(pygame.transform.flip(sprites['grape' + str(frame)], True, False), (grape[0] * 32 + g['scroller'][0], grape[1] * 32 + g['scroller'][1]))
    for ayy, direct, frame, c in level['ayys']:
        if direct == -1: screen.blit(sprites['alien' + str(frame)], (ayy[0] * 32 + g['scroller'][0], ayy[1] * 32 + g['scroller'][1]))
        else: screen.blit(pygame.transform.flip(sprites['alien' + str(frame)], True, False), (ayy[0] * 32 + g['scroller'][0], ayy[1] * 32 + g['scroller'][1]))
    for laser, direct in level['lasers']: screen.blit(sprites['laser'], (laser[0] * 32 + g['scroller'][0], laser[1] * 32 + g['scroller'][1]))
    for ship, direct in level['ships']: screen.blit(sprites['ship'], (ship[0] * 32 + g['scroller'][0], ship[1] * 32 + g['scroller'][1] + 8))
    for barrel, direct, frame, state in level['barrels']: screen.blit(sprites['barel' + str(frame)], (barrel[0] * 32 + g['scroller'][0], barrel[1] * 32 + g['scroller'][1]))
    if level['diamond']: screen.blit(sprites['dimnd'], (level['diamond'][0] * 32 + g['scroller'][0], level['diamond'][1] * 32 + g['scroller'][1]))
    draw_player()

def move_player(level):
    """hit detection happens here. Ignores scroller"""
    g['y_vel'] = min(g['y_vel'] + 1, 15)
    if not g['crouch']: hitbox = pygame.rect.Rect((g['x'], g['y']), (32, 64))
    else: hitbox = pygame.rect.Rect((g['x'], g['y']), (32, 32))
    checklist = [pygame.rect.Rect(pos, (dim[0]*32, dim[1]*32)) for pos, dim, col in level['platforms']] 
    checklist += [pygame.rect.Rect((pos[0] * 32, (pos[1] * 32) + 8), (32, 16)) for pos, d in level['ships']]
    if hitbox.collidelist([pygame.rect.Rect((p[0] * 32, p[1] * 32), (32, 32)) for p in level['spikes']]) != -1:
        take_dmg()
    if hitbox.collidelist([pygame.rect.Rect((p[0] * 32, (p[1] * 32) + 13), (64, 8)) for p, d in level['lasers']]) != -1:
        take_dmg()
    if hitbox.colliderect(pygame.rect.Rect((level['diamond'][0] * 32, level['diamond'][1] * 32), (32, 32))):
        win_lvl()
    i = hitbox.collidelist([pygame.rect.Rect((p[0] * 32, p[1] * 32), (32, 32)) for p, d, f, c in level['grapes']])
    if i != -1:
        if g['y_vel'] > 3:
            g['y_vel'] = -10 - int(g['P'])
            level['grapes'][i][2] = 2
        elif level['grapes'][i][2] != 2: take_dmg()
    i = hitbox.collidelist([pygame.rect.Rect((p[0] * 32, p[1] * 32), (32, 64)) for p, d, f, c in level['ayys']])
    if i != -1:
        if g['y_vel'] > 3:
            g['y_vel'] = -10 - int(g['P'])
            if level['ayys'][i][2] == 0: level['ayys'][i][2] = 1
        elif level['ayys'][i][2] == 0: take_dmg()
    i = hitbox.collidelist([pygame.rect.Rect((p[0] * 32, p[1] * 32), (64, 32)) for p, d, f, s in level['barrels']])
    if i != -1:
        if level['barrels'][i][3] == 0:
            if g['y_vel'] > 3:
                level['barrels'][i][3] = 1
                level['barrels'][i][1] = g['direction']
                g['y_vel'] = -10 - int(g['P'])
        else:
            g['y_vel'] = -10 - int(g['P'])
    while hitbox.move(0, g['y_vel']).collidelist(checklist) != -1:
        g['y_vel'] += 1 if g['y_vel'] < 0 else -1
        g['jumps'] = 1
        if abs(g['y_vel']) < 1 and hitbox.collidelist(checklist) != -1: break
    while hitbox.move(g['x_vel'], 0).collidelist(checklist) != -1:
        g['face'] = 1
        g['x_vel'] += 1 if g['x_vel'] < 0 else -1
        g['x_vel'] = int(g['x_vel'])
        g['P'] = 1
        if hitbox.collidelist(checklist) != -1: break
    if hitbox.move(g['x_vel'], g['y_vel']).collidelist(checklist) != -1: g['x_vel'], g['y_vel'] = 0, 0
    if g['y_vel']: g['jumps'] = 0
    g['x'] += g['x_vel']
    g['y'] += g['y_vel']

def evaluate_input(counter):
    """Controlls happen here"""
    g['face'] = 0
    for e in pygame.event.get():
        if e.type == QUIT: quit()
        if e.type == KEYDOWN:
            if e.key == K_ESCAPE: quit()
            if e.key == K_SPACE and g['jumps']:
                g['y_vel'] = -10 - int(g["P"])
                g['jumps'] -= 1
            if e.key == K_q: take_dmg()

            if e.key == K_n and '-d' in sys.argv: win_lvl()
            if e.key == K_d and '-d' in sys.argv: pdb.set_trace()

    keys = pygame.key.get_pressed()
    if not keys[K_SPACE] and -10 < g['y_vel'] < 0:
        g['y_vel'] += 2
    if keys[K_LEFT] and not keys[K_RIGHT] and not g['crouch']:
        if g['direction'] != -1:
            g['direction'] = -1
            g['P'] = g['P'] / 2
        if counter % 20:
            g['P'] = min(g['P'] + .4, 10)
            g['body'] = (g['body'] + 1) % 2
        g['x_vel'] = 0 - int(g['P'])
    elif keys[K_RIGHT] and not keys[K_LEFT] and not g['crouch']:
        if g['direction'] != 1:
            g['direction'] = 1
            g['P'] = g['P'] / 2
        if counter % 20:
            g['P'] = min(g['P'] + .4, 10)
            g['body'] = (g['body'] + 1) % 2
        g['x_vel'] = int(g['P'])
    elif g['jumps']:
        g['P'] = 1
        g['x_vel'] += 0 - g['x_vel'] / 5
    if keys[K_DOWN]:
        if not g['crouch']: 
            g['y'] += 32
        g['crouch'] = 1
    elif g['crouch']:
        hitbox = pygame.rect.Rect((g['x'], g['y'] - 32), (32, 64))
        checklist = [pygame.rect.Rect(pos, (dim[0]*32, dim[1]*32)) for pos, dim, col in levels[level]['platforms']] 
        checklist += [pygame.rect.Rect((pos[0] * 32, (pos[1] * 32) + 8), (32, 16)) for pos, d in levels[level]['ships']]
        if hitbox.collidelist(checklist) == -1:
            g['crouch'] = 0
            g['y'] -= 32

def adjust_scroll():
    g['scroller'][0] = 0 - g['x'] + (screen.get_width() /2) - 16
    g['scroller'][1] = 0 - g['y'] + (screen.get_height() /2) - 32
    if g['crouch']: g['scroller'][1] += 32

def take_dmg():
    global g
    g['face'], g['body'] = 2, 2
    t = 0
    while t < 30:
        t += 1
        clock.tick(30)
        fill_back(levels[level])
        draw_level(levels[level])
        pygame.display.update()
        for e in pygame.event.get():
            if e.type == QUIT or e.type == KEYDOWN and e.key == K_ESCAPE: quit()
    g = reset()

def win_lvl():
    global g, level, flag
    t = 0
    while t < 30:
        t += 1
        clock.tick(30)
        fill_back(levels[level])
        draw_level(levels[level])
        pygame.display.update()
        for e in pygame.event.get():
            if e.type == QUIT or e.type == KEYDOWN and e.key == K_ESCAPE: quit()
    level += 1
    if level == len(levels):
        level -= 1
        flag = False
    else:
        level_title(levels[level])
    g = reset()

def level_title(level):
    global g
    g = reset()
    c = 0
    while c < 60:
        c += 1
        screen.fill((0, 0, 0))
        screen.blit(HEL32.render(level['title'], 0, (255, 255, 255)), (64, 64))
        g['x'] = c * int(screen.get_width()  / 60)
        g['y'] = int(screen.get_height() / 2)
        g['body'] = c % 2
        draw_player()
        pygame.display.update()
        for e in pygame.event.get():
            if e.type == QUIT or e.type == KEYDOWN and e.key == K_ESCAPE: quit()
        clock.tick(30)


def move_actors(level, c):
    """all enemy code goes here"""
    checklist = [pygame.rect.Rect(pos, (dim[0]*32, dim[1]*32)) for pos, dim, col in level['platforms']]
    checklist += [pygame.rect.Rect((pos[0] * 32, pos[1] * 32), (32, 32)) for pos in level['spikes']]
    for i, data in enumerate(level['grapes']):
        grape, direction, frame, count = data
        if frame != 2:
            level['grapes'][i][2] = (frame + 1) % 2
            hitbox = pygame.rect.Rect((grape[0] * 32, grape[1] * 32), (32, 32))
            if hitbox.move(16 * direction, 1).collidelist(checklist) == -1 or hitbox.move(2 * direction, -1).collidelist(checklist) != -1:
                level['grapes'][i][1] *= -1
            level['grapes'][i][0] = level['grapes'][i][0][0] + (2 * (1/32)) * direction, level['grapes'][i][0][1]
        else:
            if count:
                level['grapes'][i][3] -= 1
            else:
                level['grapes'].pop(i)
    for i, data in enumerate(level['ayys']):
        ayy, direction, frame, count = data
        hitbox = pygame.rect.Rect((ayy[0] * 32, ayy[1] * 32), (32, 64))
        if hitbox.move(2 * direction, 0).collidelist(checklist) != -1:
            level['ayys'][i][1] *= -1
        if c % 60 == 0 and frame == 0:
            laser = [(ayy[0] - 1 , ayy[1]), direction] if direction == -1 else [(ayy[0], ayy[1]), direction]
            level['lasers'].append(laser)
        level['ayys'][i][0] = level['ayys'][i][0][0] + (2 * (1/32)) * level['ayys'][i][1], level['ayys'][i][0][1]
        if frame != 0:
            if count:
                level['ayys'][i][3] -= 1
            else:
                level['ayys'][i][2] += 1
                level['ayys'][i][3] = 10
                if level['ayys'][i][2] > 2:
                    level['ayys'].pop(i)
                    level['ships'].append([(ayy[0], ayy[1]+1), direction]) 
    for i, data in enumerate(level['lasers']):
        laser, direction = data     
        hitbox = pygame.rect.Rect((laser[0] * 32, (laser[1] * 32) + 13), (64, 8))
        if hitbox.move(10 * direction, 0).collidelist(checklist) != -1:
            level['lasers'].pop(i)
        else:
            level['lasers'][i][0] = level['lasers'][i][0][0] + (10 * (1/32)) * direction, level['lasers'][i][0][1]
    for i, data in enumerate(level['ships']):
        ship, direction = data
        hitbox = pygame.rect.Rect((ship[0] * 32, (ship[1] * 32) + 8), (32, 16))
        if hitbox.move(2 * direction, 0).collidelist(checklist) != -1:
            level['ships'][i][1] *= -1
        if hitbox.move(0, -1).colliderect(pygame.rect.Rect((g['x'], g['y']), (32, 64))):
            g['x_vel'] = 2 * direction if abs(g['x_vel']) < 2 else g['x_vel']
        level['ships'][i][0] = (level['ships'][i][0][0] + (2 * 1/32) * level['ships'][i][1], level['ships'][i][0][1])
    for i, data in enumerate(level['barrels']):
        barrel, direction, frame, state = data
        if state != 0:
            checklist = [pygame.rect.Rect(pos, (dim[0]*32, dim[1]*32)) for pos, dim, col in level['platforms']]
            checklist += [pygame.rect.Rect((pos[0] * 32, pos[1] * 32), (32, 32)) for pos in level['spikes']]
            checklist += [pygame.rect.Rect((p[0] * 32, p[1] * 32), (63, 32)) for p, d, f, s in filter(lambda b: b[0] != barrel, level['barrels'])]
            hitbox = pygame.rect.Rect((barrel[0] * 32, barrel[1] * 32), (64, 32))
            level['barrels'][i][2] = (frame + 1) % 2
            if hitbox.move(4 * direction, 0).collidelist(checklist) != -1:
                level['barrels'][i][1] *= -1
            if hitbox.move(0, 4).collidelist(checklist) == -1:
                level['barrels'][i][0] = (level['barrels'][i][0][0], level['barrels'][i][0][1] + (4 * (1/32)))
            grapeboxes = [pygame.rect.Rect((p[0] * 32, p[1] * 32), (32, 32)) for p, d, f, c in level['grapes']]
            ayyboxes = [pygame.rect.Rect((p[0] * 32, p[1] * 32), (32, 64)) for p, d, f, c in level['ayys']]
            i_ = hitbox.collidelist(grapeboxes)
            if i_ != -1: level['grapes'][i_][2] = 2
            i_ = hitbox.collidelist(ayyboxes)
            if i_ != -1: level['ayys'][i_][2] = 1
            level['barrels'][i][0] = (level['barrels'][i][0][0] + (4 * (1/32)) * direction, level['barrels'][i][0][1])

if __name__ == """__main__""":
    clock = pygame.time.Clock()
    if '-f' in sys.argv: screen = pygame.display.set_mode((640, 480), FULLSCREEN)
    else: screen = pygame.display.set_mode((640, 480))
    pygame.display.set_caption("Super Red Pants Turbo")
    sprites = load_spritesheet("platformertileset.png", sheetdata, colorkey=(1, 255, 1))
    pygame.draw.rect(sprites['alien2'], (1, 255, 1), pygame.rect.Rect((0, 0), (32, 16)))
    wallpaper = load_spritesheet("backgrounds.png", wallpaperdata)
    titlecard = pygame.image.load('titlecard.png').convert()
    endframe = pygame.image.load('endframe.png').convert()
    titlecard.set_colorkey((1, 255, 1))
    endframe.set_colorkey((1, 255, 1))
    flag = True
    screen.fill((0, 0, 0))
    screen.blit(HEL32.render("The philosophy of Red Pants", 0, (255, 255, 255)), (64, 64))
    screen.blit(HEL32.render(""" "Don't worry about it" """, 0, (255, 255, 255)), (128, 130))
    screen.blit(HEL16.render("Space         Jump", 0, (255, 255, 255)), (300, 200))
    screen.blit(HEL16.render("Left/Right    Run", 0, (255, 255, 255)), (300, 232))
    screen.blit(HEL16.render("Down          Crouch", 0, (255, 255, 255)), (300, 264))
    screen.blit(HEL16.render("Q                 Restart Level", 0, (255, 255, 255)), (300, 298))
    screen.blit(HEL16.render("Escape       Quit", 0, (255, 255, 255)), (300, 330))
    
    def miltotime(mil):
        mins = str(mil // 60000)
        secs = "0" + str(mil // 1000 % 60)[-2:]


    while flag:
        pygame.display.update()
        for e in pygame.event.get():
            if e.type == QUIT or e.type == KEYDOWN and e.key == K_ESCAPE: quit()
            if e.type == KEYUP: flag = False
    while True:
        flag = True
        g['y'] = -64
        level = 0
        check = []
        while flag:
            g['scroller'][0] -= 1
            clock.tick(30)
            fill_back(levels[level])
            draw_level(levels[level])
            move_actors(levels[level], 1)
            screen.blit(titlecard, ((screen.get_width()/2) - (titlecard.get_width()/2), 16))
            pygame.display.update()
            for e in pygame.event.get():
                if e.type == QUIT or e.type == KEYDOWN and e.key == K_ESCAPE: quit()
                elif e.type == KEYDOWN:
                    if e.key == K_SPACE:
                        flag = False
                        if check[-8:] == [K_UP, K_UP, K_DOWN, K_DOWN, K_LEFT, K_RIGHT, K_LEFT, K_RIGHT]:
                            challange = 1
                            g = reset()
                    else: check.append(e.key)
        level_title(levels[level])
        g = reset()
        flag = True
        IGT = 0
        clock.tick()
        while flag:
            g['count'] += 1
            IGT += clock.tick(30)
            evaluate_input(g['count'])
            adjust_scroll()
            move_actors(levels[level], g['count'])
            move_player(levels[level])
            fill_back(levels[level])
            draw_level(levels[level])
            pygame.display.update()
        flag = True
        count = 0
        while flag:
            count += 1
            clock.tick(30)
            fill_back(levels[level])
            screen.blit(endframe, (0, 0))
            screen.blit(HEL32.render(str(IGT // 60000) +":"+ ("0" + str(IGT // 1000 % 60))[-2:], 0, (0, 0, 0)),(180, 160))
            pygame.display.update()
            for e in pygame.event.get():
                if e.type == QUIT or e.type == KEYDOWN and e.key == K_ESCAPE: quit()
                elif e.type == KEYDOWN and e.key == K_SPACE and count >= 30: flag = False
        g = reset()
