import pygame
import random
import sys
import os

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Screen dimensions
WIDTH, HEIGHT = 450, 640
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Motorcyclist Dodge")

# Load images
road_img = pygame.image.load(os.path.join(os.path.dirname(__file__), 'road.png')).convert()
road_img = pygame.transform.scale(road_img, (WIDTH, HEIGHT))
motorcycle_img = pygame.image.load(os.path.join(os.path.dirname(__file__), 'motorcycle.png')).convert_alpha()
car_img = pygame.image.load(os.path.join(os.path.dirname(__file__), 'car.png')).convert_alpha()

# Resize images
player_width, player_height = int(75 * 0.75), int(120 * 0.75)  # 56, 90
motorcycle_img = pygame.transform.scale(motorcycle_img, (player_width, player_height))
car_width, car_height = int(90 * 0.75), int(140 * 0.75)  # 67, 105
car_img = pygame.transform.scale(car_img, (car_width, car_height))
road_img = pygame.transform.scale(road_img, (WIDTH, HEIGHT))

# Road scrolling variables
road_y1 = 0
road_y2 = -HEIGHT
base_road_speed = 4
road_speed = base_road_speed

# Player (motorcyclist) settings
player_x = WIDTH // 2 - player_width // 2
player_y = HEIGHT - player_height - 10
player_speed = 5

# Car (obstacle) settings
base_car_speed = 3
car_speed = base_car_speed
cars = []

# Add font for score display
score = 0
font = pygame.font.SysFont(None, 36)
score_counter = 0  # Counter for slower score increment

# Load sounds
crash_sound = pygame.mixer.Sound('crash.wav')
pygame.mixer.music.load('background.wav')
pygame.mixer.music.play(-1)  # Loop forever

def spawn_car():
    x = random.randint(0, WIDTH - car_width)
    y = -car_height
    cars.append(pygame.Rect(x, y, car_width, car_height))

clock = pygame.time.Clock()
spawn_timer = 0

# Main game loop
running = True
while running:
    clock.tick(60)  # 60 FPS

    # Move and draw road
    road_y1 += road_speed
    road_y2 += road_speed
    if road_y1 >= HEIGHT:
        road_y1 = -HEIGHT
    if road_y2 >= HEIGHT:
        road_y2 = -HEIGHT
    screen.blit(road_img, (0, road_y1))
    screen.blit(road_img, (0, road_y2))

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Player movement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and player_x > 0:
        player_x -= player_speed
    if keys[pygame.K_RIGHT] and player_x < WIDTH - player_width:
        player_x += player_speed

    # Spawn cars
    spawn_timer += 1
    if spawn_timer > 40:
        spawn_car()
        spawn_timer = 0

    # Move cars
    for car in cars:
        car.y += car_speed

    # Remove cars that are off screen
    cars = [car for car in cars if car.y < HEIGHT]

    # Draw player
    player_rect = pygame.Rect(player_x, player_y, player_width, player_height)
    screen.blit(motorcycle_img, (player_x, player_y))

    # Make the player hitbox 80% smaller and centered
    hitbox_width = int(player_width * 0.8)
    hitbox_height = int(player_height * 0.8)
    hitbox_x = player_x + (player_width - hitbox_width) // 2
    hitbox_y = player_y + (player_height - hitbox_height) // 2
    player_hitbox = pygame.Rect(hitbox_x, hitbox_y, hitbox_width, hitbox_height)

    # Draw cars and create smaller hitboxes for them
    car_hitboxes = []
    for car in cars:
        screen.blit(car_img, (car.x, car.y))
        car_hitbox_width = int(car_width * 0.8)
        car_hitbox_height = int(car_height * 0.8)
        car_hitbox_x = car.x + (car_width - car_hitbox_width) // 2
        car_hitbox_y = car.y + (car_height - car_hitbox_height) // 2
        car_hitboxes.append(pygame.Rect(car_hitbox_x, car_hitbox_y, car_hitbox_width, car_hitbox_height))

    # Collision detection
    collision = False
    for car_hitbox in car_hitboxes:
        if player_hitbox.colliderect(car_hitbox):
            collision = True
            break

    # Update and display score
    if not collision:
        score_counter += 1
        if score_counter >= 8:
            score += 1  # Increase score every 8 frames
            score_counter = 0
            # Increase speed every 50 points
            if score % 50 == 0:
                road_speed += 1
                car_speed += 1
    score_surface = font.render(f"Score: {score}", True, (255, 0, 0))
    screen.blit(score_surface, (10, 10))

    if collision:
        crash_sound.play()
        pygame.mixer.music.stop()
        print("Game Over!")
        # Game Over screen
        game_over = True
        flash = True
        flash_timer = 0
        while game_over:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game_over = False
                    running = False
            # Redraw the last frame
            screen.blit(road_img, (0, road_y1))
            screen.blit(road_img, (0, road_y2))
            for car in cars:
                screen.blit(car_img, (car.x, car.y))
            screen.blit(motorcycle_img, (player_x, player_y))
            score_surface = font.render(f"Score: {score}", True, (255, 0, 0))
            screen.blit(score_surface, (10, 10))
            # Flashing GAME OVER text
            flash_timer += 1
            game_over_font = pygame.font.SysFont(None, 72)
            final_score_font = pygame.font.SysFont(None, 48)
            # Draw the score (always visible)
            final_score_surface = final_score_font.render(f"Score: {score}", True, (255, 0, 0))
            final_score_rect = final_score_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 60))
            screen.blit(final_score_surface, final_score_rect)
            # Draw GAME OVER (flashing)
            if (flash_timer // 30) % 2 == 0:
                game_over_surface = game_over_font.render("GAME OVER", True, (255, 0, 0))
                game_over_rect = game_over_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
                screen.blit(game_over_surface, game_over_rect)
            pygame.display.flip()
            pygame.time.delay(33)  # ~30 FPS for flashing
        break

    pygame.display.flip()

pygame.quit()
sys.exit() 