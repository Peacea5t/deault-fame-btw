#Создай собственный Шутер!
from pygame import *
from random import randint
import time as time_module

init()
mixer.init()
font.init()

mixer.music.load("space.ogg")
mixer.music.play(-1)
fire_sound = mixer.Sound("fire.ogg")

win_width = 700
win_height = 500
window = display.set_mode((win_width, win_height))
display.set_caption("Shooter")

background = transform.scale(
    image.load("galaxy.jpg").convert(),
    (win_width, win_height)
)

FPS = 240
clock = time.Clock()

class GameSprite(sprite.Sprite):
    def __init__(self, player_image, player_x, player_y, size_x, size_y, player_speed):
        super().__init__()
        self.image = transform.scale(image.load(player_image).convert_alpha(), (size_x, size_y))
        self.speed = player_speed
        self.rect = self.image.get_rect()
        self.rect.x = player_x
        self.rect.y = player_y

    def reset(self):
        window.blit(self.image, (self.rect.x, self.rect.y))

class Player(GameSprite):
    def update(self):
        keys = key.get_pressed()
        if keys[K_a] and self.rect.x > 5:
            self.rect.x -= self.speed
        if keys[K_d] and self.rect.x < win_width - 70:
            self.rect.x += self.speed

    def fire(self):
        bullet = Bullet("bullet.png", self.rect.centerx - 7, self.rect.top, 15, 20, 10)
        bullets.add(bullet)

class Enemy(GameSprite):
    def __init__(self, player_image, player_x, player_y, size_x, size_y, player_speed):
        super().__init__(player_image, player_x, player_y, size_x, size_y, player_speed)
        self.start_y_min = -250
        self.start_y_max = -50

    def update(self):
        self.rect.y += self.speed
        if self.rect.y > win_height:
            self.rect.x = randint(40, 600)
            self.rect.y = randint(self.start_y_min, self.start_y_max)
            global missed
            missed += 1

class Asteroid(GameSprite):
    def update(self):
        self.rect.y += self.speed
        if self.rect.y > win_height:
            self.rect.x = randint(40, 600)
            self.rect.y = randint(-300, -100)

class Bullet(GameSprite):
    def update(self):
        self.rect.y -= self.speed
        if self.rect.y < 0:
            self.kill()

ship = Player("rocket.png", win_width / 2 - 35, win_height - 100, 65, 65, 5)

ufos = sprite.Group()
for i in range(7):
    ufo = Enemy("ufo.png", randint(40, 600), randint(-452, -50), 120, 75, 1)
    ufo.start_y_min = -452
    ufo.start_y_max = -50
    ufos.add(ufo)

asteroids = sprite.Group()
for i in range(2):
    asteroid = Asteroid("asteroid.png", randint(40, 600), randint(-467, -10), 150, 150, 1)
    asteroids.add(asteroid)

bullets = sprite.Group()

game_font = font.Font(None, 36)
reload_font = font.Font(None, 60)

score = 0
missed = 0

max_ammo = 20 
ammo = max_ammo
is_reloading = False
reload_start_time = 0

game = True
finish = False

while game:
    for e in event.get():
        if e.type == QUIT:
            game = False
        if e.type == MOUSEBUTTONDOWN:
            if e.button == 1:
                if ammo > 0 and not is_reloading:
                    ammo -= 1
                    ship.fire()
                    fire_sound.play()
                    if ammo == 0:
                        is_reloading = True
                        reload_start_time = time_module.time()

    if not finish:
        window.blit(background, (0, 0))

        if is_reloading:
            current_time = time_module.time()
            if current_time - reload_start_time >= 3:
                ammo = max_ammo
                is_reloading = False
            else:
                reload_text = reload_font.render("ПЕРЕЗАРЯДКА...", True, (255, 0, 0))
                window.blit(reload_text, (win_width / 2 - 160, win_height / 2 - 30))

        ship.update()
        ufos.update()
        asteroids.update()
        bullets.update()

        ship.reset()
        ufos.draw(window)
        asteroids.draw(window)
        bullets.draw(window)

        collides = sprite.groupcollide(ufos, bullets, True, True)
        for c in collides:
            score += 1
            ufo = Enemy("ufo.png", randint(40, 600), randint(-400, -50), 90, 55, 1)
            ufo.start_y_min = -400
            ufo.start_y_max = -50
            ufos.add(ufo)

        if sprite.spritecollide(ship, ufos, False) or sprite.spritecollide(ship, asteroids, False) or missed >= 10:
            finish = True
            lose_text = reload_font.render("YOU LOOOOSE", True, (255, 0, 0))
            window.blit(lose_text, (180, 120))

        if score >= 20:
            finish = True
            win_text = reload_font.render("I VERIFED TIDAL WAVE", True, (255, 215, 0))
            window.blit(win_text, (190, 120))

        score_text = game_font.render("Cбито дронов: " + str(score), True, (255, 255, 255))
        missed_text = game_font.render("Пропущено дронов : " + str(missed), True, (255, 255, 255))
        
        if is_reloading:
            ammo_text = game_font.render("Патроны: 0", True, (255, 0, 0))
        else:
            ammo_text = game_font.render("Патроны: " + str(ammo), True, (255, 255, 255))

        window.blit(score_text, (10, 20))
        window.blit(missed_text, (10, 50))
        window.blit(ammo_text, (10, 80))

    display.update()
    clock.tick(FPS)

quit()