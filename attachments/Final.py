import pygame
from pygame.locals import *
from pygame import mixer
from os import path

#Initialize pygame and mixer
pygame.mixer.pre_init(44100, -16, 2, 512)
mixer.init()
pygame.init()

#Fps
clock = pygame.time.Clock()
fps = 60

#Define the screen width and height
screen_width = 1000
screen_height = 1000

#Set the display and name of the game
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Hades: Escape From Undertale')

#Define font
font = pygame.font.SysFont('Comic Sans 93', 70)
font_score = pygame.font.SysFont('Comic Sans 93', 30)

#Define game variables
tile_size = 50
game_over = 0
main_menu = True
level = 1
score = 0

#Define colours
white = (255, 255, 255)
blue = (0, 0, 255)

#Load images and sounds
bg_img = pygame.image.load('background.png')
restart_img = pygame.image.load('restart_btn.png')
start_img = pygame.image.load('start_btn.png')
exit_img = pygame.image.load('exit_btn.png')
pygame.mixer.music.load('music.wav')
pygame.mixer.music.set_volume(0.2)
pygame.mixer.music.play(-1, 0.0, 5000)
coin_fx = pygame.mixer.Sound('coin.wav')
coin_fx.set_volume(0.5)
jump_fx = pygame.mixer.Sound('jump.wav')
jump_fx.set_volume(0.5)
game_over_fx = pygame.mixer.Sound('game_over.wav')
game_over_fx.set_volume(0.5)

#Define the draw text function to display the score
def draw_text(text, font, text_col, x, y,):
	img = font.render(text, True, text_col)
	screen.blit(img, (x, y))

#To reset the level and load a new level
def reset_level(level):
        player.reset(100, screen_height - 130)
        
        #Empty all the groups
        enemy_group.empty()
        lava_group.empty()
        exit_group.empty()
        coin_group.empty()

        #Load a map depending on the level.
        if level == 2:
                game_map = load_map('map2')
        elif level == 3:
                game_map = load_map('map3')
        elif level == 4:
                game_map = load_map('map4')
        elif level == 5:
                game_map = load_map('map5')
        elif level == 6:
                game_map = load_map('map6')
        elif level == 7:
                game_map = load_map('map7')
        elif level == 8:
                game_map = load_map('map8')
        elif level == 9:
                game_map = load_map('map9')
        else:
                game_map = load_map('end')
                
        world = World(game_map)

        return world
                


class Button():
        def __init__(self, x, y, image):
                self.image = image
                self.rect = self.image.get_rect()
                self.rect.x = x
                self.rect.y = y
                self.clicked = False

        def draw(self):
                action = False

                #get mouse position
                pos = pygame.mouse.get_pos()

                #check mouseover and clicked conditions
                if self.rect.collidepoint(pos):
                        if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                                action = True
                                self.clicked = True

                if pygame.mouse.get_pressed()[0] == 0:
                        self.clicked = False


                #draw button
                screen.blit(self.image, self.rect)

                return action

class Player():
        def __init__(self, x, y):
                self.reset(x, y)

        def update(self, game_over):
                dx = 0
                dy = 0
                walk_cooldown = 5

                if game_over == 0:
                        #get keypresses
                        key = pygame.key.get_pressed()
                        if key[pygame.K_w] and self.jumped == False and self.in_air == False:
                                jump_fx.play()
                                self.vel_y = -18
                                self.jumped = True
                        if key[pygame.K_w] == False:
                                self.jumped = False
                        if key[pygame.K_a]:
                                
                                dx -= 5
                                self.counter += 1
                                self.direction = -1
                        if key[pygame.K_d]:
                                dx += 5
                                self.counter += 1
                                self.direction = 1
                        if key[pygame.K_a] == False and key[pygame.K_d] == False:
                                self.counter = 0
                                self.index = 0
                                if self.direction == 1:
                                        self.image = self.images_right[self.index]
                                if self.direction == -1:
                                        self.image = self.images_left[self.index]

                        #handle animation
                        if self.counter > walk_cooldown:
                                self.counter = 0        
                                self.index += 1
                                if self.index >= len(self.images_right):
                                        self.index = 0
                                if self.direction == 1:
                                        self.image = self.images_right[self.index]
                                if self.direction == -1:
                                        self.image = self.images_left[self.index]


                        #add gravity
                        self.vel_y += 1
                        if self.vel_y > 10:
                                self.vel_y = 10
                        dy += self.vel_y

                        #check for collision
                        self.in_air = True
                        for tile in world.tile_list:
                                #check for collision in x direction
                                if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                                        dx = 0
                                #check for collision in y direction
                                if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                                        #check if below the ground i.e. jumping
                                        if self.vel_y < 0:
                                                dy = tile[1].bottom - self.rect.top
                                                self.vel_y = 0
                                        #check if above the ground i.e. falling
                                        elif self.vel_y >= 0:
                                                dy = tile[1].top - self.rect.bottom
                                                self.vel_y = 0
                                                self.in_air = False


                        #check for collision with enemies
                        if pygame.sprite.spritecollide(self, enemy_group, False):
                                game_over = -1
                                game_over_fx.play()

                        #check for collision with lava
                        if pygame.sprite.spritecollide(self, lava_group, False):
                                game_over = -1
                                game_over_fx.play()

                        #check for collision with exit
                        if pygame.sprite.spritecollide(self, exit_group, False):
                                game_over = 1


                        #update player coordinates
                        self.rect.x += dx
                        self.rect.y += dy


                elif game_over == -1:
                        self.image = self.dead_image
                        if self.rect.y > 200:
                                self.rect.y -= 5

                #draw player onto screen
                screen.blit(self.image, self.rect)

                return game_over
        
        def reset(self, x, y):
                self.images_right = []
                self.images_left = []
                self.index = 0
                self.counter = 0
                for num in range(1, 4):
                        img_right = pygame.image.load(f'player{num}.png')
                        img_right = pygame.transform.scale(img_right, (40, 80))
                        img_left = pygame.transform.flip(img_right, True, False)
                        self.images_right.append(img_right)
                        self.images_left.append(img_left)
                self.dead_image = pygame.image.load('ghost.png')
                self.image = self.images_right[self.index]
                self.rect = self.image.get_rect()
                self.rect.x = x
                self.rect.y = y
                self.width = self.image.get_width()
                self.height = self.image.get_height()
                self.vel_y = 0
                self.jumped = False
                self.direction = 0
                self.in_air = True


class World():
        def __init__(self, data):
                self.tile_list = []

                #load images
                dirt_img = pygame.image.load('dirt.png')
                grass_img = pygame.image.load('grass.png')

                row_count = 0
                for row in data:
                        col_count = 0
                        for tile in row:
                                if tile == '1':
                                        img = pygame.transform.scale(dirt_img, (tile_size, tile_size))
                                        img_rect = img.get_rect()
                                        img_rect.x = col_count * tile_size
                                        img_rect.y = row_count * tile_size
                                        tile = (img, img_rect)
                                        self.tile_list.append(tile)
                                if tile == '2':
                                        img = pygame.transform.scale(grass_img, (tile_size, tile_size))
                                        img_rect = img.get_rect()
                                        img_rect.x = col_count * tile_size
                                        img_rect.y = row_count * tile_size
                                        tile = (img, img_rect)
                                        self.tile_list.append(tile)
                                if tile == '3':
                                        enemy = Enemy(col_count * tile_size, row_count * tile_size + 15)
                                        enemy_group.add(enemy)
                                if tile == '6':
                                        lava = Lava(col_count * tile_size, row_count * tile_size + (tile_size // 2))
                                        lava_group.add(lava)
                                if tile == '7':
                                        coin = Coin(col_count * tile_size + (tile_size // 2), row_count * tile_size + (tile_size // 2))
                                        coin_group.add(coin)
                                if tile == '8':
                                        exit = Exit(col_count * tile_size, row_count * tile_size - (tile_size // 2))
                                        exit_group.add(exit)
                                

                                col_count += 1
                        row_count += 1

        def draw(self):
                for tile in self.tile_list:
                        screen.blit(tile[0], tile[1])

class Coin(pygame.sprite.Sprite):
        def __init__(self, x, y):
                pygame.sprite.Sprite.__init__(self)
                img = pygame.image.load('coin.png')
                self.image = pygame.transform.scale(img, (tile_size // 2, tile_size // 2))
                self.rect = self.image.get_rect()
                self.rect.center = (x, y)

class Enemy(pygame.sprite.Sprite):
        def __init__(self, x, y):
                pygame.sprite.Sprite.__init__(self)
                self.image = pygame.image.load('enemy.png')
                self.rect = self.image.get_rect()
                self.rect.x = x
                self.rect.y = y
                self.move_direction = 1
                self.move_counter = 0

        def update(self):
                self.rect.x += self.move_direction
                self.move_counter += 1
                if abs(self.move_counter) > 50:
                        self.move_direction *= -1
                        self.move_counter *= -1


class Lava(pygame.sprite.Sprite):
        def __init__(self, x, y):
                pygame.sprite.Sprite.__init__(self)
                img = pygame.image.load('lava.png')
                self.image = pygame.transform.scale(img, (tile_size, tile_size // 2))
                self.rect = self.image.get_rect()
                self.rect.x = x
                self.rect.y = y

class Exit(pygame.sprite.Sprite):
        def __init__(self, x, y):
                pygame.sprite.Sprite.__init__(self)
                img = pygame.image.load('exit.png')
                self.image = pygame.transform.scale(img, (tile_size, int(tile_size * 1.5)))
                self.rect = self.image.get_rect()
                self.rect.x = x
                self.rect.y = y



def load_map(path):     
    f = open(path +'.txt', 'r')
    data = f.read()
    f.close()
    data = data.split('\n')
    game_map = []
    for row in data:
        game_map.append(list(row))
    return game_map

game_map = load_map('map1')


player = Player(100, screen_height - 130)

enemy_group = pygame.sprite.Group()
lava_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()
coin_group = pygame.sprite.Group()


world = World(game_map)

#create buttons
restart_button = Button(screen_width // 2 - 50, screen_height // 2 + 100, restart_img)
start_button = Button(screen_width // 2 - 350, screen_height // 2, start_img)
exit_button = Button(screen_width // 2 + 150, screen_height // 2, exit_img)

run = True
while run:

        clock.tick(fps)

        screen.blit(bg_img, (0, 0))
                        
        if main_menu == True:
                if exit_button.draw():
                        run = False
                if start_button.draw():
                        main_menu = False

        else:
                
                world.draw()

                if game_over == 0:
                        enemy_group.update()
                        #update score
                        #check if a coin has been collected
                        if pygame.sprite.spritecollide(player, coin_group, True):
                                score += 1
                                coin_fx.play()
                        draw_text('Coins: ' + str(score), font_score, white, tile_size - 0, 0,)

                #Draw all the sprites stored on the map
                enemy_group.draw(screen)
                lava_group.draw(screen)
                exit_group.draw(screen)
                coin_group.draw(screen)

                #Check if game over
                game_over = player.update(game_over)

                #If the player died
                if game_over == -1:
                        if restart_button.draw():
                                world_data = []
                                world = reset_level(level)
                                game_over = 0

                #If the player has reached the end go to the next level
                if game_over == 1:
                        level += 1
                        game_map = []
                        world = reset_level(level)
                        game_over = 0

        #If the player clicks exit, quit
        for event in pygame.event.get():
                if event.type == pygame.QUIT:
                        run = False

        #Update the display
        pygame.display.update()

pygame.quit()
