# https://github.com/russs123/Battle

import pygame, random, math
from pygame.locals import *

pygame.init()

# declaring constants
bottom_painel = 150
width = 800
height = 400 + bottom_painel
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Battle")
clock = pygame.time.Clock()
green = (0,255,0)
red = (255,0,0)

# load images
back_img = pygame.image.load("./img/Background/harry potter background.jpg").convert_alpha()
painel_img = pygame.image.load("img/Icons/panel.png").convert_alpha()
sword_img = pygame.image.load("img/Icons/sword.png").convert_alpha()
potion_img = pygame.image.load("img/Icons/potion.png").convert_alpha()
victory_img = pygame.image.load("img/Icons/victory.png").convert_alpha()
defeat_img = pygame.image.load("img/Icons/defeat.png").convert_alpha()
restart_img = pygame.image.load("img/Icons/restart.png").convert_alpha()
back_img = pygame.transform.scale(back_img, (back_img.get_width() // 2, back_img.get_height() //2  - 50))
trilha = pygame.mixer.Sound("hp_music.mp3")

def drawText(texto, color, x, y, s, center=True):

    screen_text = pygame.font.SysFont('Arial', s).render(texto, True, color)

    if center:
        rect = screen_text.get_rect()
        rect.center = (x, y)
    else:
        rect = (x, y)
    screen.blit(screen_text, rect)

def drawBackground(back_img):
    screen.blit(back_img, (0,0))

def drawVictory(victory_img):
    screen.blit(victory_img, (width/2 - victory_img.get_width()/2,height/2 - victory_img.get_height()))

def drawDefeat(defeat_img):
    screen.blit(defeat_img, (width/2 - defeat_img.get_width()/2,height/2 - defeat_img.get_height()))

def drawPainel(painel_img, restart_img, knight, bandits, knight_health_bar, bandits_health_bar):
    if knight.alive and (bandits[0].alive or bandits[1].alive):
        screen.blit(painel_img, (0,400))
        screen.blit(potion_img, (10,450))

        drawText(f"{knight.name} - {knight.hp} hp", red, 150, 430, 16)
        knight_health_bar.draw(knight.hp)

        for i,bandit in enumerate(bandits):
            drawText(f"{bandit.name} - {bandit.hp} hp", red, 550, bandit.y + 160+(i*55), 16)
            bandits_health_bar[i].draw(bandit.hp)
    else:
        screen.blit(painel_img, (0,400))
        screen.blit(restart_img, (width/2 - restart_img.get_width()/2, height - bottom_painel + restart_img.get_height()/2))

def restart(knight, bandits):
    knight.hp = knight.max_hp
    knight.potions = 3
    knight.alive = True
    for bandit in bandits:
        bandit.hp = bandit.max_hp
        bandit.potions = 2
        bandit.alive = True

class Fighter:
    def __init__(self, x, y, name, max_hp = 30, strength = 10, potions = 2):
        self.x = x
        self.y = y
        self.name = name
        self.max_hp = max_hp
        self.hp = max_hp
        self.strength = strength
        self.potions = potions
        self.alive = True
        self.animation_list = []
        self.frame_index = 0
        self.action = 0#0:idle, 1:attack, 2:hurt, 3:dead
        self.update_time = pygame.time.get_ticks()
        # load idle imgs
        temp_list = []
        for i in range(8):
            img = pygame.image.load(f"img/{self.name}/Idle/{i}.png").convert_alpha()
            img = pygame.transform.scale(img, (img.get_width() * 3, img.get_height() * 3))
            temp_list.append(img)
        self.animation_list.append(temp_list)
        # load attack images
        temp_list = []
        for i in range(8):
            img = pygame.image.load(f"img/{self.name}/Attack/{i}.png").convert_alpha()
            img = pygame.transform.scale(img, (img.get_width() * 3, img.get_height() * 3))
            temp_list.append(img)
        self.animation_list.append(temp_list)
        # load hurt images
        temp_list = []
        for i in range(3):
            img = pygame.image.load(f"img/{self.name}/Hurt/{i}.png").convert_alpha()
            img = pygame.transform.scale(img, (img.get_width() * 3, img.get_height() * 3))
            temp_list.append(img)
        self.animation_list.append(temp_list)
        # load death images
        temp_list = []
        for i in range(10):
            img = pygame.image.load(f"img/{self.name}/Death/{i}.png").convert_alpha()
            img = pygame.transform.scale(img, (img.get_width() * 3, img.get_height() * 3))
            temp_list.append(img)
        self.animation_list.append(temp_list)
        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def draw(self):
        screen.blit(self.image, self.rect)

    def update(self):
        if self.alive or self.frame_index < 9:
            animation_cooldown = 100

            self.image = self.animation_list[self.action][self.frame_index]
            if pygame.time.get_ticks() - self.update_time > animation_cooldown:
                self.update_time = pygame.time.get_ticks()
                self.frame_index = self.frame_index + 1

            if self.frame_index >= len(self.animation_list[self.action]):
                if self.hp > 0:
                    self.idle()
                elif self.hp <= 0:
                    self.death()
        else:
            self.image = self.animation_list[3][9]

    def idle(self):
        self.action = 0
        self.frame_index = 0

    def attack(self, target):
        self.action = 1
        self.frame_index = 0

        damage = self.strength + random.randint(-5, 5)
        target.hp = target.hp - damage
        if target.hp <= 0:
            target.hp = 0
            target.alive = False
        return damage

    def hurt(self):
        self.action = 2
        self.frame_index = 0

    def death(self):
        self.action = 3
        self.frame_index = 0

class HealthBar:

    def __init__(self, x, y, hp, max_hp):
        self.x = x
        self.y = y
        self.hp = hp
        self.max_hp = max_hp

    def draw(self, hp):

        self.hp = hp
        var = (self.hp * 250)/self.max_hp
        pygame.draw.rect(screen, red, (self.x, self.y, 250, 20))
        pygame.draw.rect(screen, green, (self.x, self.y, var, 20))

# initializing knight
knight = Fighter(200,260,"Knight", 30, 10, 3)
knight_health_bar = HealthBar(100, 450, knight.hp, knight.max_hp)

# initializing bandits
bandits = []
bandits_health_bar = []
bandits.append(Fighter(550,270,"Bandit", 20, 6, 1))
bandits_health_bar.append(HealthBar(500, 445, bandits[0].hp, bandits[0].max_hp))
bandits.append(Fighter(650,270,"Bandit", 20, 6, 1))
bandits_health_bar.append(HealthBar(500, 500, bandits[1].hp, bandits[1].max_hp))

# declaring variables
click = False
attacking = False
healing = False
action_time = 0
target = None
turno = 0
bandit_action = 0
potion_rect = potion_img.get_rect(topleft=(10,450))
restart_rect = restart_img.get_rect(topleft=(width/2 - restart_img.get_width()/2, height - bottom_painel + restart_img.get_height()/2))
damage = 0
hurt = False
hurt_x = 0
hurt_y = 0
heal_number = 0
heal = False
heal_x = 0
heal_y = 0
pygame.mixer.Sound.play(trilha)

run = True
while run:

    clock.tick(60)

    if pygame.mixer.get_busy() == 0:
        pygame.mixer.Sound.play(trilha)

    drawBackground(back_img)
    drawPainel(painel_img, restart_img, knight, bandits, knight_health_bar, bandits_health_bar)

    # knight actions
    if target == knight and pygame.time.get_ticks() - action_time > 400:
        target.hurt()
        hurt = True
        hurt_x = target.x
        hurt_y = target.y - 50
        target = None
    knight.update()
    knight.draw()

    # bandit actions
    for i,bandit in enumerate(bandits):
        if target == bandit and pygame.time.get_ticks() - action_time > 400:
            target.hurt()
            hurt = True
            hurt_x = target.x
            hurt_y = target.y - 50
            target = None
        bandit.update()
        bandit.draw()

    # make sure mouse is visible
    pygame.mouse.set_visible(True)
    mouse = pygame.mouse.get_pos()

    # getting knight actions
    for bandit in bandits:
        if bandit.rect.collidepoint(mouse) and bandit.alive:
            pygame.mouse.set_visible(False)
            screen.blit(sword_img, mouse)
            if click == True and turno == 0 and  pygame.time.get_ticks() - action_time > 1000:
                attacking = True
                target = bandit

    if potion_rect.collidepoint(mouse) and click == True and turno == 0 and  pygame.time.get_ticks() - action_time > 1000:
        healing = True

    # making damage text or healing text
    if hurt:
        hurt_y = hurt_y - 1
        drawText(f"- {damage}", red, hurt_x, hurt_y, 22, center=True)
        if hurt_y <= 190:
            hurt = False
    elif heal:
        heal_y = heal_y - 1
        drawText(f"+ {heal_number}", green, heal_x, heal_y, 22, center=True)
        if heal_y <= 190:
            heal = False

    # knight's shift
    if turno == 0:
        if attacking:
            damage = knight.attack(target)
            action_time = pygame.time.get_ticks()
            attacking = False
            turno = 1
        elif healing:
            if knight.potions:
                knight.hp = knight.hp + 12
                heal_number = 12
                heal = True
                heal_x = knight.x
                heal_y = knight.y - 50
                if knight.hp > knight.max_hp:
                    knight.hp = knight.max_hp
                action_time = pygame.time.get_ticks()
                knight.potions = knight.potions - 1
                healing = False
                turno = 1
            else:
                healing = False
    # bandit nº1's shift
    elif turno == 1:
        if pygame.time.get_ticks() - action_time > 1000:
            bandit_action = random.randint(0,1)
            if bandits[0].alive and knight.alive and bandit_action == 0:
                    target = knight
                    damage = bandits[0].attack(target)
                    action_time = pygame.time.get_ticks()
                    turno = 2
            elif bandits[0].alive and knight.alive and bandit_action == 1 and bandits[0].hp < bandits[0].max_hp:
                if bandits[0].potions:
                    bandits[0].hp = bandits[0].hp + 6
                    heal_number = 6
                    heal = True
                    heal_x = bandits[0].x
                    heal_y = bandits[0].y - 50
                    if bandits[0].hp > bandits[0].max_hp:
                        bandits[0].hp = bandits[0].max_hp
                    action_time = pygame.time.get_ticks()
                    bandits[0].potions = bandits[0].potions - 1
                    turno = 2
            elif bandits[0].alive == False or knight.alive == False:
                turno = 2
    # bandit nº2's shift
    elif turno == 2:
        if pygame.time.get_ticks() - action_time > 1000:
            bandit_action = random.randint(0,1)
            if bandits[1].alive and knight.alive and bandit_action == 0:
                    target = knight
                    damage = bandits[1].attack(target)
                    action_time = pygame.time.get_ticks()
                    turno = 0
            elif bandits[1].alive and knight.alive and bandit_action == 1 and bandits[1].hp < bandits[1].max_hp:
                if bandits[1].potions:
                    bandits[1].hp = bandits[1].hp + 6
                    heal_number = 6
                    heal = True
                    heal_x = bandits[1].x
                    heal_y = bandits[1].y - 50
                    if bandits[1].hp > bandits[1].max_hp:
                        bandits[1].hp = bandits[1].max_hp
                    action_time = pygame.time.get_ticks()
                    bandits[1].potions = bandits[1].potions - 1
                    turno = 0
            elif bandits[1].alive == False or knight.alive == False:
                turno = 0

    # getting mouse events
    if knight.alive and (bandits[0].alive or bandits[1].alive):
        for event in pygame.event.get():
            if event.type == QUIT:
                run = False
            if knight.alive:
                if event.type == MOUSEBUTTONDOWN:
                    click = True
                elif event.type == MOUSEBUTTONUP:
                    click = False
    elif knight.alive == False:
        drawDefeat(defeat_img)
        for event in pygame.event.get():
            if event.type == QUIT:
                run = False
    elif knight.alive and not bandits[0].alive and not bandits[1].alive:
        drawVictory(victory_img)
        for event in pygame.event.get():
            if event.type == QUIT:
                run = False

    if restart_rect.collidepoint(mouse) and pygame.mouse.get_pressed() == (1, 0, 0):
        restart(knight, bandits)

    pygame.display.update()

pygame.quit()
