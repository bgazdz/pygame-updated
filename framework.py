import sys
import os
import math
import vector
import random
random.seed()
from menu import *
# Global Bullet list
bullet_list = pygame.sprite.Group()
# Global enemy list
enemy_list = pygame.sprite.Group()
#Globbal shovel list
shovel_list = pygame.sprite.Group()
# Global bullet size
bullet_size = 0
#global enemy count
enemy_count = 0
#Global shovel amounts on screen (can only have one)
shovel = 0
#Global score
score = 0

#For movement between Menu, game, and death screens
class GameEngine:
    def __init__(self):
        # initialize pygame
        pygame.init()
        # create the window
        size = width, height = 718, 480
        screen = pygame.display.set_mode(size)

        # set the window title
        pygame.display.set_caption("Rico-ja")
        states = [main(), event_loop(), game_over()]


    def run(self):
        while(True):
            main()

class Player(pygame.sprite.Sprite):
    # constructor for this class
    def __init__(self):
        # call the parent class (Sprite) constructor
        pygame.sprite.Sprite.__init__(self)
        #load player pistol PNG
        self.image = pygame.image.load(os.path.join('images', 'player_pistol.png'))
        self.original_image = self.image.copy()
        self.rect = self.image.get_rect()
        self.rect.x = 718/2
        self.rect.y = 240
        self.speed = [0, 0]
        self.health = 100

        #starts facing east
        self.angle = 0
        self.face_vector = [1, 0]

    def left(self):
        self.speed[0] -= 10

    def right(self):
        self.speed[0] += 10

    def up(self):
        self.speed[1] -= 10

    def down(self):
        self.speed[1] += 10

    def move(self):
        # move the rect by the displacement ("speed")
        self.rect.x += self.speed[0]*self.health/100 * (1 + .25 * score / 25)
        self.rect.y += self.speed[1]*self.health/100 * (1 + .25 * score / 25)

    def rotate(self, mouse_location):
        # get the mouse location
        x, y = mouse_location
        # get the vector difference of the players location and the mouse
        move_vector = [x - self.rect.centerx, y - self.rect.centery]
        self.angle = math.degrees(math.atan2(*move_vector)) - 90
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)

    def fire(self, mouse_location):
        global bullet_size
        if bullet_size < 20:
            bullet = Bullet()
            start_x, start_y = Bullet.calculate_start(self, mouse_location)
            bullet.rect.centerx = start_x
            bullet.rect.centery = start_y
            bullet.speed[0] = math.cos(math.radians(self.angle))*bullet.base_speed
            bullet.speed[1] = -math.sin(math.radians(self.angle))*bullet.base_speed
            bullet_list.add(bullet)
            bullet_size += 1

    #lose 10 health upon enemy hit
    def lose_health_enemy(self):
        self.health -= 10
        if(self.health <= 0) :
            self.death()

    #lose 25 health upon bullet hit
    def lose_health_bullet(self):
        self.health -= 25
        if(self.health <= 0) :
            self.death()

    def death(self):
        game_over()

    #Weapon action
    def shovel(self):
        shovel_list.empty()
        enemy_list.empty()
        bullet_list.empty()
        global enemy_count
        global bullet_size
        global score
        global shovel
        score += enemy_count
        enemy_count = 0
        bullet_size = 0
        shovel = 0
        # set up the score text
        # set up font
        basic_font = pygame.font.SysFont(None, 100)
        text = basic_font.render('BOOM!', True, (255, 255, 255))
        text_rect = text.get_rect()
        text_rect.x = 200
        text_rect.y = 200

        # draw the text onto the surface
        screen = pygame.display.get_surface()
        screen_rect = screen.get_rect()
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        count = 0
        while(count < 100):
            screen.blit(text, text_rect)
            count += 1
            # update the screen
            pygame.display.flip()


class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        # load the PNG
        self.image = pygame.image.load(os.path.join('images', 'ninja.png'))
        self.rect = self.image.get_rect()
        self.rect.topleft = 0, 0


# Bullet sprite
class Bullet(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface([10, 10])
        self.image.fill(WHITE)
        self.speed = [0,0]
        self.base_speed = 20
        self.rect = self.image.get_rect()

    @staticmethod
    def calculate_start(sprite, mouse_location):
        mouse_x, mouse_y = mouse_location
        sprite_center = [sprite.rect.centerx, sprite.rect.centery]
        move_vector = [mouse_x - sprite.rect.centerx, mouse_y - sprite.rect.centery]
        # normalize the move vector
        unit_move_vector = [move_vector[0] / vector.length(move_vector), move_vector[1] / vector.length(move_vector)]
        # calculate distance between the center of the player and the potential bullet start point
        distance = vector.distance(sprite_center, [sprite_center[0] + unit_move_vector[0], sprite_center[1] + unit_move_vector[1]])
        # One number above the radius of the circle circumscribing the player sprite
        radius = hitbox_radius = math.ceil((sprite.image.get_width()/2) * math.sqrt(2))
        # ensure that the bullet starts outside of the player hitbox
        while distance < hitbox_radius:
            move_vector = vector.multiply_scalar(unit_move_vector, radius)
            distance = vector.distance(sprite_center, [sprite_center[0] + move_vector[0], sprite_center[1] + move_vector[1]])
            radius += 1  # raise me to lower iterations but possibly increase start distance

        return sprite_center[0] + move_vector[0], sprite_center[1] + move_vector[1]

# Shovel Sprite
class Shovel(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        # load the PNG
        self.image = pygame.image.load(os.path.join('images', 'shovel.png'))
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, 700)
        self.rect.y = random.randint(0, 450)

def read_high_scores():
    if not os.path.isfile('high_scores'):
        f = open('high_scores', 'w')
        for i in range(0, 5):
            f.write('0\n')
        f.close()

    f = open('high_scores', 'r')
    scores = []
    for s in f.readlines():
        scores.append(s)
    f.close()
    return scores


def new_high_score():
    global score
    if not os.path.isfile('high_scores'):
        print 'creating file'
        f = open('high_scores', 'w')
        for i in range(0, 5):
            f.write('0\n')
        f.close()

    f = open('high_scores', 'r')
    high_scores = []
    for high_score in f.readlines():
        high_scores.append(int(high_score.rstrip('\n')))
    f.close()
    f = open('high_scores', 'w')
    for i in range(0, len(high_scores)):
        if score > high_scores[i]:
            high_scores.insert(i, score)
            break
    # keep the top 5 high scores only
    if len(high_scores) > 5:
        del high_scores[-1]

    # write the scores back to disk
    for score in high_scores:
        f.write(str(score) + '\n')
    f.close()


# Game Over loop
def game_over():
    global score
    bullet_list.empty()
    enemy_list.empty()
    shovel_list.empty()
    screen = pygame.display.get_surface()
    screen_rect = screen.get_rect()
    screen_width = screen.get_width()
    screen_height = screen.get_height()
    global enemy_count
    enemy_count = 0
    global bullet_size
    bullet_size = 0
    # set up font
    basic_font = pygame.font.SysFont(None, 48)
    # initialize a clock
    clock = pygame.time.Clock()
    #Death Loop
    while 1:
        # handle input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                new_high_score()
                score = 0
                sys.exit()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    screen.fill((0, 0, 0))
                    pygame.display.flip()
                    new_high_score()
                    score = 0
                    main()

        death = pygame.image.load(os.path.join('images', 'death_screen.png'))
        screen.blit(death, [0, 0])

        # Keep showing score text
        text = basic_font.render('Score: %d' % score, True, (255, 255, 255))
        text_rect = text.get_rect()
        text_rect.x = screen_rect.x
        text_rect.y = screen_rect.y
        screen.blit(text, text_rect)
        # update the screen
        pygame.display.flip()


def display_high_scores():

    # get the pygame screen and create some local vars
    screen = pygame.display.get_surface()
    screen_width = screen.get_width()
    screen_height = screen.get_height()
    # set up font
    basic_font = pygame.font.SysFont(None, 32)
    # initialize a clock
    scores = read_high_scores()
    menu = cMenu(50, 50, 20, 5, 'vertical', 100, screen,
                 [('Back', 1, None)])
    # center the menu
    menu.set_center(False, False)
    menu.set_alignment('bottom', 'center')
    offset = -50
    rank = 1
    for score in scores:
        text = basic_font.render(str(rank) + ': ' + score.rstrip('\n'), True, (255, 255, 255))
        text_rect = text.get_rect()
        text_rect.x = screen_width / 2 + 80
        text_rect.y = screen_height / 2 + offset
        offset += 20
        rank += 1
        # draw the text onto the surface
        screen.blit(text, text_rect)
    pygame.display.flip()


def event_loop():
    # get the pygame screen and create some local vars
    screen = pygame.display.get_surface()
    screen_rect = screen.get_rect()
    screen_width = screen.get_width()
    screen_height = screen.get_height()
    # set up font
    basic_font = pygame.font.SysFont(None, 48)
    # initialize a clock
    clock = pygame.time.Clock()

    # initialize score
    global score
    score = 0
    global enemy_count

    # Global bullet_size
    global bullet_size

    # initialize the player and the enemy
    player = Player()
    enemy = Enemy()
    enemy_count+=1

    #initialize weapon amounts
    global shovel
    shovel = 0

    # create a sprite group for the player and enemy
    # so we can draw to the screen
    sprite_list = pygame.sprite.Group()
    sprite_list.add(player)

    # create a sprite group for enemies only to detect collisions
    enemy_list.add(enemy)

    # main game loop
    while 1:
        # handle input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            #Mouse input controls
            elif event.type == pygame.MOUSEMOTION:
                # rotate the player to face the mouse
                player.rotate(event.pos)
                #player.fire()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    player.left()
                elif event.key == pygame.K_d:
                    player.right()
                elif event.key == pygame.K_w:
                    player.up()
                elif event.key == pygame.K_s:
                    player.down()

            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_a:
                    player.right()
                elif event.key == pygame.K_d:
                    player.left()
                elif event.key == pygame.K_w:
                    player.down()
                elif event.key == pygame.K_s:
                    player.up()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                player.fire(event.pos)

        # call the move function for the player
        player.move()

        # check player bounds
        if player.rect.left < 0:
            player.rect.left = 0
        if player.rect.right > screen_width:
            player.rect.right = screen_width
        if player.rect.top < 0:
            player.rect.top = 0
        if player.rect.bottom > screen_height:
            player.rect.bottom = screen_height

        # Places a new enemy off screen
        def newEnemyPlacement():
            side = random.randint(0,5)
            placement = [0,0]
            if(side == 1):
                placement[0] = random.randint(0, 750)
                placement[1] = 0
            elif(side == 2):
                placement[0] = 0
                placement[1] = random.randint(0, 500)
            elif(side == 3):
                placement[0] = random.randint(0, 750)
                placement[1] = 500
            elif(side == 4):
                placement[0] = 750
                placement[1] = random.randint(0, 500)
            return placement
        # Add new enemy randomly until max number of enemies
        if(random.randint(0,10) == 5):
            if(enemy_count < score/10 + 3):
                newEnemy = Enemy()
                placement = newEnemyPlacement()
                newEnemy.rect.x = placement[0]
                newEnemy.rect.y = placement[1]
                enemy_list.add(newEnemy)
                enemy_count += 1

        # Get direction for enemy movement and move enemy
        def Tracking(enemy, player):
            speed = [0,0]
            speed[0] = -(enemy.rect.centerx - player.rect.centerx)
            speed[1] = -(enemy.rect.centery - player.rect.centery)
            dist = math.hypot(speed[0], speed[1])
            no_move_x = 0
            no_move_y = 0
            #Enemy collision detector
            for e in enemy_list :
                if(e != enemy) :
                    collision = check_collision(enemy, e)
                    if collision == 1 :
                        if(abs((enemy.rect.centerx - player.rect.centerx)) >= abs((e.rect.centerx - player.rect.centerx)) ):
                            no_move_x = 1
                    elif collision == 2 :
                        if(abs((enemy.rect.centery - player.rect.centery)) >= abs((e.rect.centery - player.rect.centery)) ):
                            no_move_y = 1
                    elif collision == 3 :
                        if(abs((enemy.rect.centerx - player.rect.centerx)) >= abs((e.rect.centerx - player.rect.centerx)) ):
                            no_move_y = 1
                        if(abs((enemy.rect.centery - player.rect.centery)) >= abs((e.rect.centery - player.rect.centery)) ):
                            no_move_x = 1
            if no_move_x == 0 :
                enemy.rect.x += (speed[0]*2/dist) * (1 + .25 * score / 25)
            if no_move_y == 0 :
                enemy.rect.y += (speed[1]*2/dist) * (1 + .25 * score / 25)

        #Checks for enemy collisions between single enemies
        #Returns
        # 0 - No collision
        # 1 - collision in X
        # 2 - collision in Y
        # 3 - collision in both X and Y
        def check_collision(enemy, e):
            x_dif = abs(enemy.rect.centerx - e.rect.centerx)
            y_dif = abs(enemy.rect.centery - e.rect.centery)
            length = abs(enemy.rect.x - enemy.rect.centerx)
            width = abs(enemy.rect.y - enemy.rect.centery)
            if(x_dif < length) :
                if y_dif < width :
                    return 3
                return 1
            if(y_dif < width) :
                return 2
            return 0


        # Call function to move each enemy
        for enemy in enemy_list:
            # Track player
            Tracking(enemy, player)

        # Bullet bounce check
        for bullet in bullet_list:
            if bullet.rect.left < 0 or bullet.rect.right > screen_width :
                bullet.speed[0] = -bullet.speed[0]
            if bullet.rect.top < 0 or bullet.rect.bottom > screen_height :
                bullet.speed[1] = -bullet.speed[1]
            #Move Bullet
            bullet.rect.x += bullet.speed[0] * (1 + .25 * score / 25)
            bullet.rect.y += bullet.speed[1] * (1 + .25 * score / 25)


        # detect all collisions
        if pygame.sprite.groupcollide(enemy_list, bullet_list, True, True, None):
            score += 1
            enemy_count -= 1
            bullet_size -= 1

        if pygame.sprite.spritecollide(player, bullet_list, True):
            bullet_size -= 1
            player.lose_health_bullet()

        if pygame.sprite.spritecollide(player, enemy_list, True):
            enemy_count -= 1
            player.lose_health_enemy()

        if pygame.sprite.spritecollide(player, shovel_list, False):
            player.shovel()

        # Draw super awesome shovel
        def draw_shovel():
            shovel = Shovel()
            shovel_list.add(shovel)

        # Super awesome shovel spawning
        if (score%25 == 0) and (score > 0) and (shovel == 0):
            shovel = 1
            draw_shovel()

        #draw_background define
        def draw_background(background, x, y):
            screen.blit(background, [x, y])

        # draw background
        background = pygame.image.load(os.path.join('images', 'ground.png'))
        draw_background(background, 0, 0)

        # set up the score text
        text = basic_font.render('Score: %d' % score, True, (255, 255, 255))
        text_rect = text.get_rect()
        text_rect.x = screen_rect.x
        text_rect.y = screen_rect.y

        life = basic_font.render('Health: %d' % player.health, True, (255, 255, 255))
        life_rect = life.get_rect()
        life_rect.x =  screen_rect.x
        life_rect.y = screen_rect.y + screen_height - 30

        # draw the text onto the surface
        screen.blit(text, text_rect)
        screen.blit(life, life_rect)

        # draw the player and enemy sprites to the screen
        sprite_list.draw(screen)
        bullet_list.draw(screen)
        enemy_list.draw(screen)
        shovel_list.draw(screen)

        # update the screen
        pygame.display.flip()

        # limit to 45 FPS
        clock.tick(45)

def tutorial():

    global screen

    ground = pygame.image.load(os.path.join('images', 'ground.png'))
    screen.blit(ground, [0, 0])

    #Movement controls
    while(True) :
        screen.blit(ground, [0, 0])
        text = basic_font.render('Welcome to the tutorial', True, (255, 255, 255))
        text_rect = text.get_rect()
        text_rect.x = screen_rect.centerx
        text_rect.y = screen_rect.centery

        text2 = basic_font.render('Press any button to continue', True, (255, 255, 255))
        text2_rect = text2.get_rect()
        text2_rect.x = screen_rect.centerx
        text2_rect.y = screen_rect.centery + 30

        # draw the text onto the surface
        screen.blit(text, text_rect)
        screen.blit(text2, text2_rect)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            #Mouse input controls
            elif event.type == pygame.KEYDOWN:
                break

def main():
    # initialize pygame
    pygame.init()

    # create the window
    size = width, height = 718, 480
    screen = pygame.display.set_mode(size)

    # set the window title
    pygame.display.set_caption("Rico-ja")

    # create the menu
    menu = cMenu(50, 50, 20, 5, 'vertical', 100, screen,
                 [('Start Game', 1, None),
                  #('Tutorial', 2, None),
                  ('High Score', 2, None),
                  ('Exit', 3, None)])
    # center the menu
    menu.set_center(True, True)
    menu.set_alignment('center', 'center')

    # state variables for the finite state machine menu
    state = 0
    prev_state = 1

    # ignore mouse and only update certain rects for efficiency
    #pygame.event.set_blocked(pygame.MOUSEMOTION)
    rect_list = []

    #pygame.display.update(rect_list)

    high_scores_displayed = False
    while 1:
        pygame.display.set_caption("Rico-ja")
        # check if the state has changed, if it has, then post a user event to
        # the queue to force the menu to be shown at least once
        if prev_state != state:
            pygame.event.post(pygame.event.Event(EVENT_CHANGE_STATE, key=0))
            prev_state = state

        # get the next event
        e = pygame.event.wait()

        # update the menu
        if e.type == pygame.KEYDOWN or e.type == EVENT_CHANGE_STATE or e.type == pygame.QUIT:

            # quit if the user closes the window
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if state == 0:
                # "default" state
                rect_list, state = menu.update(e, state)
            elif state == 1:
                # start the game
                event_loop()
            #elif state == 2:
            #    tutorial()
            #    state = 0
            elif state == 2:
                if not high_scores_displayed:
                    display_high_scores()
                    high_scores_displayed = True
                state = 0
            else:
                # exit the game and program
                pygame.quit()
                sys.exit()

            # update the screen
            pygame.display.update(rect_list)



if __name__ == '__main__':
    GameEngine()
