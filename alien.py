#!/usr/bin/python

import os, random
import pygame
from pygame.locals import *

SCREENWIDTH    = 680
SCREENHEIGHT   = 480
ALIEN_RELOAD   = 12     #frames between new aliens
ALIEN_ODDS     = 20     #chances a new alien appears
SCREENRECT     = Rect(0, 0, SCREENWIDTH, SCREENHEIGHT)
SCORE          = 0
DEADALIENS     = 0

#our directory 
main_dir = os.path.split(os.path.abspath(__file__))[0]

FPS = 40
fpsClock = pygame.time.Clock()

def load_image(file, colorkey = None):
    "loads an image"
    file = os.path.join(main_dir, 'data', file)
    try:
        surface = pygame.image.load(file)
    except pygame.error:
        raise SystemExit('can`t load image "%s" %s' %(file, pygame.get_error()))
    image = surface.convert()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0,0))
        image.set_colorkey(colorkey, RLEACCEL)
    return image


def load_images(*files):
    imgs = []
    for file in files:
      imgs.append(load_image(file))
    return imgs


class dummysound:
    def play(self): pass


def load_sound(file):
    if not pygame.mixer: return dummysound()
    file = os.path.join(main_dir, 'data', file)
    try:
        sound = pygame.mixer.Sound(file)
        return sound
    except pygame.error:
        print ('Warning, unable to load, %s' % file)
    return dummysound()


class Fist(pygame.sprite.Sprite):
    """moves a fist on the screen, following the mouse"""
    def __init__(self):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = load_image('fist.bmp', -1)
        self.rect = self.image.get_rect()

    def update(self):
        "update the fist with the postion of the mouse"
        pos = pygame.mouse.get_pos()
        self.rect.midtop = pos


class Alien(pygame.sprite.Sprite):
    speed = 13                  #speed of the aline
    images = []                 #aline images
    def __init__(self):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[random.choice((0, 1, 2))]
        self.rect = self.image.get_rect()
        self.facing = random.choice((-1,1)) * Alien.speed
        if self.facing < 0:
            self.rect.right = SCREENRECT.right


    def update(self):
        global DEADALIENS
        self.rect.move_ip(self.facing, 0)
        # wether the alien is in the screen
        if not SCREENRECT.contains(self.rect):
            self.facing = -self.facing; #go the opposite way
            self.rect.top = self.rect.bottom + 1 #move it to the next level
        #here, we should kill the alien
        if self.rect.top > SCREENHEIGHT:
            print (self.rect.top)
            self.kill()
            DEADALIENS = DEADALIENS + 1
        if DEADALIENS > 20:
            Text('red', 'You Lose', 300, 200)            


class Explosion(pygame.sprite.Sprite):
    defaultlife = 12 # boom effect
    images = []
    def __init__(self, actor):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect(center=actor.rect.center)
        self.life = self.defaultlife


    def update(self):
        self.life = self.life - 1
        self.image = self.images[self.life%2]
        if self.life <= 0: self.kill()

class Score(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.font = pygame.font.Font(None, 20)
        self.font.set_italic(1)
        self.color = Color('red')
        self.lastscore = -1
        self.update()
        self.rect = self.image.get_rect().move(10, 450)


    def update(self):
        if SCORE != self.lastscore:
            self.lastscore = SCORE
            msg = "Score: %d" % SCORE
            self.image = self.font.render(msg, 0, self.color)

class Text(pygame.sprite.Sprite):
    def __init__(self, color, string, x, y):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.font = pygame.font.Font(None, 40)
        self.string = string
        self.color = Color(color)
        self.update()
        self.rect = self.image.get_rect().move(x, y)

    def update(self):
        self.image = self.font.render(self.string, 0, self.color)

def main():
    # Initialize
    pygame.init()

    # check out wether the sound module is initialized
    if pygame.mixer and not pygame.mixer.get_init():
        print ('Waring: no sound')
        pygame.mixer = None

    # setup the background and screen
    screen = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
    background = load_image('background.gif')
    background = pygame.transform.scale2x(background)
    background = pygame.transform.scale2x(background)
    background = pygame.transform.scale2x(background)
    background = pygame.transform.scale2x(background)
    
    # put background on the screen
    screen.blit(background, (0, 0)) 
    pygame.display.update()

    # Initialize 
    img = load_image('explosion1.gif')
    Explosion.images = [img, pygame.transform.flip(img, 1, 1)]
    Alien.images = load_images('alien1.gif', 'alien2.gif', 'alien3.gif')

    # setup window
    pygame.display.set_caption('Aliens')
    pygame.mouse.set_visible(0)

    # Initialize sound 
    boom_sound = load_sound('boom.wav')
    fist_sound = load_sound('car_door.wav')
    # background sound
    if pygame.mixer:
        music = os.path.join(main_dir, 'data', 'house_lo.wav')
        pygame.mixer.music.load(music)
        pygame.mixer.music.play(-1) #loop indefinitely


    #Game group for objects
    aliens = pygame.sprite.Group()
    all = pygame.sprite.RenderUpdates()
  
    Alien.containers = aliens, all
    Explosion.containers = all
    #Score.containers = all
    Fist.containers = all
    Text.containers = all

    # Initialize
    alienreload = ALIEN_RELOAD
    clock = pygame.time.Clock()

    global SCORE
    global DEADALIENS
    fist = Fist()
    if pygame.font:
        all.add(Score())

    while True:
        all.clear(screen, background)

        if DEADALIENS > 20:
            return
        # handle input 
        for event in pygame.event.get():
            if event.type == QUIT:
                return
            elif event.type == MOUSEBUTTONDOWN:
                for alien in pygame.sprite.spritecollide(fist, aliens, 1):
                    boom_sound.play()
                    Explosion(alien)
                    SCORE = SCORE + 1

        # update the sprite in "all" group
        all.update()

        # here we create a new alien
        if alienreload:
            alienreload = alienreload - 1
        elif not int(random.random() * ALIEN_ODDS):
            Alien()
            alienreload = ALIEN_RELOAD

        # draw the update
        dirty = all.draw(screen)
        pygame.display.update(dirty)
        clock.tick(FPS)

    # game over
    pygame.quit()

if __name__ == '__main__': main()
