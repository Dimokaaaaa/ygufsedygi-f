import pygame
import random
import math

# Инициализация Pygame
pygame.init()

# Размеры экрана
screen_width, screen_height = 1200, 800
screen = pygame.display.set_mode((screen_width, screen_height))

# Размер чанка и размеры мира
chunk_size = 800
world_width, world_height = 4, 4  # 4 на 4 чанка

# Загрузка фона и настройка цветов
bg = pygame.image.load("images/bg.jpg")
bg = pygame.transform.scale(bg, (1200, 800))
WHITE = (255, 255, 255)
LIGHT_GREEN = (0, 255, 0)  # Цвет чанков (светло-зеленый)
BLACK = (0, 0, 0)  # Цвет границы чанков
BLUE = (0, 0, 255)  # Цвет хитбокса

# Генерация мира: создаем сетку 4x4 с чанками
def generate_world():
    return [[LIGHT_GREEN for _ in range(world_height)] for _ in range(world_width)]

# Игрок
class Player:
    def __init__(self, image_path):
        self.image = pygame.image.load(image_path)
        self.image = pygame.transform.scale(self.image, (90, 90))
        self.position = [1.5, 1.5]
        self.velocity = [0, 0]
        self.angle = 0
        self.speed = 15
        self.drift_factor = 0.9

    def move(self, keys):
        if keys[pygame.K_w]:
            self.velocity[0] += self.speed * math.cos(math.radians(self.angle))
            self.velocity[1] += self.speed * math.sin(math.radians(self.angle))
        if keys[pygame.K_s]:
            self.velocity[0] -= self.speed * math.cos(math.radians(self.angle))
            self.velocity[1] -= self.speed * math.sin(math.radians(self.angle))
        if keys[pygame.K_a]:
            self.angle -= 3
        if keys[pygame.K_d]:
            self.angle += 3

        # Применяем инерцию к движению
        self.velocity[0] *= self.drift_factor
        self.velocity[1] *= self.drift_factor

        # Ограничение максимальной скорости
        speed = math.sqrt(self.velocity[0] ** 2 + self.velocity[1] ** 2)
        if speed > 10:
            self.velocity[0] *= 10 / speed
            self.velocity[1] *= 10 / speed

        # Обновление позиции
        self.position[0] = max(0, min(self.position[0] + self.velocity[0] / chunk_size, world_width))
        self.position[1] = max(0, min(self.position[1] + self.velocity[1] / chunk_size, world_height))

    def draw(self, screen):
        rotated_image = pygame.transform.rotate(pygame.transform.rotate(self.image, -self.angle), 180)
        image_rect = rotated_image.get_rect(center=(screen_width // 2, screen_height // 2))
        screen.blit(rotated_image, image_rect.topleft)

    def get_rect(self):
        # Вычисляем хитбокс с учетом угла поворота
        rect = pygame.Rect(screen_width // 2 - 22.5, screen_height // 2 - 44.5, 45, 89)
        rotated_rect = rect.copy()
        rotated_rect.center = (screen_width // 2, screen_height // 2)
        return rotated_rect

# Функция отрисовки повернутого прямоугольника
def draw_rotated_rect(screen, color, rect, angle):
    surface = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(surface, color, surface.get_rect(), 2)
    rotated_surface = pygame.transform.rotate(surface, angle + 90)  # Поворот на 90 градусов
    rotated_rect = rotated_surface.get_rect(center=rect.center)
    screen.blit(rotated_surface, rotated_rect.topleft)

def get_bot_rect(bot_pos, camera_x, camera_y):
    bot_x, bot_y = bot_pos[0] * chunk_size - camera_x, bot_pos[1] * chunk_size - camera_y
    return pygame.Rect(bot_x - 22.5, bot_y - 44.5, 45, 89)
# Инициализация игры
def reset_game():
    global player, bots, elapsed_time, paused, game_over
    player = Player('images/car1.png')
    bots.clear()  # Очистка списка ботов
    elapsed_time = 0
    paused = False
    game_over = False

def update_and_draw_bots():
    global bots, game_over
    bots_to_remove = set()  # Используем множество для исключения дубликатов

    keys = pygame.key.get_pressed()

    # Обновление ботов
    for i, bot_pos in enumerate(bots):
        bot_x, bot_y = bot_pos
        angle = math.atan2(player.position[1] - bot_y, player.position[0] - bot_x)
        bot_velocity = [bot_speed * math.cos(angle), bot_speed * math.sin(angle)]

        # Применяем инерцию к ботам
        bot_velocity[0] *= bot_drift_factor
        bot_velocity[1] *= bot_drift_factor

        # Обновляем позицию ботов
        bot_pos[0] = max(0, min(bot_pos[0] + bot_velocity[0] / chunk_size, world_width))
        bot_pos[1] = max(0, min(bot_pos[1] + bot_velocity[1] / chunk_size, world_height))

        # Определяем хитбокс бота
        bot_rect = get_bot_rect(bot_pos, camera_x, camera_y)

        # Проверяем столкновение с игроком
        if player.get_rect().colliderect(bot_rect):
            game_over = True
            return

        # Проверка на столкновение с другими ботами
        for j, other_bot_pos in enumerate(bots):
            if i != j:  # Исключаем проверку с самим собой
                other_bot_rect = get_bot_rect(other_bot_pos, camera_x, camera_y)
                if bot_rect.colliderect(other_bot_rect):
                    bots_to_remove.add(i)
                    bots_to_remove.add(j)

        # Отрисовка хитбокса текущего бота (если нажата клавиша Alt)
        if keys[pygame.K_LALT] or keys[pygame.K_RALT]:
            # Отображаем хитбокс без сдвига
            draw_rotated_rect(screen, BLUE, bot_rect, -math.degrees(angle))

    # Удаляем ботов, которые столкнулись
    bots = [bot for idx, bot in enumerate(bots) if idx not in bots_to_remove]


    # Отрисовка ботов
    for bot_pos in bots:
        angle = math.atan2(player.position[1] - bot_pos[1], player.position[0] - bot_pos[0])
        bot_image_rotated = pygame.transform.rotate(bot_image, -math.degrees(angle))
        bot_image_rect = bot_image_rotated.get_rect(
            center=(bot_pos[0] * chunk_size - camera_x, bot_pos[1] * chunk_size - camera_y)
        )
        screen.blit(bot_image_rotated, bot_image_rect.topleft)


# Боты
bots = []
bot_image = pygame.image.load('images/police_car.png')
bot_image = pygame.transform.rotate(pygame.transform.scale(bot_image, (45, 89)), -90)
bot_speed = 6
bot_drift_factor = 0.9
bot_spawn_interval = 1500
last_bot_spawn_time = pygame.time.get_ticks()

# Генерация мира
world = generate_world()

# Шрифты и текст
label = pygame.font.SysFont('Arial', 50)
lose_label = label.render("YOU LOSE", False, (20, 20, 255))
inter_label = label.render("WELCOME", False, (20, 20, 255))
restart_label = label.render("PLAY AGAIN", False, (20, 20, 185))
start_label = label.render("START", False, (20, 20, 255))
main_menu_label = label.render("GO TO MAIN MENU", False, (20, 20, 255))
pause_label = label.render("PAUSED",False,(20, 20, 255))
restart_label_rect = restart_label.get_rect(topleft=(450, 425))
start_label_rect = start_label.get_rect(topleft=(525, 400))
main_menu_rect = main_menu_label.get_rect(topleft=(400, 500))

# Начальные состояния игры
gameplay = False
main_menu = True
paused = False
game_over = False
elapsed_time = 0
waiting_for_resume = False
running = True
# Основной игровой цикл
while running:
    mouse = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if not paused:  # Если игра не на паузе, ставим её на паузу
                        paused = True
                        pause_start_time = pygame.time.get_ticks()
                    elif paused and not waiting_for_resume:  # Если пауза активна и мы еще не ждем второго нажатия
                        waiting_for_resume = True
                        pause_start_time = pygame.time.get_ticks()  # Начало отсчета 2 секунд
                        elapsed_time = 0  # Сброс времени

    # Проверка состояния игры
    if main_menu:
        screen.blit(bg, (0, 0))
        screen.blit(inter_label, (500, 250))
        screen.blit(start_label, start_label_rect)
        if start_label_rect.collidepoint(mouse) and pygame.mouse.get_pressed()[0]:
            main_menu = False
            gameplay = True
            reset_game()
    elif gameplay and not paused:
        keys = pygame.key.get_pressed()

        # Движение игрока
        player.move(keys)

        # Очистка экрана
        screen.fill(WHITE)

        # Камера
        camera_x = int(player.position[0] * chunk_size - screen_width // 2)
        camera_y = int(player.position[1] * chunk_size - screen_height // 2)

        # Отображение чанков
        for i in range(world_width):
            for j in range(world_height):
                chunk_x = i * chunk_size - camera_x
                chunk_y = j * chunk_size - camera_y
                pygame.draw.rect(screen, LIGHT_GREEN, (chunk_x, chunk_y, chunk_size, chunk_size))
                pygame.draw.rect(screen, BLACK, (chunk_x, chunk_y, chunk_size, chunk_size), 2)

        # Хитбокс игрока
        player_rect = player.get_rect()
        player.draw(screen)

        update_and_draw_bots()

        # Проверка нажатия клавиши Alt
        if keys[pygame.K_LALT] or keys[pygame.K_RALT]:
            # Отрисовка хитбокса игрока
            draw_rotated_rect(screen, BLUE, player_rect, -player.angle)

        # Генерация ботов каждые 3 секунды
        current_time = pygame.time.get_ticks()
        if current_time - last_bot_spawn_time > bot_spawn_interval:
            bot_x = random.uniform(0, world_width)
            bot_y = random.uniform(0, world_height)
            bots.append([bot_x, bot_y])
            last_bot_spawn_time = current_time

    if gameplay and paused:
        if waiting_for_resume:
            # Показываем таймер, если на паузе и ждем второго нажатия
            time_left = 2 - (pygame.time.get_ticks() - pause_start_time) / 1000  # Таймер в секундах
            if time_left > 0:
                # Отображаем таймер
                timer_text = label.render(f"Resuming in {int(time_left)}s", True, (255, 0, 0))
                screen.blit(timer_text, (screen_width // 2 - timer_text.get_width() // 2, screen_height // 2))
                pygame.display.flip()
            else:
                # Снимаем паузу, если время прошло
                paused = False
                waiting_for_resume = False  # Заканчиваем ожидание
                elapsed_time = 0  # Обнуляем время игры
        else:
            screen.blit(lose_label, (450, 425))  # Отображаем текст "PAUSED"
            pygame.display.flip()  # Обновление экрана
            continue  # Переход к следующей итерации, чтобы не отрисовывать остальную часть игры



    # Проверка окончания игры
    elif game_over:
        screen.blit(lose_label, (500, 300))
        screen.blit(restart_label, restart_label_rect)
        screen.blit(main_menu_label, main_menu_rect)
        if restart_label_rect.collidepoint(mouse) and pygame.mouse.get_pressed()[0]:
            reset_game()
        if main_menu_rect.collidepoint(mouse) and pygame.mouse.get_pressed()[0]:
            main_menu = True
            gameplay = False
            reset_game()

    # Обновление экрана
    pygame.display.flip()
    pygame.time.Clock().tick(60)

pygame.quit()