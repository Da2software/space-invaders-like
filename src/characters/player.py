import pygame
import pygame.mixer
from src.globals import GameVariables
from src.utils import Position2D

GLOBALS = GameVariables()


class Player(pygame.sprite.Sprite):
    """
    Main Player render class, this also handles the player movement
    """

    def __init__(self, col, x, y):
        pygame.sprite.Sprite.__init__(self)
        # player attributes
        self.tag = "player"
        self.movex_speed = 400
        self.movey_speed = 400
        # self.life = GLOBALS.life
        self.is_dead = False
        # player rendering
        self.image = pygame.image.load(
            GLOBALS.sprite_dir + "Player.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (48, 48))
        # self.image.fill(col)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.move_f = Position2D()
        self.invulnerable = False
        self.blink_alpha_timer = 100
        self.blink_alpha = 200
        self.blink_state = False
        self.invulnerability_timeout = 0  # 2 seconds, but starts with zero

    def blink(self):
        """ used to generate the blink state when player got damage """
        # start if invulnerability is active
        if self.invulnerable and self.blink_alpha_timer <= 0:
            # alpha change between two values 50|180 each timer period
            self.blink_alpha = 180 if self.blink_state else 50
            # set the new alpha
            self.image.set_alpha(self.blink_alpha)
            # this value helps switch the alpha value
            self.blink_state = not self.blink_state  # invert the current value
            # set again the timer
            self.blink_alpha_timer = 100
        if self.invulnerable:  # timer works if is invulnerable
            self.blink_alpha_timer -= GLOBALS.ms_fps
        elif self.image.get_alpha() != 255:
            # in case the blink ends then restore the alpha
            self.image.set_alpha(255)

    def update(self) -> None:
        """
        Process the key events to move the playr
        :return: None
        """
        keys = pygame.key.get_pressed()
        # self.move_f.clear()
        self.move_f.y = self.get_axisY(
            keys) * (self.movey_speed * GLOBALS.delta_time)
        self.move_f.x = self.get_axisX(
            keys) * (self.movex_speed * GLOBALS.delta_time)

        self.rect.move_ip(self.move_f.x, self.move_f.y)

        self.invulnerability_timeout -= GLOBALS.ms_fps if (
                self.invulnerability_timeout > 0) else 0
        if self.invulnerability_timeout <= 0:
            self.invulnerable = False
        self.blink()

    def active_invulnerability(self):
        self.invulnerable = True
        self.invulnerability_timeout = 2000  # 2 seconds

    def get_axisY(self, keys) -> int:
        """
        used to return the axis value in case this is active -1 = UP, 1 = DOWN
        and 0 = no direction detected
        :param keys: pygame keys object
        :return: int value with Y axis value
        """
        if ((keys[pygame.K_s] or keys[pygame.K_DOWN])
                and self.rect.bottom < GLOBALS.screen.get_height()):
            return 1
        elif ((keys[pygame.K_w] or keys[pygame.K_UP])
              and self.rect.top > 0):
            return -1
        return 0

    def get_axisX(self, keys) -> int:
        """
        used to return the axis value in case this is
        active -1 = LEFT, 1 = RIGHT and 0 = no direction detected
        :param keys: pygame keys object
        :return: int value with X axis value
        """
        if ((keys[pygame.K_d] or keys[pygame.K_RIGHT])
                and self.rect.right < GLOBALS.screen.get_width()):
            return 1
        elif ((keys[pygame.K_a] or keys[pygame.K_LEFT])
              and self.rect.left > 0):
            return -1
        return 0

    def get_pos(self) -> Position2D:
        """
        :return: {Position2D} object with the current player position
        """
        pos = Position2D()
        pos.x = self.rect.x
        pos.y = self.rect.y
        return pos

    def take_damage(self, damage: int):
        GLOBALS.life -= damage
        self.is_dead = GLOBALS.life <= 0
        # sound effect for damage
        GLOBALS.sound_controller.play("dmg")


class Bullet(pygame.sprite.Sprite):
    def __init__(self, player: Player):
        pygame.sprite.Sprite.__init__(self)
        # Bullet attributes
        self.tag = "bullet"
        self.damage = 10
        self.speed = 8
        self.is_dead = False  # in case bullet hits an Enemy
        # Rendering Variables
        self.image = pygame.Surface((6, 10))
        self.image.fill((255, 255, 0))
        self.rect = self.image.get_rect()
        player_pos = player.get_pos()
        self.rect.center = (
            player_pos.x + (player.rect.width / 2), player_pos.y)

        # if bullet is created we need a sound effect for shoot
        GLOBALS.sound_controller.play("s1")  # shoot1

    def update(self) -> None:
        # check if bullet got hit
        if self.is_dead:
            self.kill()
            return
            # move up the bullet to hit enemies
        self.rect.move_ip(0, -self.speed)
        if self.rect.bottom < 0:
            self.kill()

    def hit(self):
        self.is_dead = True


class PlayerController:
    def __init__(self):
        # create the player instance
        self.player = Player("blue", GLOBALS.screen.get_width() / 2,
                             GLOBALS.screen.get_height() - 50)
        # create the Sprites Groups related with the player
        self.playerGroup = pygame.sprite.Group()
        self.playerGroup.add(self.player)  # add player to the group
        # set 1 second shoot rate
        self.shoot_rate = 0.6
        self.shoot_timer = 0.6

    def can_shot(self):
        """ Can not shoot more than one bullet, we need to wait until
        the next bullet is destroyed
        :return True or False if we can shoot or not """
        for item in self.playerGroup.sprites():
            player_or_bullet: Player | Bullet = item
            if player_or_bullet.tag == "bullet":
                return False
        return True

    def render(self):
        keys = pygame.key.get_pressed()
        # detect player shoot
        self.shoot_timer -= GLOBALS.delta_time
        if keys[pygame.K_SPACE] and self.shoot_timer <= 0 and self.can_shot():
            bullet = Bullet(self.player)
            self.playerGroup.add(bullet)
            self.shoot_timer = self.shoot_rate
        self.playerGroup.update()
        self.playerGroup.draw(GLOBALS.screen)
