import pygame
import sys
import os
import time
import pygame.freetype
import random
import pygame_menu

'''
Kilder brukt i dette prosjektet:

https://opensource.com/article/18/7/put-platforms-python-game
https://opensource.com/article/17/12/game-framework-python
https://www.tutorialspoint.com/What-is-difference-between-self-and-init-methods-in-python-Class
https://pygame-menu.readthedocs.io/en/latest/

'''

lvl = 1 #hvilken level spilleren er på
is_nextlevel_enabled = False
nextlevel = False
gameover = False

while True:

    # Variabler:
    main = True # dette betyr at spillet kjører (motoren skrus på)
    map_x=1800
    map_y=900
    fps=30 
    ani=4 # animasjons-sykluser
    world=pygame.display.set_mode([map_x,map_y])
    pygame.init()
    blue  = (25, 25, 200)
    black = (23, 23, 23)
    white = (254, 254, 254)
    ALPHA = (0, 255, 0)
    snowFall = []
    tx   = 128 #tykkelsen av 'ground'
    ty   = 128 #høyden av 'ground'
    fremx = 700 #hvor den begynner å scrolle når du går frem
    bakx = 400 #hvor den begynner å scrolle når du går bak

    font_path = "C:/Users/Eirik Brun-Lunde/Desktop/rescuesanta-main/fonts/slkscr.ttf" #den fonten vi bruker til stats
    font_size = 64 
    pygame.freetype.init() 
    guifont = pygame.freetype.Font(font_path, font_size)

    wantedvolume = 0.05

    
    Selected = False 

    # Start Menu
    
    def set_volume(value, thing):  #denne funsjonen gjør at spilleren kan velge volum
        if value[1] == 0:
            pygame.mixer.music.set_volume(0)
        elif value[1] == 1:
            pygame.mixer.music.set_volume(0.05)
        elif value[1] == 2:
            pygame.mixer.music.set_volume(0.25)
        elif value[1] == 3:
            pygame.mixer.music.set_volume(0.5)
        else:
            pass

    #def start_game():
    #    Selected = True
    #    
    #

    is_gameover_enabled = True
    is_menu_disabled = False

    def restartgame():
        global is_gameover_enabled
        is_gameover_enabled = False
        main = True
    def closemenu():
        global is_menu_disabled
        is_menu_disabled = True

    def stopnextlevel():
        global is_nextlevel_enabled
        is_nextlevel_enabled = False
        print(is_nextlevel_enabled)
        main = True

    startmenu_theme = pygame_menu.themes.THEME_BLUE.copy()
    startmenu_theme.set_background_color_opacity(0.9)
    startmenu = pygame_menu.Menu(map_y, map_x, "Rescue Santa", theme=startmenu_theme)
    startmenu.add_selector("Sound Volume:", [("High", 3),("Medium", 2),("Low", 1), ("Off", 0)], onchange=set_volume)
    startmenu.add_button("Start Game", closemenu)
    startmenu.add_button("Quit", pygame_menu.events.EXIT)

    gameovermenu_theme = pygame_menu.themes.THEME_ORANGE.copy()
    gameovermenu_theme.set_background_color_opacity(0.9)
    gameovermenu = pygame_menu.Menu(map_y, map_x, "Level finished / Game Over", theme=gameovermenu_theme)
    gameovermenu.add_button("Reload Game", restartgame)
    gameovermenu.add_button("Quit", pygame_menu.events.EXIT)

    nextlevelmenu_theme = pygame_menu.themes.THEME_SOLARIZED.copy()
    nextlevelmenu_theme.set_background_color_opacity(0.9)
    nextlevelmenu = pygame_menu.Menu(map_y, map_x, "Next Level!", theme=nextlevelmenu_theme)
    nextlevelmenu.add_button("Next Level", stopnextlevel)
    nextlevelmenu.add_button("Quit", pygame_menu.events.EXIT)
    
    #while not Selected:
    #    events = pygame.event.get()
    #    for event in events:
    #        if event.type == pygame.QUIT:
    #            exit()
    #    if startmenu.is_enabled():
    #        startmenu.update(events)
    #        startmenu.draw(world)
    #    pygame.display.flip()




    


    # Objekter:

    def stats(score,health): #dennefunsjonen displayer stats på sjermen
        guifont.render_to(world, (4, 860), "Score: " + str(score), black, None, size=font_size)
        guifont.render_to(world, (4, 820), "HP: " + str(health), black, None, size=font_size)
        guifont.render_to(world, (4, 780), "Level: " + str(lvl), black, None, size=font_size)

    class Platform(pygame.sprite.Sprite): #denne klassen gir platformene en sprite og størrelse
        def __init__(self, xpl, ypl, bldb, bldh, bld): # xpl = x-plassering, ypl = y-plassering, bldb = bilde-bredde, bldh = bilde-høyde, bld = bilde // __init__ er en metode som brukes i python klasser. Det kalles ofte for en "constructor". Grunnen til dette er siden den lar klassen bruke attributesene sine. (Kilde: https://www.tutorialspoint.com/What-is-difference-between-self-and-init-methods-in-python-Class)
            pygame.sprite.Sprite.__init__(self)
            self.image = pygame.image.load(bld).convert()
            if bld == "loot.png":
                self.image = pygame.transform.scale(self.image, (125,150))
            self.image.convert_alpha()
            self.image.set_colorkey(ALPHA)
            self.rect = self.image.get_rect()
            self.rect.y = ypl # setter y plasseringen til plattformen til variabelen ypl
            self.rect.x = xpl # --||-- x  --||--                                     xpl
    
    class Player(pygame.sprite.Sprite): #denne funsjonen gir spilleren sprite og mange andre egenskaper
        def __init__(self):
            pygame.sprite.Sprite.__init__(self)
            self.movex = 0 # her flyttes player på x aksen
            self.movey = 0 # her flyttes player på y aksen
            self.frame = 0 # her tracker vi hvilken frame vi er på
            self.health = 3 # hp
            self.score = 0 #antall presanger
            self.damage = 0 #hvor mye skade den skat ta
            self.lvlup = 0 #hvor mange levler spilleren skal levle opp
            self.høyre = True #ser om spilleren set til høyre eller ikke
            self.is_jumping = True #ser om spilleren hopper eller ikke
            self.is_falling = True #ser om spilleren faller eller ikke
            self.images = [] #en liste som inneholder bilder som blir bruk i klassen
            for i in range(1, 10): #en for loop som sykler på walking animasonen til spilleren når han går
                    img = pygame.image.load("tile" + str(i) + '.png').convert()
                    img.convert_alpha()
                    img.set_colorkey(ALPHA)
                    self.images.append(img)
                    self.image = self.images[0]
                    self.rect = self.image.get_rect()

        def control(self, x, y): #en funsjon som setter variabelen for at spilleren skal flytte seg
            self.movex += x
            self.movey += y

        def gravity(self):# en funsjon som gjør at spilleren faller når det ikke er bakke under dem
            if self.is_jumping:
                self.movey += 3.2 # hvor sterk gravitasjonen er
            
            if self.rect.y > map_y and self.movey >= 0:
                self.movey = 0
                self.rect.y = map_y-ty-ty

        def update(self, level):#en funsjon som opdaterer hva som skjer med spilleren
            #Dette legger merke til om spilleren er i kontakt med loot og plukker det opp
            global lvl
            loot_hit_list = pygame.sprite.spritecollide(self, loot_list, False)
            for loot in loot_hit_list:
                loot_list.remove(loot)
                self.score += 1

            #print(self.score)
            #Dette ser om spilleren kommer i kontakt med 'levelup' skiltet og gør at du kommer opp en level
            sign_hit_list = pygame.sprite.spritecollide(self, sign_list, False)
            '''
            if self.score >= 3:
                if self.lvlup == 0:
                    for sign in sign_hit_list:
                        if not self.rect.contains(sign):
                            self.lvlup = self.rect.colliderect(sign)
                if self.lvlup == 1:
                    levelup = self.rect.collidelist(sign_hit_list)
                    if levelup == -1:
                        self.lvl += 1
                        self.lvlup = 0
                        if self.lvl >= 2: 
                            sign_list.remove(sign)
            '''
            sign_hit_list = pygame.sprite.spritecollide(self, sign_list, False)
            for sign in sign_hit_list:
                lvl += 1
                self.health = 3
                sign_list.remove(sign)
                nextlevel()
                
            #dette sjekker om spilleren kommer i kontakt med en fiende og tar skade til
            enemy_hit_list = pygame.sprite.spritecollide(self, enemy_list, False)
            if self.damage == 0:
                for enemy in enemy_hit_list:
                    if not self.rect.contains(enemy):
                        self.damage = self.rect.colliderect(enemy)
            if self.damage == 1:
                skade = self.rect.collidelist(enemy_hit_list)
                pygame.mixer.Sound.play(oof)
                if skade == -1:
                    self.damage = 0
                    self.health -= 1
                    if self.health <= 0:
                        gameover()
            self.rect.x = self.rect.x + self.movex
            self.rect.y = self.rect.y + self.movey
            if self.is_jumping and self.is_falling is False:
                self.is_falling = True
                self.movey -= 33
            


            # beveg sprite til venstre

            if self.movex < 0:
                self.is_jumping = True
                self.frame += 1
                if self.frame > 3 * ani:
                    self.frame = 0
                self.image = pygame.transform.flip(self.images[self.frame//ani], True, False)
            
            # beveg sprite til høyre

            if self.movex > 0:
                self.is_jumping = True
                self.frame += 1
                if self.frame > 3 * ani:
                    self.frame = 0
                self.image = self.images[self.frame//ani]
            
            #dette ser om spilleren er i kontakt med spilleren
            ground_hit_list = pygame.sprite.spritecollide(self, ground_list, False)
            #dette ser om spilleren er i kontakt med en platform
            plat_hit_list = pygame.sprite.spritecollide(self, plat_list, False)
            for p in plat_hit_list:
                self.is_jumping = False
                self.movey=0
                if self.rect.bottom <= p.rect.bottom:
                    self.rect.bottom = p.rect.top
                else:
                    self.movey += 3.2


            for g in ground_hit_list:
                self.movey = 0
                self.rect.bottom = g.rect.top
                self.is_jumping = False # stopper hopping
                
            
            if self.rect.y > map_y:
                gameover()
            
        def jump(self):
            if self.is_jumping is False:
                self.is_falling = False
                self.is_jumping = True


    class Enemy(pygame.sprite.Sprite):
        def __init__(self,x,y,img,dist):    
            pygame.sprite.Sprite.__init__(self)
            self.images = []
            self.movex = 0
            self.movey = 0
            for i in range(1, 10):
                    img = pygame.image.load("grinch" + str(i) + '.png').convert()
                    img = pygame.transform.scale(img, (100,100))
                    img.convert_alpha()
                    img.set_colorkey(ALPHA)
                    self.images.append(img)
                    self.image = self.images[0]
                    self.rect = self.image.get_rect()
                    self.rect.x = x
                    self.rect.y = y
                    self.frame = 0 # tracker frame
                    self.counter = 0 # denne tracker hvor mye enemyen har beveget seg
                    self.distancetomove = dist
        def move(self):
            distance = self.distancetomove
            speed = 8
                
            if self.counter >= 0 and self.counter <= distance:
                self.rect.x += speed
                self.movex += -steps
            elif self.counter >= distance and self.counter <= distance*2:
                self.rect.x -= speed
                self.movex += steps
            else:
                self.counter = 0
                
            self.counter += 1
        def update(self,candypower, enemy_list):
            cane_hit_list = pygame.sprite.spritecollide(self, candypower, False)
            for cane in cane_hit_list:
                enemy_list.remove(self)
                candypower.remove(cane)

            # beveg sprite til venstre

            if self.movex < 0:
                self.frame += 1
                if self.frame > 3 * ani:
                    self.frame = 0
                self.image = pygame.transform.flip(self.images[self.frame//ani], True, False)
            
            # beveg sprite til høyre

            if self.movex > 0:
                self.frame += 1
                if self.frame > 3 * ani:
                    self.frame = 0
                self.image = self.images[self.frame//ani]

    class Level:
        
        def ground(lvl, gloc, tx, ty):
            ground_list = pygame.sprite.Group()
            i = 0
            platform_image = pygame.image.load("platform3" + '.png').convert()
            if lvl == 1:
                while i < len(gloc):
                    ground = Platform(gloc[i], map_y - ty, tx, ty, "platform3.png") # self, xpl, ypl, bldb, bldh, bld
                    ground_list.add(ground)
                    i = i + 1

            if lvl == 2:
                while i < len(gloc):
                    ground = Platform(gloc[i], map_y - ty, tx, ty, "platform3.png")
                    ground_list.add(ground)
                    i = i + 1
            
            if lvl == 3:
                pass # do something here

            return ground_list

        def enemyspawn(lvl, eloc):
            if lvl == 1:
                enemy = Enemy(eloc[0], eloc[1], 'enemy.png', 50) # bakerste tall = hvor langt de skal gå
                enemy2 = Enemy(eloc[2], eloc[3], 'enemy.png', 70)
                enemy3 = Enemy(eloc[4], eloc[5], 'enemy.png', 70)
                enemy_list = pygame.sprite.Group()
                enemy_list.add(enemy, enemy2, enemy3)
                return enemy_list
            if lvl == 2:
                print("Level " + str(lvl))
                enemy = Enemy(eloc[0], eloc[1], 'enemy.png', 50) # bakerste tall = hvor langt de skal gå
                enemy2 = Enemy(eloc[2], eloc[3], 'enemy.png', 70)
                enemy3 = Enemy(eloc[4], eloc[5], 'enemy.png', 70)
                enemy_list = pygame.sprite.Group()
                enemy_list.add(enemy, enemy2, enemy3)
                return enemy_list
            
        
        
        # x location, y location, img width, img height, img file
        def platform(lvl, tx, ty):
            plat_list = pygame.sprite.Group()
            ploc = []
            i = 0
            if lvl == 1:
                ploc.append((1000, map_y - ty - 128, 3))
                ploc.append((1500, map_y - ty - 256, 1))
                ploc.append((1600, map_y - ty - 420, 4))
                ploc.append((2500, map_y - ty - 420, 5))
                ploc.append((3500, map_y - ty - 600, 1))
                while i < len(ploc):
                    j = 0
                    while j <= ploc[i][2]:
                        plat = Platform((ploc[i][0] + (j * tx)), ploc[i][1], tx, ty, 'platform2.png')
                        plat_list.add(plat)
                        j = j + 1
                    i = i + 1

            if lvl == 2:
                ploc.append((700, 592, 2))
                ploc.append((1000, 352, 1))
                ploc.append((1300, 200, 4))
                while i < len(ploc):
                    j = 0
                    while j <= ploc[i][2]:
                        plat = Platform((ploc[i][0] + (j * tx)), ploc[i][1], tx, ty, 'platform2.png')
                        plat_list.add(plat)
                        j = j + 1
                    i = i + 1

            return plat_list

        def loot(lvl):
            lootimg = "loot.png"
            loot_list = pygame.sprite.Group()
            if lvl == 1:
                loot1 = Platform(1700, 210, 10, 10, lootimg)
                loot2 = Platform(2500, 210, 10, 10, lootimg)
                loot3 = Platform(3590, 30, 10, 10, lootimg)
                loot_list.add(loot1,loot2,loot3)
            

            if lvl == 2:
                loot1 = Platform(1000, 210, 10, 10, lootimg)
                loot2 = Platform(1500, 50, 10, 10, lootimg)
                loot3 = Platform(1700, 50, 10, 10, lootimg)
                loot_list.add(loot1,loot2,loot3)
                

            return loot_list
            
        def NextLevel(lvl):
            
            sign_list = pygame.sprite.Group()
            signimg = "levelup.png"
            sign1 = Platform(5000, 540, 10, 10, signimg)
            sign2 = Platform(6000, 540, 10, 10, signimg)
            sign3 = Platform(7000, 540, 10, 10, signimg)
            sign_list.add(sign1, sign2, sign3)
            return sign_list

        


    class Throwable(pygame.sprite.Sprite):
        def __init__(self, x, y, img, throw): # Throwable(player.rect.x,player.rect.y,'candycane.png',1)
            pygame.sprite.Sprite.__init__(self)
            self.image = pygame.image.load('candycane.png')
            self.image = pygame.transform.scale(self.image, (100,100))
            self.image.convert_alpha()
            self.image.set_colorkey(ALPHA)
            self.rect   = self.image.get_rect()
            self.rect.x = x
            self.rect.y = y
            self.firing = throw
        
        def update(self, map_y):
            canekill=player.rect.y + 40
            if self.rect.y < canekill:
                if player.høyre:
                    self.rect.x += 15
                else:
                    self.rect.x -= 15
                self.rect.y += 1

            else:
                self.kill()
                self.firing = 0





    # Set-up:
    def gameover():
        global main
        global gameover
        gameover = True
        is_gameover_enabled = True
        main = False

    def nextlevel():
        global main
        global nextlevel
        global is_nextlevel_enabled
        nextlevel = True
        is_nextlevel_enabled = True
        main = False
    
    pygame.display.set_caption("Rescue Santa: The Rescue")
    background=pygame.image.load("BG.png")
    clock = pygame.time.Clock()
    oof = pygame.mixer.Sound("oof.ogg")
    music = pygame.mixer.music.load("winteryloop.ogg")
    pygame.mixer.music.play(-1)


    backgroundbox = world.get_rect()


    player = Player()   # spawn spiller
    player.rect.x = 200   # tar spilleren til 0 på x aksen
    player.rect.y = 500   # tar spilleren til 0 på y aksen
    player_list = pygame.sprite.LayeredUpdates()
    player_list.add(player)
    steps = 10 # hvor mange pixels spriten beveger seg

    cane = Throwable(player.rect.x,player.rect.y,'candycane.png',0)
    candypower = pygame.sprite.Group()

    eloc = []
    if lvl == 1:
        eloc = [1000, 550, 2500, 250, 2580, 250]
    elif lvl == 2:
        eloc = [1000, 550, 1300, 60, 1360, 60]

    enemy_list = Level.enemyspawn(lvl, eloc) # level spawning

    gloc = []

    i=0

    while i <= (map_x/tx)+tx:
        gloc.append(i*tx)
        i=i+1
    ground_list = Level.ground(lvl,gloc,tx,ty)


    plat_list = Level.platform(lvl, tx, ty)

    loot_list = Level.loot(lvl)

    sign_list = Level.NextLevel(lvl)



    # Main-Loop:


    while main:
        plat_list.draw(world)
        #events = pygame.event.get()

        events = pygame.event.get()

        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                try:
                    sys.exit()
                finally:
                    main = False # her skrus selve motoren til koden av
            
            if event.type==pygame.KEYDOWN:
                if event.key==ord("q"):
                    pygame.quit()
                    try:
                        sys.exit()
                    finally:
                        main = False
            if event.type == pygame.KEYDOWN:
                if event.key == ord("p"):
                    startmenu.enable()
                    print(str(startmenu.is_enabled()))
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT or event.key == ord('a'):
                    player.control(-steps, 0)
                if event.key == pygame.K_RIGHT or event.key == ord('d'):
                    player.control(steps, 0)
                if event.key == pygame.K_UP or event.key == ord('w'):
                    player.control(0, -steps)
                    player.jump()
                if event.key == pygame.K_SPACE:
                    if not cane.firing:
                        cane = Throwable(player.rect.x,player.rect.y,'candycane.png',1)
                        candypower.add(cane)



            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT or event.key == ord('a'):
                    player.control(steps, 0)
                    player.høyre = False
                if event.key == pygame.K_RIGHT or event.key == ord('d'):
                    player.control(-steps, 0)
                    player.høyre = True
                if event.key == ord('q'):
                    pygame.quit()
                    sys.exit()
                    main = False
                

        #scroll fremover
        if player.rect.x >= fremx:
            scroll = player.rect.x - fremx
            player.rect.x = fremx
            for k in plat_list:
                k.rect.x -= scroll
            for e in enemy_list:
                e.rect.x -=scroll
            for a in ground_list:
                a.rect.x -=scroll
            for l in loot_list:
                l.rect.x -= scroll
            for c in candypower:
                c.rect.x -= scroll
            for p in sign_list:
                p.rect.x -= scroll
            #scroll bakover
        if player.rect.x <= bakx:
            scroll = bakx - player.rect.x
            player.rect.x = bakx
            for j in plat_list:
                j.rect.x +=scroll
            for f in enemy_list:
                f.rect.x += scroll
            for a in ground_list:
                a.rect.x+=scroll
            for t in loot_list:
                t.rect.x += scroll
            for s in candypower:
                s.rect.x += scroll
            for q in sign_list:
                q.rect.x +=scroll



        player.gravity() # caller funksjonen for å bruke gravitasjon (dette endrer noe som blir callet i player.update())
        player.update(lvl) # oppdater posisjonen med funksjonen vi har laget fra tidligere
        world.blit(background, backgroundbox)
        if cane.firing:
            cane.update(map_y)
            candypower.draw(world)
            enemy_list.update(candypower,enemy_list)
        player_list.draw(world)
        enemy_list.draw(world)
        ground_list.draw(world)
        plat_list.draw(world)
        loot_list.draw(world)
        sign_list.draw(world)

        if startmenu.is_enabled():
            if is_menu_disabled:
                startmenu.disable()
            else:
                startmenu.update(events)
                startmenu.draw(world)

        stats(player.score, player.health)
        for enemy_entity in enemy_list:
            enemy_entity.move()
        pygame.display.flip()
        clock.tick(fps)

    while nextlevel:
        events = pygame.event.get()

        if is_nextlevel_enabled:
            nextlevelmenu.update(events)
            nextlevelmenu.draw(world)

        else:
            main = True
            nextlevel = False
            nextlevelmenu.disable()

        pygame.display.flip()

    while gameover:
        events = pygame.event.get()
        
        if is_gameover_enabled:
            gameovermenu.update(events)
            gameovermenu.draw(world)

        else:
            main = True
            gameover = False
            nextlevelmenu.disable()

        
        pygame.display.flip()