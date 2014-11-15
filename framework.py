import sys
import os
import math
import vector
from menu import *
# Global Bullet list
bullet_list = pygame.sprite.Group()

class Player(pygame.sprite.Sprite):
    # constructor for this class
    def __init__(self):
        # call the parent class (Sprite) constructor
        pygame.sprite.Sprite.__init__(self)
        #load player pistol PNG
        self.image = pygame.image.load(os.path.join('images', 'player_pistol.png'))
        self.original_image = self.image.copy()
        self.rect = self.image.get_rect()
        self.speed = [0, 0]

        #starts facing east
        self.angle = 0
        self.face_vector = [1, 0]

    def left(self):
        self.speed[0] -= 8

    def right(self):
        self.speed[0] += 8

    def up(self):
        self.speed[1] -= 8

    def down(self):
        self.speed[1] += 8

    def move(self):
        # move the rect by the displacement ("speed")
        self.rect = self.rect.move(self.speed)

    def rotate(self, mouse_location):
        # get the mouse location
        x, y = mouse_location
        # get the vector difference of the players location and the mouse
        move_vector = [x - self.rect.centerx, y - self.rect.centery]
        self.angle = math.degrees(math.atan2(*move_vector)) - 90
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)

    def fire(self):
        bullet = Bullet()
        bullet.rect.x = self.rect.x
        bullet.rect.y = self.rect.y
        bullet.speed[0] = math.cos(self.angle)*bullet.base_speed
        bullet.speed[1] = math.sin(self.angle)*bullet.base_speed
        bullet_list.add(bullet)


class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        # load the PNG
        self.image = pygame.image.load(os.path.join('images', 'ball.png'))
        self.rect = self.image.get_rect()
        self.rect.topleft = 0, 0


        #Bullet sprite
class Bullet(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface([5, 15])
        self.image.fill(WHITE)
        self.speed = [0,0]
        self.base_speed = 10


        self.rect = self.image.get_rect()

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
    # initialize the score counter
    score = 0
    # initialize the enemy speed
    enemy_speed = [6, 6]

    # initialize the player and the enemy
    player = Player()
    enemy = Enemy()

    # create a sprite group for the player and enemy
    # so we can draw to the screen
    sprite_list = pygame.sprite.Group()
    sprite_list.add(player)
    sprite_list.add(enemy)

    # create a sprite group for enemies only to detect collisions
    enemy_list = pygame.sprite.Group()
    enemy_list.add(enemy)

    # main game loop
    while 1:
        # handle input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            #Mouse input controls
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # rotate the player to face the mouse
                player.rotate(event.pos)
                player.fire()

                
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    player.left()
                elif event.key == pygame.K_RIGHT:
                    player.right()
                elif event.key == pygame.K_UP:
                    player.up()
                elif event.key == pygame.K_DOWN:
                    player.down()

            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    player.right()
                elif event.key == pygame.K_RIGHT:
                    player.left()
                elif event.key == pygame.K_UP:
                    player.down()
                elif event.key == pygame.K_DOWN:
                    player.up()

            #elif event.type == pygame.MOUSEBUTTONDOWN:
            #    player.fire()

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

        # reverse the movement direction if enemy goes out of bounds
        if enemy.rect.left < 0 or enemy.rect.right > screen_width:
            enemy_speed[0] = -enemy_speed[0]
        if enemy.rect.top < 0 or enemy.rect.bottom > screen_height:
            enemy_speed[1] = -enemy_speed[1]

        # another way to move rects
        enemy.rect.x += enemy_speed[0]
        enemy.rect.y += enemy_speed[1]

        for bullet in bullet_list:
            if(bullet.rect.left < 0 or bullet.rect.right > screen_width):
                bullet.speed[0] = -bullet.speed[0]
            if(bullet.rect.top < 0 or bullet.rect.bottom > screen_height):
                bullet.speed[1] = -bullet.speed[1]
            #Move Bullet
            bullet.rect.x += bullet.speed[0]
            bullet.rect.y += bullet.speed[1]

        # detect all collisions between the player and enemy
        # but don't remove enemy after collisions
        # increment score if there was a collision
        if pygame.sprite.spritecollide(player, enemy_list, False):
            score += 1

        #draw_background define
        def draw_background(background, x, y):
            screen.blit(background, [x, y])

        # draw background
        # screen.fill((0, 0, 0))
        background = pygame.image.load(os.path.join('images', 'ground.png'))
        draw_background(background, 0, 0)

        # set up the score text
        text = basic_font.render('Score: %d' % score, True, (255, 255, 255))
        text_rect = text.get_rect()
        text_rect.x = screen_rect.x
        text_rect.y = screen_rect.y

        # draw the text onto the surface
        screen.blit(text, text_rect)

        # draw the player and enemy sprites to the screen
        sprite_list.draw(screen)
        bullet_list.draw(screen)

        # update the screen
        pygame.display.flip()

        # limit to 45 FPS
        clock.tick(45)


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
                  ('Other Option', 2, None),
                  ('Exit', 3, None)])
    # center the menu
    menu.set_center(True, True)
    menu.set_alignment('center', 'center')

    # state variables for the finite state machine menu
    state = 0
    prev_state = 1

    # ignore mouse and only update certain rects for efficiency
    pygame.event.set_blocked(pygame.MOUSEMOTION)
    rect_list = []

    while 1:
        # check if the state has changed, if it has, then post a user event to
        # the queue to force the menu to be shown at least once
        if prev_state != state:
            pygame.event.post(pygame.event.Event(EVENT_CHANGE_STATE, key=0))
            prev_state = state

        # get the next event
        e = pygame.event.wait()

        # update the menu
        if e.type == pygame.KEYDOWN or e.type == EVENT_CHANGE_STATE:
            if state == 0:
                # "default" state
                rect_list, state = menu.update(e, state)
            elif state == 1:
                # start the game
                event_loop()
            elif state == 2:
                # just to demonstrate how to make other options
                pygame.display.set_caption("y u touch this")
                state = 0
            else:
                # exit the game and program
                pygame.quit()
                sys.exit()

            # quit if the user closes the window
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # update the screen
            pygame.display.update(rect_list)


if __name__ == '__main__':
    main()