import pygame
import random
import time

pygame.init()
pygame.mixer.init()

 
pygame.mixer.music.load("ref/music.mp3")
pygame.mixer.music.play(-1)
pygame.mixer.music.set_volume(0.3)

shoot_sound = pygame.mixer.Sound("ref/shoot.mp3")
win_sound = pygame.mixer.Sound("ref/win.mp3")
lose_sound = pygame.mixer.Sound("ref/lose.mp3")

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Магічний шутер(⁠´⁠∩⁠｡⁠•⁠ ⁠ᵕ⁠ ⁠•⁠｡⁠∩⁠`⁠)")

background = pygame.image.load("ref/background.jpg")
background = pygame.transform.scale(background, (WIDTH, HEIGHT))
new_background = pygame.image.load("ref/background_hard.png")
new_background = pygame.transform.scale(new_background, (WIDTH, HEIGHT))


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image_normal = pygame.image.load("ref/player.png")
        self.image_happy = pygame.image.load("ref/player_happy.png")
        self.image_sad = pygame.image.load("ref/player_sad.png")
        self.image = pygame.transform.scale(self.image_normal, (75, 125))
        self.rect = self.image.get_rect(center=(50, HEIGHT // 2))
        self.speed = 7

    def update(self, keys):
        if keys[pygame.K_UP] and self.rect.top > 0:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN] and self.rect.bottom < HEIGHT:
            self.rect.y += self.speed
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH // 2:
            self.rect.x += self.speed

    def set_happy(self):
        self.image = pygame.transform.scale(self.image_happy, (150, 200))

    def set_sad(self):
        self.image = pygame.transform.scale(self.image_sad, (150, 200))


class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        enemy_image_path = random.choice(["ref/enemy.png", "ref/enemy_1.png"])
        self.image = pygame.image.load(enemy_image_path)
        self.image = pygame.transform.scale(self.image, (50, 50))
        self.rect = self.image.get_rect(center=(WIDTH + 40, random.randint(40, HEIGHT - 40)))
        self.speed = -3

    def update(self):
        self.rect.x += self.speed
        if self.rect.right < 0:
            self.kill()
            return True
        return False


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load("ref/bullet.png")
        self.image = pygame.transform.scale(self.image, (40, 20))
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 7

    def update(self):
        self.rect.x += self.speed
        if self.rect.left > WIDTH:
            self.kill()


def fade_out_music():
    pygame.mixer.music.fadeout(1000)


def main_menu():
    font = pygame.font.Font(None, 50)
    text = font.render("Натисніть пробіл для початку гри", True, (255, 255, 255))
    text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.fill((0, 0, 0))
    screen.blit(text, text_rect)
    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                waiting = False
    return True


def game_over(win, player):
    font = pygame.font.Font(None, 50)
    screen.fill((0, 0, 0))

    fade_out_music()

    if win:
        text = font.render("Ви виграли!", True, (255, 215, 0))
        player.set_happy()
        win_sound.play()
    else:
        text = font.render("Програш!", True, (255, 0, 0))
        player.set_sad()
        lose_sound.play()

    screen.blit(text, (WIDTH // 2 - 150, HEIGHT // 2))
    screen.blit(player.image, player.rect)
    pygame.display.flip()
    pygame.time.delay(3000)


def show_hardmode_text():
    font = pygame.font.Font(None, 100)
    start_time = time.time()
    show = True
    while time.time() - start_time < 3:
        screen.fill((0, 0, 0))
        text = font.render("HARDMODE!", True, (255, 0, 0) if show else (0, 0, 0))
        text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(text, text_rect)
        pygame.display.flip()
        pygame.time.delay(300)
        show = not show


def game():
    player = Player()
    enemies = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    all_sprites = pygame.sprite.Group()
    all_sprites.add(player)

    for _ in range(5):
        enemy = Enemy()
        enemies.add(enemy)
        all_sprites.add(enemy)

    clock = pygame.time.Clock()
    running = True

    killed_enemies = 0
    missed_enemies = 0
    hardmode = False
    hardmode_triggered = False
    font = pygame.font.Font(None, 36)

    global background

    while running:
        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                bullet = Bullet(player.rect.centerx, player.rect.centery)
                bullets.add(bullet)
                all_sprites.add(bullet)
                shoot_sound.play()

        player.update(keys)
        bullets.update()

        for enemy in enemies.sprites():
            if enemy.update():
                missed_enemies += 1

                # Создаём нового врага
                new_enemy = Enemy()
                enemies.add(new_enemy)
                all_sprites.add(new_enemy)

        for bullet in bullets:
            hits = pygame.sprite.spritecollide(bullet, enemies, True)
            if hits:
                bullet.kill()
                killed_enemies += len(hits)
                for _ in hits:
                    new_enemy = Enemy()
                    enemies.add(new_enemy)
                    all_sprites.add(new_enemy)

        # Активация hardmode
        if not hardmode_triggered and killed_enemies >= 45:
            hardmode = True
            hardmode_triggered = True
            background = new_background

            show_hardmode_text()
            killed_enemies = 0
            missed_enemies = 0

            for _ in range(5):
                new_enemy = Enemy()
                enemies.add(new_enemy)
                all_sprites.add(new_enemy)

        if hardmode and killed_enemies >= 80:
            game_over(True, player)
            running = False

        if missed_enemies >= (20 if hardmode else 15):
            game_over(False, player)
            running = False

        screen.blit(background, (0, 0))
        all_sprites.draw(screen)

        text_killed = font.render(f"Вбито: {killed_enemies}", True, (255, 255, 255))
        text_missed = font.render(f"Пропущено: {missed_enemies}", True, (255, 0, 0))

        screen.blit(text_killed, (10, 10))
        screen.blit(text_missed, (10, 40))

        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    if main_menu():
        game()
    pygame.quit()
