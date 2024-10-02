USING_VS_CODE = True
MAX_LEVEL = 75

from typing import Any
import pygame, sys, random, math, os
pygame.init()

#create game window
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 900

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("loop error")

clock = pygame.time.Clock() 

#game variables
game_paused = True
menu_state = "main"

#define fonts
font = pygame.font.SysFont("arialblack", 40)

#define colours
WHITE = (255, 255, 255)
bgcolor = WHITE

LVLCOLORS = [(0,0,0), (255, 255, 255)]
BG_COLORS = [(255, 0, 0), (193, 236, 250), (255, 255, 224), (144, 238, 144), (255, 213, 128), (177, 156, 217), (180, 180, 180), (196, 164, 132), (255, 182, 193), (51, 51, 51), (128,128,0), (32,178,170), (85,107,47), (0,0,128), (139,0,139),
             (128,0,0), (188,143,143), (250,128,114), (112,128,144)]

STAR_REQUIREMENTS = [0, 6, 15, 24, 33, 42, 51, 60, 72, 84, 96, 108, 120, 132, 144, 156]
REQ_NEXT_BATCH = 0
GREATEST_LEVEL = 0

WEIRD_LEVELS = [51, 55, 59, 65, 69, 72]

fyx = 156
for i in range((len(os.listdir('maps'))-(len(STAR_REQUIREMENTS)-1))):
   STAR_REQUIREMENTS.append(fyx)
   fyx += 12

if USING_VS_CODE:
    TRUE_TILE_SIZE = 75
else:
    TRUE_TILE_SIZE = 50

TILE_SIZE = TRUE_TILE_SIZE



level = 1


COMPLETED_LEVELS = []
stars = 1000

tokens = 0

class Button():
	def __init__(self, x, y, image, scale):
		width = image.get_width()
		height = image.get_height()
		self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
		self.rect = self.image.get_rect()
		self.rect.topleft = (x, y)
		self.clicked = False

	def draw(self, surface):
		action = False
		#get mouse position
		pos = pygame.mouse.get_pos()

		#check mouseover and clicked conditions
		if self.rect.collidepoint(pos):
			if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
				self.clicked = True
				action = True

		if pygame.mouse.get_pressed()[0] == 0:
			self.clicked = False

		#draw button on screen
		surface.blit(self.image, (self.rect.x, self.rect.y))

		return action

def Image(path):
  return pygame.image.load(path).convert_alpha()

def audio(path):
    pygame.mixer.Sound.play(pygame.mixer.Sound(path))

#load button images
resume_img = pygame.image.load("buttons/play.svg").convert_alpha()
quit_img = pygame.image.load("buttons/exit.svg").convert_alpha()

#create button instances
resume_button = Button(75, 600, resume_img, 3)
quit_button = Button(950, 600, quit_img, 3)

def draw_text(text, font, text_col, x, y):
  img = font.render(text, True, text_col)
  screen.blit(img, (x, y))



gameOver = False

class LvlButton():
  def __init__(self, x, y, lvl):
    self.clicked = False
    self.lvlnum = lvl
    if stars >= STAR_REQUIREMENTS[int((str(int((self.lvlnum-1)/4+1))))-1]:
      if lvl == MAX_LEVEL:
        self.color = (255,255,255)
      else:
        try:
                  self.color = BG_COLORS[int((str(int((lvl-1)/4)+1)))-1]
        except IndexError:
                  self.color = BG_COLORS[int((str(int((lvl-1)/4+1))))-1]
    else:
       self.color = (128,128,128)
    self.image = pygame.Surface((75,75))
    self.image.fill(self.color)
    self.outline = pygame.Surface((75,75))
    self.outline.fill((0,0,0))
    self.rect = self.image.get_rect()
    self.rect.topleft = (x, y)
    

  def draw(self, surface):
    action = False
    pos = pygame.mouse.get_pos()

    if self.rect.collidepoint(pos):
      if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
        self.clicked = True
        action = True

    if pygame.mouse.get_pressed()[0] == 0:
      self.clicked = False

    surface.blit(self.outline, (self.rect.x, self.rect.y))
    surface.blit(self.image, (self.rect.x, self.rect.y))

    if self.lvlnum in COMPLETED_LEVELS:
       draw_text(f'{self.lvlnum}', pygame.font.Font("fonts/queen.ttf", 30), (0,255,0), self.rect.x+20, self.rect.y+20)
    elif self.lvlnum in WEIRD_LEVELS:
      draw_text(f'{self.lvlnum}', pygame.font.Font("fonts/queen.ttf", 30), (255,255,255), self.rect.x+20, self.rect.y+20)
    else:
       draw_text(f'{self.lvlnum}', pygame.font.Font("fonts/queen.ttf", 30), (0,0,0), self.rect.x+20, self.rect.y+20)

    return action

level_buttons = []
lx = 40
ly = 40
for i in range(len(os.listdir('maps'))-1):
   if i % 15 == 0:
      ly += 75
      lx = 40
   level_buttons.append(LvlButton(lx, ly, i+1))
   lx += 75


class Player(pygame.sprite.Sprite):
    def __init__(self, game, pos):
      self.groups = game.all_sprites
      pygame.sprite.Sprite.__init__(self, self.groups)
      self.game = game


      self.image = Image('tiles/blue_sq.svg')
      self.color = 'blue'
      self.rect = self.image.get_rect(center=pos)
      self.speed = TILE_SIZE

      self.key_held = ''
      self.previous_key_held = ''
      self.any_key_held = False

      self.moves = []
      self.move_interval = 0
      self.move_index = 0
      self.max_move_interval = 12

      self.portaling = False

    def get_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.key_held = 'LEFT'
            self.any_key_held = True
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.key_held = 'RIGHT'
            self.any_key_held = True
        elif keys[pygame.K_UP] or keys[pygame.K_w]:
            self.key_held = 'UP'
            self.any_key_held = True
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.key_held = 'DOWN'
            self.any_key_held = True
        else:
            self.key_held = ''


        if self.previous_key_held != self.key_held:
          if self.key_held == 'LEFT':
              self.rect.x -= self.speed
              self.moves.append('L')
          if self.key_held == 'RIGHT':
              self.rect.x += self.speed
              self.moves.append('R')
          if self.key_held == 'UP':
              self.rect.y -= self.speed
              self.moves.append('U')
          if self.key_held == 'DOWN':
              self.rect.y += self.speed  
              self.moves.append('D')
                
        
        self.previous_key_held = self.key_held

    def loop_input(self):
        if self.move_index >= len(self.moves):
            self.move_index = 0
        
        if self.move_interval >= self.max_move_interval:
          move = self.moves[self.move_index]
          if level in WEIRD_LEVELS:
            Vortex(self.game, (self.rect.centerx, self.rect.centery), 1)    
          if move == 'L':
              self.rect.x -= self.speed
          if move == 'R':
              self.rect.x += self.speed
          if move == 'U':
              self.rect.y -= self.speed
          if move == 'D':
              self.rect.y += self.speed  

          self.move_index += 1
          self.move_interval = 0

        self.move_interval += 1


    def update(self):
        if pygame.sprite.spritecollideany(self, self.game.control):
          self.get_input()
        else:
          self.loop_input()
        if self.rect.x < 0 or self.rect.x > SCREEN_WIDTH or self.rect.y < 0 or self.rect.y > SCREEN_HEIGHT:
            self.kill()
            audio('audio/crash.wav')
            self.game.death(True)
            pygame.time.wait(200)

        color = self.color
        if color == 'blue':
          self.image = Image('tiles/blue_sq.svg')
        elif color == 'yellow':
          self.image = Image('tiles/yellow_sq.svg')
        elif color == 'orange':
          self.image = Image('tiles/orange_sq.svg')
        elif color == 'purple':
          self.image = Image('tiles/purple_sq.svg')
          

class ControlTile(pygame.sprite.Sprite):
    def __init__(self, game, pos):
      self.groups = game.all_sprites, game.control
      pygame.sprite.Sprite.__init__(self, self.groups)
      self.game = game

      # self.image = Image('tiles/control.svg')
      # self.image = pygame.transform.scale(self.image, (TILE_SIZE, TILE_SIZE))
      self.image = pygame.Surface((TILE_SIZE,TILE_SIZE))
      self.image.fill((0,0,0))
      self.rect = self.image.get_rect(center=pos)

class Token(pygame.sprite.Sprite):
    def __init__(self, game, pos, type):
      self.groups = game.all_sprites, game.tokens
      pygame.sprite.Sprite.__init__(self, self.groups)
      self.game = game
      if type == 1:
        self.image = Image('tiles/token_mid.svg')
        self.color = 'blue'
      elif type == 2:
        self.image = Image('tiles/token_small.svg')
        self.color = 'orange'
      elif type == 3:
        self.image = Image('tiles/token_large.svg')
        self.color = 'purple'
      elif type == 4:
        self.image = Image('tiles/token_mid_2.svg')
        self.color = 'yellow'
        
      # self.image = pygame.transform.scale(self.image, (TILE_SIZE, TILE_SIZE))
      self.rect = self.image.get_rect(center=pos)
    
    def update(self):
        if pygame.sprite.collide_rect(self, self.game.player):
            if self.game.player.color == self.color:
              global tokens; tokens += 1
              audio('audio/notification.wav')
              self.kill()

class MovingToken(pygame.sprite.Sprite):
    def __init__(self, game, pos, type, way):
      self.groups = game.all_sprites, game.tokens
      pygame.sprite.Sprite.__init__(self, self.groups)
      self.game = game
      if type == 1:
        self.image = Image('tiles/token_mid.svg')
        self.color = 'blue'
      elif type == 2:
        self.image = Image('tiles/token_small.svg')
        self.color = 'orange'
      elif type == 3:
        self.image = Image('tiles/token_large.svg')
        self.color = 'purple'
      elif type == 4:
        self.image = Image('tiles/token_mid_2.svg')
        self.color = 'yellow'
        
      # self.image = pygame.transform.scale(self.image, (TILE_SIZE, TILE_SIZE))
      self.rect = self.image.get_rect(center=pos)
      self.dir = 1
      self.way = way
      if level==50:
          self.way = 'y'
    
    def update(self):
        if self.way == 'x':
          self.rect.x += self.dir * 3
        else:
           self.rect.y += self.dir * 3
        if pygame.sprite.spritecollideany(self, self.game.control) or (self.rect.x < 0 or self.rect.x > SCREEN_WIDTH - 75 or self.rect.y < 0 or self.rect.y > SCREEN_HEIGHT - 75):
          self.dir *= -1
          if self.way == 'x':
            self.rect.x += self.dir * 15
          else:
            self.rect.y += self.dir * 15

        if level > 60 and (level!=68):
          if pygame.sprite.spritecollideany(self, self.game.vortexes):
            self.dir *= -1
            if self.way == 'x':
              self.rect.x += self.dir * 15
            else:
              self.rect.y += self.dir * 15
           
           
        if pygame.sprite.collide_rect(self, self.game.player):
            if self.game.player.color == self.color:
              global tokens; tokens += 1
              audio('audio/notification.wav')
              self.kill()

class Paint(pygame.sprite.Sprite):
    def __init__(self, game, pos, color):
      self.groups = game.all_sprites
      pygame.sprite.Sprite.__init__(self, self.groups)
      self.game = game
      self.color = color
      if color == 'blue':
        self.image = Image('tiles/blue_sq.svg')
      elif color == 'yellow':
        self.image = Image('tiles/yellow_sq.svg')
      elif color == 'orange':
        self.image = Image('tiles/orange_sq.svg')
      elif color == 'purple':
        self.image = Image('tiles/purple_sq.svg')
        
      self.rect = self.image.get_rect(center=pos)
    
    def update(self):
        if pygame.sprite.collide_rect(self, self.game.player):
            self.game.player.color = self.color
            audio('audio/paint.wav')
            self.kill()

class Portal(pygame.sprite.Sprite):
    def __init__(self, game, pos, channel):
      self.groups = game.all_sprites, game.portals
      pygame.sprite.Sprite.__init__(self, self.groups)
      self.game = game
      self.channel = channel
      self.image = Image('tiles/portal.svg')
      self.rect = self.image.get_rect(center=pos)
    
    def update(self):
      if not self.game.player.portaling:
        if pygame.sprite.collide_rect(self, self.game.player):
            for portal in self.game.portals:
              print(self.game.portals)
              if portal != self:
                if portal.channel == self.channel:
                  audio('audio/Zoop.wav')
                  self.game.player.portaling = True
                  portal.kill()
                  self.game.player.rect.x,self.game.player.rect.y = portal.rect.topleft[0] + 5, portal.rect.topleft[1] + 5
              
        else:
           self.game.player.portaling = False

class Vortex(pygame.sprite.Sprite):
    def __init__(self, game, pos, type):
      self.groups = game.all_sprites, game.vortexes
      pygame.sprite.Sprite.__init__(self, self.groups)
      self.game = game
      if type == 1:
        self.image = Image('tiles/vortex_mid.svg')
      elif type == 2:
        self.image = Image('tiles/vortex_small.svg')
      elif type == 3:
        self.image = Image('tiles/vortex_large.svg')

      self.rect = self.image.get_rect(center=pos)
    
    def update(self):
        if pygame.sprite.collide_rect(self, self.game.player):
            self.kill()
            audio('audio/crash.wav')
            self.game.death(True)
            pygame.time.wait(200)


class Map:
    def __init__(self, filename):
        self.data = []
        with open(filename, 'rt') as main_file:
            for line in main_file:
                self.data.append(line.strip())

        self.tilewidth = len(self.data[0])
        self.tileheight = len(self.data)
        self.width = self.tilewidth * TILE_SIZE
        self.height = self.tileheight * TILE_SIZE

trans_y1 = 0
trans_y2 = 0

class Game():
    def __init__(self):
        self.max_tokens = math.inf
        self.transition = False
    
    def new_game(self):
        self.map = Map(f'maps/{level}.txt')

        self.all_sprites = pygame.sprite.Group()
        self.control = pygame.sprite.Group()
        self.tokens = pygame.sprite.Group()
        self.vortexes = pygame.sprite.Group()
        self.portals = pygame.sprite.Group()


        global tokens; tokens = 0

        global TILE_SIZE
        TILE_SIZE=TRUE_TILE_SIZE

        self.makemap()

    def makemap(self):
        self.max_tokens = 0
        for row, tiles in enumerate(self.map.data):
            for col, tile in enumerate(tiles):
                x = col * TILE_SIZE + (TILE_SIZE/2)
                y = row * TILE_SIZE + (TILE_SIZE/2)

                if tile == '!':
                    ControlTile(self, (x, y))

                if tile == '1':
                    Token(self, (x, y), 1)
                    self.max_tokens += 1

                if tile == '2':
                    Token(self, (x, y), 2)
                    self.max_tokens += 1

                if tile == '3':
                    Token(self, (x, y), 3)
                    self.max_tokens += 1

                if tile == '4':
                    Token(self, (x, y), 4)
                    self.max_tokens += 1


                if tile == '5':
                    MovingToken(self, (x, y), 1, 'x')
                    self.max_tokens += 1

                if tile == '6':
                    MovingToken(self, (x, y), 2, 'x')
                    self.max_tokens += 1

                if tile == '7':
                    MovingToken(self, (x, y), 3, 'y')
                    self.max_tokens += 1

                if tile == '8':
                    MovingToken(self, (x, y), 4, 'y')
                    self.max_tokens += 1

                if tile == 'A':
                    Vortex(self, (x, y), 1)

                if tile == 'B':
                    Vortex(self, (x, y), 2)

                if tile == 'C':
                    Vortex(self, (x, y), 3)

                if tile == 'Y':
                    Paint(self, (x, y), 'yellow')

                if tile == 'O':
                    Paint(self, (x, y), 'orange')

                if tile == 'L':
                    Paint(self, (x, y), 'blue')
                  
                if tile == 'U':
                    Paint(self, (x, y), 'purple')

                if tile == 'E':
                    Portal(self, (x, y), 1)

                if tile == 'F':
                    Portal(self, (x, y), 2)

                if tile == 'G':
                    Portal(self, (x, y), 3)



        for row, tiles in enumerate(self.map.data):
            for col, tile in enumerate(tiles):
                x = col * TILE_SIZE + (TILE_SIZE/2)
                y = row * TILE_SIZE + (TILE_SIZE/2)
                if tile == 'P':
                    ControlTile(self, (x, y))
                    self.player = Player(self, (x, y))

    def death(self, KILL):
        for object in self.all_sprites:
            object.kill()
        if KILL:
          self.new_game()
        else:
            self.transition = True
            global trans_y1, trans_y2
            trans_y1 = -300
            trans_y2 = SCREEN_HEIGHT/2-150

    def update(self):
        global tokens
        self.all_sprites.update()
        if tokens >= self.max_tokens:
            global COMPLETED_LEVELS
            global level
            tokens = 0
            if not (level in COMPLETED_LEVELS):
               global stars; stars += 3
               COMPLETED_LEVELS.append(level)
            
            level += 1
          
            if stars >= STAR_REQUIREMENTS[int((str(int((level-1)/4+1))))-1]:
              self.death(False)
              audio('audio/new_level.wav')
              pygame.time.wait(400)
            else:
              global menu_state, game_paused
              game_paused = True
              audio('audio/new_level.wav')
              pygame.time.wait(400)
              menu_state = "levels"

        global TILE_SIZE
        TILE_SIZE=TRUE_TILE_SIZE

    def draw(self):
        global bgcolor
        if lvl == MAX_LEVEL:
          bgcolor = (255,255,255)
        else:
          try:
            bgcolor = BG_COLORS[int((str(int((level-1)/4)+1)))-1]
          except IndexError:
              bgcolor = BG_COLORS[int((str(int((level-1)/4+1))))-1]
        screen.fill(bgcolor)
        for sprite in self.all_sprites:
            screen.blit(sprite.image, (sprite.rect.x, sprite.rect.y))
        if level == 1:
            draw_text(f"hello there | use arrow keys/WASD to move | collect all tokens | every action you do in the black loops.", pygame.font.Font("fonts/queen.ttf", 25), (255,255,255), 15, 15)
        elif level == 2:
            draw_text(f"every action you do in the black loops.", pygame.font.Font("fonts/queen.ttf", 55), (255,255,255), 15, 15)
        elif level == 5:
            draw_text(f"do not touch an edge or a black dot.", pygame.font.Font("fonts/queen.ttf", 55), (255,0,0), 10, 15)
        elif level == 10:
            draw_text(f"you need to be the color of the token you collect.", pygame.font.Font("fonts/queen.ttf", 44), (255,0,0), 15, 15)
        

    def run(self):
        self.update()
        global trans_y2, trans_y1
        if self.transition:
            global bgcolor
            if lvl == MAX_LEVEL:
              bgcolor = (255,255,255)
            else:
                try:
                    bgcolor = BG_COLORS[int((str(int((level-1)/4)+1)))-1]
                except IndexError:
                    bgcolor = BG_COLORS[int((str(int((level-1)/4+1))))-1]
            screen.fill(bgcolor)

            if trans_y1 >= SCREEN_HEIGHT/2-150:
                trans_y1 = SCREEN_HEIGHT/2-150
                trans_y2 = 2000
                draw_text(f"click to continue.", pygame.font.Font("fonts/queen.ttf", 50), (0,0,0), 15, 15)
                if pygame.mouse.get_pressed()[0] == 1:
                  if level > MAX_LEVEL:
                    pygame.time.wait(300)
                    global menu_state; menu_state = "levels"
                    global game_paused; game_paused = True
                  else:
                    self.transition = False
                    self.new_game()
                  

            else:
                trans_y1 += 10
                trans_y2 += 10

            draw_text(f"{level-1}", pygame.font.Font("fonts/queen.ttf", 170), (0,0,0), SCREEN_WIDTH/2-75, trans_y2)
            if level > MAX_LEVEL:
               draw_text(f"THE END", pygame.font.Font("fonts/queen.ttf", 170), (0,0,0), 10, trans_y1)
               draw_text(f"thank you for playing.", pygame.font.Font("fonts/queen.ttf", 50), (0,0,0), 25, trans_y1 + 170)
            else:
              draw_text(f"{level}", pygame.font.Font("fonts/queen.ttf", 170), (0,0,0), SCREEN_WIDTH/2-75, trans_y1)

        else:
          self.draw()


powerhouse = Game()

#game loop
run = True
while run:

  #check if game is paused
  if game_paused == True:
    if menu_state == "main":
      screen.fill((230,230,230))

      if resume_button.draw(screen):
        audio('audio/notification.wav')
        menu_state = 'levels'
        

      if quit_button.draw(screen):
        run = False

      draw_text("loop error.", pygame.font.Font("fonts/queen.ttf", 145), (0,0,0), 300, 100)

    elif menu_state == 'levels':
      screen.fill((230,230,230))
      draw_text(f"stars: {stars}", pygame.font.Font("fonts/queen.ttf", 45), (0,0,0), 15, 15)
      draw_text(f"next set of levels unlock in {REQ_NEXT_BATCH - stars} stars ({stars}/{STAR_REQUIREMENTS[int((str(int((GREATEST_LEVEL-1)/4+1))))-1]})", pygame.font.Font("fonts/queen.ttf", 32), (0,0,0), 15, 60)

      for req in STAR_REQUIREMENTS:
         if stars < req:
            REQ_NEXT_BATCH = req
            GREATEST_LEVEL = (STAR_REQUIREMENTS.index(req) + 1) * 4
            break
         
      for lvl in level_buttons:
          if lvl.draw(screen):
            if stars >= STAR_REQUIREMENTS[int((str(int((lvl.lvlnum-1)/4+1))))-1]:
              level = lvl.lvlnum
              audio('audio/notification.wav')
              gameOver = False
              game_paused = False
              if level == 59:
                TRUE_TILE_SIZE = 54
              elif level == 71 or level == 72:
                 TRUE_TILE_SIZE = 68
              else:
                if USING_VS_CODE:
                      TRUE_TILE_SIZE = 75
                else:
                      TRUE_TILE_SIZE = 50
              powerhouse.new_game()
  else:
    powerhouse.run()


  #event handler
  for event in pygame.event.get():
    if event.type == pygame.KEYDOWN:
      if event.key == pygame.K_q:
        game_paused = True
        level_buttons = []
        lx = 40
        ly = 40
        for i in range(len(os.listdir('maps'))-1):
          if i % 15 == 0:
              ly += 75
              lx = 40
          level_buttons.append(LvlButton(lx, ly, i+1))
          lx += 75
    if event.type == pygame.QUIT:
      run = False

  clock.tick(60)
  pygame.display.update()

pygame.quit()