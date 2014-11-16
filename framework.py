import sys
import os
import math
import vector
import pygame
from menu import *
# Global Bullet list
bullet_list = pygame.sprite.Group()
# Global enemy list
enemy_list = pygame.sprite.Group()


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

    def fire(self, mouse_location):
        bullet = Bullet()
        start_x, start_y = Bullet.calculate_start(self, mouse_location)

        bullet.rect.centerx = start_x
        bullet.rect.centery = start_y
        bullet.speed[0] = math.cos(math.radians(self.angle))*bullet.base_speed
        print math.radians(self.angle)
        bullet.speed[1] = -math.sin(math.radians(self.angle))*bullet.base_speed
        print bullet.speed
        bullet_list.add(bullet)

    def death(self, score):
        game_over(score)


class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        # load the PNG
        self.image = pygame.image.load(os.path.join('images', 'ball.png'))
        self.rect = self.image.get_rect()
        self.rect.topleft = 0, 0


# Bullet sprite
class Bullet(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface([5, 5])
        self.image.fill(WHITE)
        self.speed = [0,0]
        self.base_speed = 10
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

# Game Over loop
def game_over(score):
    bullet_list.empty()
    screen = pygame.display.get_surface()
    screen_rect = screen.get_rect()
    screen_width = screen.get_width()
    screen_height = screen.get_height()
    # set up font
    basic_font = pygame.font.SysFont(None, 48)
    # initialize a clock
    clock = pygame.time.Clock()

    #Death Loop
    while 1:
        # handle input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    screen.fill((0, 0, 0))
                    pygame.display.flip()
                    main()

        death = pygame.image.load(os.path.join('images', 'death_screen.png'))
        screen.blit(death, [0, 0])

        # set up the score text
        text = basic_font.render('Score: %d' % score, True, (255, 255, 255))
        text_rect = text.get_rect()
        text_rect.x = screen_rect.x
        text_rect.y = screen_rect.y
        screen.blit(text, text_rect)
        # update the screen
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
        for e in enemy_list:
            if pygame.sprite.spritecollide(e, bullet_list, False):
                score += 1
                enemy_list.remove(e)


        if pygame.sprite.spritecollide(player, bullet_list, False):
            player.death(score)

        if pygame.sprite.spritecollide(player, enemy_list, False):
            player.death(score)

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
        enemy_list.draw(screen)

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
        if e.type == pygame.KEYDOWN or e.type == EVENT_CHANGE_STATE:
            if state == 0:
                # "default" state
                rect_list, state = menu.update(e, state)
            elif state == 1:
                # start the game
                event_loop()
            elif state == 2:
                # just to demonstrate how to make other options
                pygame.display.set_caption("High Scores")
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
    GameEngine()